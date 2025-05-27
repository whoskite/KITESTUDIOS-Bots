# Discord RSS Bot with AI Processing

A Discord bot that automatically monitors multiple RSS feeds and uses Claude 3.5 Sonnet to create engaging, educational Discord messages with Feynman technique explanations and actionable tips.

## Features

- 🤖 **Advanced AI Processing**: Uses Claude 3.5 Sonnet to transform RSS content into structured, educational Discord messages
- 📚 **Feynman Technique**: Explains complex concepts in simple, understandable language
- ⚡ **Actionable Tips**: Extracts practical, implementable advice from articles
- 📝 **Smart Summaries**: Provides concise TL;DR summaries for quick consumption
- 📡 **Multi-Feed Support**: Monitor multiple RSS feeds simultaneously
- 🚫 **Spam Prevention**: Limits posts per feed to ensure balanced content
- 🔄 **Duplicate Prevention**: Tracks processed posts to avoid repeating content
- 🔍 **Content Validation**: AI-powered filtering to skip problematic articles
- ⚡ **Real-time Posting**: Instantly posts new content to your Discord channel
- 🛡️ **Error Handling**: Robust error handling with comprehensive logging
- ⚙️ **Configurable**: Easy configuration via environment variables

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables

Copy `config.env.example` to `config.env` and fill in your credentials:

```bash
cp config.env.example config.env
```

Edit `config.env` with your actual values:

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
RSS_FEED_URL=https://every.to/feeds/fe85842ddccec3a4c0f4.xml, https://fs.blog/feed/, https://dailystoic.com/feed/
CHECK_INTERVAL_MINUTES=60
MAX_POSTS_PER_FEED=2
ENABLE_CONTENT_VALIDATION=true
```

### 3. Get Required Tokens

#### Discord Bot Token:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create a bot and copy the token
5. Invite bot to your server with "Send Messages" permission

#### Discord Channel ID:
1. Enable Developer Mode in Discord settings
2. Right-click your target channel
3. Select "Copy ID"

#### Anthropic API Key:
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create a new API key
3. Copy the key

### 4. Run the Bot

```bash
python discord_rss_bot.py
```

## How It Works

1. **Multi-Feed Monitoring**: Bot checks all configured RSS feeds every hour (configurable)
2. **Loop Prevention**: Tracks last check time per feed to prevent reprocessing if bot restarts
3. **New Post Detection**: Compares against previously processed posts across all feeds
4. **Content Validation**: AI analyzes articles to skip problematic content (future dates, broken links, etc.)
5. **Spam Prevention**: Limits posts per feed to ensure balanced content distribution
6. **Advanced AI Processing**: Uses Claude 3.5 Sonnet to create structured, educational content:
   - 🎯 **Punchy Headlines**: Benefit-focused titles under 60 characters
   - 🧠 **Simple Explanations**: Feynman technique for complex concepts
   - ⚡ **Quick Wins**: 2-3 actionable tips with action verbs
   - 📝 **TL;DR**: One-sentence key insight summary
7. **Discord Posting**: Sends formatted messages to your channel with 2-second delays
8. **Tracking**: Saves processed post IDs and check times to avoid duplicates

## Configuration

### Environment Variables

- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `DISCORD_CHANNEL_ID`: Channel where posts will be sent
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude 3.5 Sonnet
- `RSS_FEED_URL`: Comma-separated list of RSS feed URLs to monitor
- `CHECK_INTERVAL_MINUTES`: How often to check for new posts (default: 60)
- `MAX_POSTS_PER_FEED`: Maximum posts per feed per check cycle (default: 2)
- `ENABLE_CONTENT_VALIDATION`: Enable AI validation to skip problematic articles (default: true)

### Multi-Feed Configuration

Add multiple RSS feeds separated by commas:

```
RSS_FEED_URL=https://every.to/feeds/fe85842ddccec3a4c0f4.xml, https://fs.blog/feed/, https://dailystoic.com/feed/, https://news.ycombinator.com/rss, https://www.smashingmagazine.com/feed/
```

### Spam Prevention

Control content volume with `MAX_POSTS_PER_FEED`:
- `1`: Ultra-conservative (max 1 post per feed per check)
- `2`: Balanced (recommended - max 2 posts per feed per check)
- `3`: More content (max 3 posts per feed per check)

### Files Created

- `processed_posts.json`: Tracks processed posts and last check times per feed to prevent duplicates and loops
- Console logs: Bot activity and status updates

**processed_posts.json structure:**
```json
{
  "posts": {
    "article_id_1": {
      "title": "Article Title",
      "link": "https://example.com/article",
      "processed_at": "2024-01-15T10:30:00"
    }
  },
  "last_check_times": {
    "https://feed1.com/rss": "2024-01-15T10:30:00",
    "https://feed2.com/rss": "2024-01-15T10:32:00"
  }
}
```

### Content Validation

Control content quality with `ENABLE_CONTENT_VALIDATION`:
- `true`: AI validates articles before processing (recommended)
- `false`: Process all articles without validation

**Validation checks for:**
- Future dates in articles
- Broken or inaccessible links
- Empty or malformed content
- AI processing errors

## Message Format

The bot creates structured Discord messages with:

```
🎯 **Punchy Headline**

🧠 **SIMPLE EXPLANATION**: Feynman-style explanation of the main concept

⚡ **QUICK WINS**: 
• Action-oriented tip 1
• Action-oriented tip 2
• Action-oriented tip 3

📝 **TL;DR**: One-sentence summary of key insight

🔗 [Original Article Link]
```

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if bot token is valid and bot has permissions
2. **No posts appearing**: Verify channel ID and bot permissions in that channel
3. **AI errors**: Check Anthropic API key and account credits
4. **RSS parsing errors**: Verify RSS feed URLs are accessible
5. **Too many posts**: Reduce `MAX_POSTS_PER_FEED` value
6. **Duplicate posts**: Check if `processed_posts.json` exists and is readable
7. **Articles being skipped**: Check validation logs or disable `ENABLE_CONTENT_VALIDATION`

### Logs

The bot logs all activities to console. Look for:
- `Starting bot with X RSS feeds`
- `Processing feed: [URL]`
- `Skipping [URL] - already checked X.X minutes ago`
- `Found X new posts for [URL]`
- `Skipping article 'Title' - SKIP_FUTURE_DATE` (or other validation reasons)
- `Skipping article 'Title' - AI returned error message`
- `Limited to X posts for [URL] to prevent spam`
- `Message sent to Discord successfully`

## Customization

### AI Prompt Modification

Edit the `process_with_ai` method in `discord_rss_bot.py` to customize content processing:

```python
prompt = f"""
Transform this RSS article into an engaging Discord post that provides real value. Structure it as follows:

🎯 **HEADLINE**: Create a punchy, benefit-focused headline (max 60 chars)

🧠 **SIMPLE EXPLANATION**: Use the Feynman technique - explain the main concept like you're teaching a smart 12-year-old.

⚡ **QUICK WINS**: List 2-3 actionable, pragmatic tips that readers can implement immediately.

📝 **TL;DR**: One sentence summary of the key insight or main benefit.
"""
```

### Check Interval

Modify `CHECK_INTERVAL_MINUTES` in your `config.env` file:
- `30`: Check every 30 minutes (more frequent)
- `60`: Check every hour (recommended)
- `120`: Check every 2 hours (less frequent)

## Running as a Service

For production use, consider running the bot as a service:

### Using systemd (Linux)

Create `/etc/systemd/system/discord-rss-bot.service`:

```ini
[Unit]
Description=Discord RSS Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/your/bot
ExecStart=/usr/bin/python3 discord_rss_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable discord-rss-bot
sudo systemctl start discord-rss-bot
```

## Example RSS Feeds

High-quality feeds that work well with this bot:

**Business & Productivity:**
- Every.to: `https://every.to/feeds/fe85842ddccec3a4c0f4.xml`
- Farnam Street: `https://fs.blog/feed/`

**Philosophy & Wisdom:**
- Daily Stoic: `https://dailystoic.com/feed/`
- The Marginalian: `https://www.themarginalian.org/feed/`

**Technology:**
- Hacker News: `https://news.ycombinator.com/rss`
- Smashing Magazine: `https://www.smashingmagazine.com/feed/`

**AI & Innovation:**
- The Verge AI: `https://www.theverge.com/artificial-intelligence/rss/index.xml`
- Wait But Why: `https://waitbutwhy.com/feed`

## License

This project is open source and available under the MIT License.