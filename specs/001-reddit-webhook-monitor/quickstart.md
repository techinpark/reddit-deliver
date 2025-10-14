# Quickstart Guide: Reddit Monitoring and Webhook Delivery

**Feature**: 001-reddit-webhook-monitor
**Date**: 2025-10-15

## Prerequisites

- Python 3.11 or higher
- Reddit API credentials (client ID and secret)
- DeepL API key (free tier available)
- Discord or Slack webhook URL

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Clone repository (if needed)
git clone <repository-url>
cd reddit-deliver

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get API Credentials

#### Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: reddit-deliver
   - **App type**: Select "script"
   - **Description**: Personal Reddit monitoring tool
   - **About URL**: (leave blank)
   - **Redirect URI**: http://localhost:8080 (required but not used)
4. Click "Create app"
5. Copy the **client ID** (under the app name) and **secret**

#### DeepL API Key

1. Go to https://www.deepl.com/pro-api
2. Sign up for free tier (500,000 characters/month)
3. Verify email and log in
4. Go to Account → API Keys
5. Copy your **Authentication Key**

#### Discord Webhook URL

1. Open Discord and go to your server
2. Right-click the channel → Edit Channel
3. Go to Integrations → Webhooks
4. Click "New Webhook"
5. Copy the **Webhook URL**

**OR for Slack:**

1. Go to https://api.slack.com/apps
2. Create a new app → "From scratch"
3. Choose workspace and give it a name
4. Go to "Incoming Webhooks" → Activate
5. Click "Add New Webhook to Workspace"
6. Select channel and authorize
7. Copy the **Webhook URL**

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
# .env file (DO NOT commit to git!)

# Reddit API credentials
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# DeepL API key
DEEPL_API_KEY=your_deepl_api_key_here
```

### Step 4: Initialize Configuration

```bash
# Create necessary directories
mkdir -p data config

# Initialize configuration
reddit-deliver config init

# Set your preferred language (e.g., Korean)
reddit-deliver config set language ko

# Configure webhook (choose Discord OR Slack)
reddit-deliver webhook set discord https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# OR for Slack:
# reddit-deliver webhook set slack https://hooks.slack.com/services/YOUR_WEBHOOK_URL
```

### Step 5: Add Subreddits to Monitor

```bash
# Add subreddits you want to monitor
reddit-deliver subreddit add ClaudeAI
reddit-deliver subreddit add Python
reddit-deliver subreddit add MachineLearning

# Verify they were added
reddit-deliver subreddit list
```

### Step 6: Test the Setup

```bash
# Test webhook delivery
reddit-deliver webhook test discord

# Run a single check cycle
reddit-deliver monitor start --once --verbose
```

If you see posts being detected and translated, you're all set!

### Step 7: Start Monitoring

```bash
# Option 1: Run in foreground (see live output)
reddit-deliver monitor start

# Option 2: Run as background daemon
reddit-deliver monitor start --daemon

# Check status
reddit-deliver monitor status
```

## Configuration File

The system stores configuration in `config/config.yaml`:

```yaml
# config/config.yaml
language: ko                    # Target translation language
poll_interval_minutes: 5        # How often to check subreddits

# Note: API keys and webhook URLs are stored in database for security
```

## Example Workflow

### Scenario: Monitor r/ClaudeAI for Korean Notifications

```bash
# 1. Initialize
reddit-deliver config init
reddit-deliver config set language ko

# 2. Configure webhook
reddit-deliver webhook set discord https://discord.com/api/webhooks/123456/abcdef

# 3. Add subreddit
reddit-deliver subreddit add ClaudeAI

# 4. Test
reddit-deliver webhook test discord
reddit-deliver monitor start --once

# 5. Start monitoring
reddit-deliver monitor start --daemon

# 6. Check results
reddit-deliver history posts --limit 10
```

When a new post appears in r/ClaudeAI, you'll receive a Discord message like:

```
**New post in r/ClaudeAI**

Claude Code는 놀랍습니다!

저는 방금 새로운 Claude Code CLI를 사용해봤는데 정말 놀라웠습니다...

Posted by u/reddit_user_123
[View original post →]
```

## Common Tasks

### Change Translation Language

```bash
# Switch to Japanese
reddit-deliver config set language ja

# The next posts will be translated to Japanese
```

### Add More Subreddits

```bash
reddit-deliver subreddit add Rust
reddit-deliver subreddit add WebDev
reddit-deliver subreddit list
```

### Temporarily Pause a Subreddit

```bash
# Disable monitoring (keeps history)
reddit-deliver subreddit disable MachineLearning

# Re-enable later
reddit-deliver subreddit enable MachineLearning
```

### View Recent Activity

```bash
# Last 20 posts
reddit-deliver history posts

# Last 50 posts from specific subreddit
reddit-deliver history posts --limit 50 --subreddit ClaudeAI

# Show only failed deliveries
reddit-deliver history posts --failed-only
```

### Stop Monitoring

```bash
# If running as daemon
reddit-deliver monitor stop

# If running in foreground, press Ctrl+C
```

## Troubleshooting

### "No posts detected"

Check that:
- Reddit credentials are correct in `.env`
- Subreddit names are spelled correctly
- The subreddit has recent posts (created in last 24 hours)

Run with verbose logging:
```bash
reddit-deliver monitor start --once --verbose
```

### "Translation failed"

Check that:
- DeepL API key is correct in `.env`
- You haven't exceeded free tier quota (500k chars/month)
- Source language is supported by DeepL

### "Webhook delivery failed"

Check that:
- Webhook URL is correct (not expired)
- Webhook type matches URL (discord vs slack)
- Network connection is working

Test webhook:
```bash
reddit-deliver webhook test discord --verbose
```

### "Database locked" errors

Only one instance can run at a time. Check if monitor is already running:
```bash
reddit-deliver monitor status
```

If stuck, stop the daemon:
```bash
reddit-deliver monitor stop
```

## Supported Languages

DeepL supports translation to:

- **Korean** (ko)
- **Japanese** (ja)
- **Chinese Simplified** (zh)
- **Spanish** (es)
- **French** (fr)
- **German** (de)
- **Italian** (it)
- **Portuguese** (pt)
- And 20+ more languages

See full list: https://www.deepl.com/docs-api/translating-text/

## Rate Limits

**Reddit API**:
- 60 requests per minute (with OAuth)
- System respects this automatically

**DeepL Free Tier**:
- 500,000 characters per month
- Estimate: ~50-100 posts per day

**Webhooks**:
- Discord: 30 messages per minute per webhook
- Slack: 1 message per second

The system handles these limits automatically with retry logic.

## File Structure

After setup, your project will look like:

```
reddit-deliver/
├── .env                        # API credentials (git-ignored)
├── config/
│   └── config.yaml             # User configuration
├── data/
│   └── reddit-deliver.db       # SQLite database
├── src/                        # Source code
├── tests/                      # Tests
└── requirements.txt            # Dependencies
```

## Next Steps

After completing this quickstart:

1. **Fine-tune polling interval**: Adjust based on subreddit activity
   ```bash
   reddit-deliver config set poll_interval 10  # Check every 10 minutes
   ```

2. **Set up as system service**: For always-on monitoring, configure systemd (Linux) or launchd (macOS)

3. **Monitor logs**: Check `~/.reddit-deliver/monitor.log` for detailed activity

4. **Customize notifications**: Edit webhook formatting in source code (advanced)

## Getting Help

- Run `reddit-deliver --help` for command reference
- Run `reddit-deliver <command> --help` for command-specific help
- Check logs: `~/.reddit-deliver/monitor.log`
- View source documentation: `docs/` directory

## Security Notes

- **Never commit `.env` file** to version control
- Webhook URLs contain secrets - treat them like passwords
- Reddit API credentials are sensitive - don't share them
- Database file contains webhook URLs - keep secure

Add to `.gitignore`:
```
.env
data/reddit-deliver.db
*.log
```

## Performance Tips

For monitoring many subreddits (10+):

1. Increase poll interval to reduce API calls:
   ```bash
   reddit-deliver config set poll_interval 10
   ```

2. Monitor translation quota:
   ```bash
   reddit-deliver history posts --json | jq '.stats.chars_translated_today'
   ```

3. Use `--once` mode with cron instead of daemon for lower memory usage:
   ```cron
   */5 * * * * cd /path/to/reddit-deliver && ./venv/bin/reddit-deliver monitor start --once
   ```

## Upgrading

When new versions are released:

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations (if any)
alembic upgrade head

# Restart monitoring
reddit-deliver monitor stop
reddit-deliver monitor start --daemon
```

Happy monitoring! 🎉
