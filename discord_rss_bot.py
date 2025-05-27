import asyncio
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

import discord
from discord.ext import tasks
import atoma
import requests
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordRSSBot:
    def __init__(self):
        self.bot = discord.Client(intents=discord.Intents.default())
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        
        # Parse multiple RSS URLs
        rss_urls_str = os.getenv('RSS_FEED_URL', '')
        self.rss_urls = [url.strip() for url in rss_urls_str.split(',') if url.strip()]
        
        self.check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', 60))
        self.processed_file = 'processed_posts.json'
        
        # Limit posts per feed per check to prevent spam
        self.max_posts_per_feed = int(os.getenv('MAX_POSTS_PER_FEED', 2))
        
        # Initialize Anthropic
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Load processed posts
        self.processed_posts = self.load_processed_posts()
        
        # Set up bot events
        self.setup_bot_events()
    
    def load_processed_posts(self) -> Dict:
        """Load previously processed posts from JSON file"""
        try:
            if os.path.exists(self.processed_file):
                with open(self.processed_file, 'r') as f:
                    data = json.load(f)
                    # Ensure we have the new structure with last_check_times
                    if 'posts' not in data:
                        # Migrate old format
                        data = {
                            'posts': data,
                            'last_check_times': {}
                        }
                    return data
        except Exception as e:
            logger.error(f"Error loading processed posts: {e}")
        return {'posts': {}, 'last_check_times': {}}
    
    def save_processed_posts(self):
        """Save processed posts to JSON file"""
        try:
            with open(self.processed_file, 'w') as f:
                json.dump(self.processed_posts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving processed posts: {e}")
    
    def setup_bot_events(self):
        """Set up Discord bot event handlers"""
        @self.bot.event
        async def on_ready():
            logger.info(f'{self.bot.user} has connected to Discord!')
            self.rss_checker.start()
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            logger.error(f'Discord error in {event}: {args}')
    
    async def fetch_rss_feed(self, url: str):
        """Fetch and parse RSS feed"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            feed = atoma.parse_rss_bytes(response.content)
            return feed
        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return None
    
    async def process_with_ai(self, title: str, content: str, link: str) -> str:
        """Process RSS content with AI to make it Discord-friendly"""
        try:
            prompt = f"""
            Transform this RSS article into an engaging Discord post that provides real value. Structure it as follows:

            🎯 **HEADLINE**: Create a punchy, benefit-focused headline (max 60 chars)
            
            🧠 **SIMPLE EXPLANATION**: Use the Feynman technique - explain the main concept like you're teaching a smart 12-year-old. Make complex ideas crystal clear.
            
            ⚡ **QUICK WINS**: List 2-3 actionable, pragmatic tips that readers can implement immediately. Start each with an action verb.
            
            📝 **TL;DR**: One sentence summary of the key insight or main benefit.
            
            Requirements:
            - Keep total message under 1500 characters
            - Use emojis strategically (not excessively)
            - Make it conversational and engaging
            - Focus on practical value, not theory
            - End with the link
            
            Article Title: {title}
            Article Content: {content[:1500]}
            Link: {link}
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        
        except Exception as e:
            logger.error(f"Error processing with AI: {e}")
            # Fallback to basic formatting
            return f"🔥 **{title}**\n\n{content[:500]}...\n\n🔗 Read more: {link}"
    
    async def send_to_discord(self, message: str):
        """Send message to Discord channel"""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                # Split long messages if needed
                if len(message) > 2000:
                    parts = [message[i:i+2000] for i in range(0, len(message), 2000)]
                    for part in parts:
                        await channel.send(part)
                else:
                    await channel.send(message)
                logger.info("Message sent to Discord successfully")
            else:
                logger.error(f"Channel {self.channel_id} not found")
        except Exception as e:
            logger.error(f"Error sending to Discord: {e}")
    
    @tasks.loop(minutes=60)  # Will be overridden by check_interval
    async def rss_checker(self):
        """Main RSS checking loop"""
        try:
            logger.info("Checking RSS feeds for new posts...")
            current_time = datetime.now()
            
            for url in self.rss_urls:
                # Check if this feed was already processed recently
                last_check = self.processed_posts['last_check_times'].get(url)
                if last_check:
                    last_check_time = datetime.fromisoformat(last_check)
                    time_since_check = (current_time - last_check_time).total_seconds() / 60
                    
                    if time_since_check < self.check_interval:
                        logger.info(f"Skipping {url} - already checked {time_since_check:.1f} minutes ago")
                        continue
                
                logger.info(f"Processing feed: {url}")
                feed = await self.fetch_rss_feed(url)
                
                if not feed or not feed.items:
                    logger.warning(f"No entries found in RSS feed for {url}")
                    # Still update last check time even if no entries
                    self.processed_posts['last_check_times'][url] = current_time.isoformat()
                    continue
                
                new_posts = []
                for item in feed.items:
                    post_id = getattr(item, 'guid', item.link)
                    
                    if post_id not in self.processed_posts['posts']:
                        new_posts.append(item)
                        self.processed_posts['posts'][post_id] = {
                            'title': item.title,
                            'link': item.link,
                            'processed_at': datetime.now().isoformat()
                        }
                
                # Limit to 3 most recent posts if this is the first run
                if len(self.processed_posts['posts']) <= len(new_posts):
                    new_posts = new_posts[:3]
                    logger.info(f"First run detected - limiting to {len(new_posts)} most recent posts for {url}")
                else:
                    # Limit posts per feed to prevent spam
                    new_posts = new_posts[:self.max_posts_per_feed]
                    if len(new_posts) == self.max_posts_per_feed:
                        logger.info(f"Limited to {self.max_posts_per_feed} posts for {url} to prevent spam")
                
                if new_posts:
                    logger.info(f"Found {len(new_posts)} new posts for {url}")
                    for item in new_posts:
                        # Get content
                        content = ""
                        if hasattr(item, 'description') and item.description:
                            content = item.description
                        elif hasattr(item, 'summary') and item.summary:
                            content = item.summary
                        
                        # Process with AI
                        ai_message = await self.process_with_ai(
                            item.title, 
                            content, 
                            item.link
                        )
                        
                        # Send to Discord
                        await self.send_to_discord(ai_message)
                        
                        # Small delay between posts
                        await asyncio.sleep(2)
                    
                    # Save processed posts
                    self.save_processed_posts()
                else:
                    logger.info("No new posts found for " + url)
                
                # Mark this feed as checked
                self.processed_posts['last_check_times'][url] = current_time.isoformat()
                self.save_processed_posts()
                
        except Exception as e:
            logger.error(f"Error in RSS checker: {e}")
    
    @rss_checker.before_loop
    async def before_rss_checker(self):
        """Wait for bot to be ready before starting RSS checker"""
        await self.bot.wait_until_ready()
        # Override the loop interval
        self.rss_checker.change_interval(minutes=self.check_interval)
    
    def run(self):
        """Start the bot"""
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("DISCORD_BOT_TOKEN not found in environment variables")
            return
        
        logger.info(f"Starting bot with {len(self.rss_urls)} RSS feeds")
        logger.info(f"Checking every {self.check_interval} minutes")
        self.bot.run(token)

if __name__ == "__main__":
    bot = DiscordRSSBot()
    bot.run() 