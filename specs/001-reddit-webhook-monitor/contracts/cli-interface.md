# CLI Interface Contract

**Feature**: 001-reddit-webhook-monitor
**Date**: 2025-10-15

## Overview

This document defines the command-line interface for the Reddit Monitoring and Webhook Delivery System. The CLI follows POSIX conventions and provides both human-readable and JSON output formats.

## Binary Name

`reddit-deliver`

## Global Options

Available for all commands:

```
--help, -h          Show help message and exit
--version, -v       Show version and exit
--json              Output in JSON format (machine-readable)
--config FILE       Path to config file (default: config/config.yaml)
--db FILE           Path to database file (default: data/reddit-deliver.db)
--verbose           Enable verbose logging
--quiet             Suppress all output except errors
```

## Commands

### 1. config

Manage configuration settings.

#### config set

Set a configuration value.

**Syntax**:
```bash
reddit-deliver config set <key> <value>
```

**Arguments**:
- `key`: Configuration key (language, poll_interval)
- `value`: Value to set

**Examples**:
```bash
# Set target language to Korean
reddit-deliver config set language ko

# Set poll interval to 10 minutes
reddit-deliver config set poll_interval 10
```

**Output** (human-readable):
```
✓ Configuration updated
  language: ko
```

**Output** (JSON with --json):
```json
{
  "status": "success",
  "key": "language",
  "value": "ko",
  "message": "Configuration updated"
}
```

**Exit Codes**:
- 0: Success
- 1: Invalid key
- 2: Invalid value

#### config get

Get a configuration value.

**Syntax**:
```bash
reddit-deliver config get <key>
```

**Arguments**:
- `key`: Configuration key (language, poll_interval, or 'all' for everything)

**Examples**:
```bash
# Get current language
reddit-deliver config get language

# Get all configuration
reddit-deliver config get all
```

**Output** (human-readable):
```
language: ko
```

**Output** (JSON with --json):
```json
{
  "language": "ko",
  "poll_interval": 5
}
```

**Exit Codes**:
- 0: Success
- 1: Key not found

#### config init

Initialize configuration with default values.

**Syntax**:
```bash
reddit-deliver config init
```

**Examples**:
```bash
reddit-deliver config init
```

**Output**:
```
✓ Configuration initialized with defaults
  language: en
  poll_interval: 5 minutes
```

**Exit Codes**:
- 0: Success
- 1: Config already exists (use --force to overwrite)

### 2. subreddit

Manage monitored subreddits.

#### subreddit add

Add a subreddit to monitor.

**Syntax**:
```bash
reddit-deliver subreddit add <subreddit_name> [--url URL]
```

**Arguments**:
- `subreddit_name`: Name of subreddit (e.g., 'ClaudeAI')
- `--url URL`: Full Reddit URL (optional, will be constructed from name if omitted)

**Examples**:
```bash
# Add by name
reddit-deliver subreddit add ClaudeAI

# Add by URL
reddit-deliver subreddit add ClaudeAI --url https://www.reddit.com/r/ClaudeAI/
```

**Output** (human-readable):
```
✓ Subreddit added
  Name: ClaudeAI
  URL: https://www.reddit.com/r/ClaudeAI/
  Status: Enabled
```

**Output** (JSON with --json):
```json
{
  "status": "success",
  "subreddit": {
    "id": 1,
    "name": "ClaudeAI",
    "url": "https://www.reddit.com/r/ClaudeAI/",
    "enabled": true,
    "created_at": "2025-10-15T10:00:00Z"
  }
}
```

**Exit Codes**:
- 0: Success
- 1: Invalid subreddit name
- 2: Subreddit already exists
- 3: Invalid URL format

#### subreddit list

List all monitored subreddits.

**Syntax**:
```bash
reddit-deliver subreddit list [--enabled-only]
```

**Options**:
- `--enabled-only`: Show only enabled subreddits

**Examples**:
```bash
# List all subreddits
reddit-deliver subreddit list

# List only enabled ones
reddit-deliver subreddit list --enabled-only
```

**Output** (human-readable):
```
Monitored Subreddits (3 total, 2 enabled):

  [✓] ClaudeAI
      https://www.reddit.com/r/ClaudeAI/
      Last checked: 2 minutes ago

  [✓] Python
      https://www.reddit.com/r/Python/
      Last checked: 5 minutes ago

  [✗] MachineLearning (disabled)
      https://www.reddit.com/r/MachineLearning/
      Last checked: Never
```

**Output** (JSON with --json):
```json
{
  "total": 3,
  "enabled": 2,
  "subreddits": [
    {
      "id": 1,
      "name": "ClaudeAI",
      "url": "https://www.reddit.com/r/ClaudeAI/",
      "enabled": true,
      "last_checked_at": "2025-10-15T10:28:00Z"
    },
    {
      "id": 2,
      "name": "Python",
      "url": "https://www.reddit.com/r/Python/",
      "enabled": true,
      "last_checked_at": "2025-10-15T10:25:00Z"
    }
  ]
}
```

**Exit Codes**:
- 0: Success

#### subreddit remove

Remove a subreddit from monitoring.

**Syntax**:
```bash
reddit-deliver subreddit remove <subreddit_name>
```

**Arguments**:
- `subreddit_name`: Name of subreddit to remove

**Examples**:
```bash
reddit-deliver subreddit remove MachineLearning
```

**Output**:
```
✓ Subreddit removed: MachineLearning
```

**Exit Codes**:
- 0: Success
- 1: Subreddit not found

#### subreddit enable/disable

Enable or disable monitoring for a subreddit.

**Syntax**:
```bash
reddit-deliver subreddit enable <subreddit_name>
reddit-deliver subreddit disable <subreddit_name>
```

**Examples**:
```bash
reddit-deliver subreddit disable MachineLearning
reddit-deliver subreddit enable MachineLearning
```

**Output**:
```
✓ Subreddit disabled: MachineLearning
```

**Exit Codes**:
- 0: Success
- 1: Subreddit not found

### 3. webhook

Manage webhook configuration.

#### webhook set

Configure webhook URL.

**Syntax**:
```bash
reddit-deliver webhook set <type> <url>
```

**Arguments**:
- `type`: Webhook type ('discord' or 'slack')
- `url`: Webhook URL

**Examples**:
```bash
reddit-deliver webhook set discord https://discord.com/api/webhooks/123/abc

reddit-deliver webhook set slack https://hooks.slack.com/services/T123/B456/xyz
```

**Output**:
```
✓ Discord webhook configured
  URL: https://discord.com/api/webhooks/***
  Status: Enabled
```

**Exit Codes**:
- 0: Success
- 1: Invalid webhook type
- 2: Invalid URL format
- 3: Webhook test failed (use --no-test to skip)

#### webhook test

Test webhook delivery.

**Syntax**:
```bash
reddit-deliver webhook test <type>
```

**Arguments**:
- `type`: Webhook type ('discord' or 'slack')

**Examples**:
```bash
reddit-deliver webhook test discord
```

**Output**:
```
Testing Discord webhook...
✓ Test message delivered successfully
  Response: 200 OK
```

**Exit Codes**:
- 0: Success
- 1: Webhook not configured
- 2: Delivery failed

#### webhook disable/enable

Disable or enable a webhook.

**Syntax**:
```bash
reddit-deliver webhook disable <type>
reddit-deliver webhook enable <type>
```

**Examples**:
```bash
reddit-deliver webhook disable discord
```

**Exit Codes**:
- 0: Success
- 1: Webhook not found

### 4. monitor

Control the monitoring service.

#### monitor start

Start monitoring in foreground or background.

**Syntax**:
```bash
reddit-deliver monitor start [--daemon]
```

**Options**:
- `--daemon`: Run as background daemon
- `--once`: Run one check cycle and exit (useful for cron)

**Examples**:
```bash
# Run in foreground (blocks until Ctrl+C)
reddit-deliver monitor start

# Run as daemon
reddit-deliver monitor start --daemon

# Run once and exit (for cron)
reddit-deliver monitor start --once
```

**Output** (foreground):
```
Starting Reddit monitoring service...
✓ Configuration loaded
✓ 3 subreddits enabled
✓ Discord webhook configured
✓ Language: Korean (ko)
✓ Poll interval: 5 minutes

[10:00:00] Checking ClaudeAI... 2 new posts
[10:00:05] Checking Python... 0 new posts
[10:00:10] Checking MachineLearning... 1 new post
[10:05:00] Checking ClaudeAI... 0 new posts
...

Press Ctrl+C to stop
```

**Output** (daemon):
```
✓ Monitor started as daemon
  PID: 12345
  Logs: ~/.reddit-deliver/monitor.log

Use 'reddit-deliver monitor stop' to stop
```

**Exit Codes**:
- 0: Success (or daemon started)
- 1: Configuration missing
- 2: No enabled subreddits
- 3: No webhook configured
- 4: Already running

#### monitor stop

Stop the monitoring daemon.

**Syntax**:
```bash
reddit-deliver monitor stop
```

**Examples**:
```bash
reddit-deliver monitor stop
```

**Output**:
```
✓ Monitor stopped
  PID: 12345 terminated
```

**Exit Codes**:
- 0: Success
- 1: Not running

#### monitor status

Show monitor status.

**Syntax**:
```bash
reddit-deliver monitor status
```

**Examples**:
```bash
reddit-deliver monitor status
```

**Output**:
```
Monitor Status: Running
  PID: 12345
  Uptime: 2 hours, 15 minutes
  Last check: 30 seconds ago
  Posts processed today: 47
  Webhooks delivered: 45 (2 failed)
```

**Output** (JSON with --json):
```json
{
  "status": "running",
  "pid": 12345,
  "uptime_seconds": 8100,
  "last_check": "2025-10-15T12:29:30Z",
  "stats": {
    "posts_processed_today": 47,
    "webhooks_delivered_today": 45,
    "webhooks_failed_today": 2
  }
}
```

**Exit Codes**:
- 0: Running
- 1: Not running

### 5. history

View processing history.

#### history posts

Show recently processed posts.

**Syntax**:
```bash
reddit-deliver history posts [--limit N] [--subreddit NAME] [--failed-only]
```

**Options**:
- `--limit N`: Show last N posts (default: 20)
- `--subreddit NAME`: Filter by subreddit
- `--failed-only`: Show only failed posts

**Examples**:
```bash
# Show last 20 posts
reddit-deliver history posts

# Show last 50 posts from ClaudeAI
reddit-deliver history posts --limit 50 --subreddit ClaudeAI

# Show failed posts
reddit-deliver history posts --failed-only
```

**Output**:
```
Recent Posts (20 most recent):

[✓] 2025-10-15 10:25  r/ClaudeAI
    "Claude Code is amazing!"
    Translated to: Korean
    Delivered to: Discord

[✓] 2025-10-15 10:20  r/Python
    "New Python 3.13 features"
    Translated to: Korean
    Delivered to: Discord

[✗] 2025-10-15 10:15  r/MachineLearning (FAILED)
    "Latest LLM benchmarks"
    Error: Translation API quota exceeded
    Retries: 3/3
```

**Exit Codes**:
- 0: Success

## Environment Variables

The CLI supports configuration via environment variables:

```bash
REDDIT_DELIVER_CONFIG=/path/to/config.yaml
REDDIT_DELIVER_DB=/path/to/database.db
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
DEEPL_API_KEY=your_deepl_api_key
```

## Error Handling

All commands use consistent exit codes:
- **0**: Success
- **1**: General error (invalid arguments, not found, etc.)
- **2**: Configuration error
- **3**: External API error (Reddit, DeepL, webhook)
- **4**: Database error

Error messages are written to stderr, regular output to stdout.

## Example Workflows

### Initial Setup

```bash
# Initialize config
reddit-deliver config init

# Set language to Korean
reddit-deliver config set language ko

# Configure Discord webhook
reddit-deliver webhook set discord https://discord.com/api/webhooks/123/abc

# Add subreddits
reddit-deliver subreddit add ClaudeAI
reddit-deliver subreddit add Python
reddit-deliver subreddit add MachineLearning

# Test webhook
reddit-deliver webhook test discord

# Start monitoring
reddit-deliver monitor start --daemon
```

### Daily Operations

```bash
# Check status
reddit-deliver monitor status

# View recent posts
reddit-deliver history posts --limit 50

# Add new subreddit
reddit-deliver subreddit add Rust

# Temporarily disable a subreddit
reddit-deliver subreddit disable MachineLearning
```

### Troubleshooting

```bash
# Check failed posts
reddit-deliver history posts --failed-only

# Test webhook delivery
reddit-deliver webhook test discord

# Run one check cycle with verbose output
reddit-deliver monitor start --once --verbose
```
