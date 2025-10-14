# 🤖 reddit-deliver

> Reddit post monitoring service with webhook delivery and multi-language translation support

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://github.com/techinpark/reddit-deliver/pkgs/container/reddit-deliver)
[![GitHub issues](https://img.shields.io/github/issues/techinpark/reddit-deliver)](https://github.com/techinpark/reddit-deliver/issues)

Stay updated with your favorite subreddits! **reddit-deliver** automatically monitors Reddit communities, translates posts to your preferred language, and delivers notifications via Discord or Slack webhooks.

---

## ✨ Features

- 🔍 **Smart Monitoring** - Automatically track new posts from your favorite subreddits
- 🌍 **Multi-Language Translation** - Translate posts using DeepL API (supports 30+ languages)
- 📢 **Webhook Notifications** - Deliver to Discord, Slack, or custom webhooks
- 🚫 **Duplicate Detection** - Never receive the same post twice
- 💾 **Persistent Storage** - SQLite database for configuration and history
- 🐳 **Docker Ready** - Deploy with a single command using Docker Compose
- 🔧 **CLI Interface** - Easy configuration through command-line tools
- ⚡ **Lightweight** - Minimal resource usage, perfect for self-hosting

---

## 📦 Installation

### Option 1: Docker Compose (Recommended)

The fastest way to get started!

```bash
# Clone the repository
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# Copy environment template
cp .env.example .env

# Edit .env with your API credentials
nano .env

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 2: Docker (Manual)

```bash
# Pull the latest image
docker pull ghcr.io/techinpark/reddit-deliver:latest

# Create .env file with your credentials
# Run the container
docker run -d \
  --name reddit-deliver \
  --env-file .env \
  -v reddit-deliver-data:/app/data \
  --restart unless-stopped \
  ghcr.io/techinpark/reddit-deliver:latest
```

### Option 3: Local Installation

```bash
# Clone the repository
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Initialize database
python src/storage/migrations/init_schema.py
```

---

## 🚀 Quick Start

### 1. Get API Credentials

#### Reddit API
1. Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - **name**: `reddit-deliver` (or any name)
   - **type**: Select "script"
   - **redirect uri**: `http://localhost:8080` (required but not used)
4. Click "Create app"
5. Copy the **client ID** (under your app name) and **secret**

#### DeepL API
1. Go to [https://www.deepl.com/pro-api](https://www.deepl.com/pro-api)
2. Sign up for a **free account** (500,000 characters/month)
3. Verify your email and add payment method (free tier won't be charged)
4. Go to your [Account Settings](https://www.deepl.com/account/summary)
5. Copy your **API Key**

#### Discord Webhook
1. Open Discord and go to your server
2. Go to **Server Settings** → **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Name it (e.g., "Reddit Bot"), select a channel
5. Click **Copy Webhook URL**

#### Slack Webhook (Optional)
1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Name your app and select workspace
4. Go to **Incoming Webhooks** → Enable it
5. Click **Add New Webhook to Workspace**
6. Select channel and copy the webhook URL

### 2. Configure Environment Variables

Create a `.env` file:

```bash
# Reddit API Configuration
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=reddit-deliver/0.1.0

# DeepL Translation API
DEEPL_API_KEY=your_deepl_api_key_here

# Discord Webhook (required)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url

# Optional: Slack Webhook
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your_webhook_url

# Monitoring Configuration
MONITOR_INTERVAL=300        # Check interval in seconds (default: 5 minutes)
SUBREDDITS=python,programming,docker,ClaudeAI  # Comma-separated list
POST_LIMIT=10               # Number of posts to fetch per subreddit
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

### 3. Initialize Configuration

```bash
# Initialize configuration
reddit-deliver config init

# Set translation language (examples: ko, ja, de, fr, es, it, pt, ru, zh)
reddit-deliver config set language ko

# Add subreddits to monitor
reddit-deliver subreddit add ClaudeAI
reddit-deliver subreddit add python
reddit-deliver subreddit add programming

# List monitored subreddits
reddit-deliver subreddit list

# Configure Discord webhook
reddit-deliver webhook set discord https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# Test webhook connection
reddit-deliver webhook test discord
```

### 4. Start Monitoring

```bash
# Run a single monitoring cycle (for testing)
reddit-deliver monitor start --once

# Run continuous monitoring (daemon mode - coming soon)
# reddit-deliver monitor start
```

---

## 🎯 Usage Examples

### Monitor Multiple Subreddits

```bash
# Add multiple subreddits
reddit-deliver subreddit add MachineLearning
reddit-deliver subreddit add kubernetes
reddit-deliver subreddit add golang

# View all monitored subreddits
reddit-deliver subreddit list
```

### Switch Translation Language

```bash
# Change to Japanese
reddit-deliver config set language ja

# Change to German
reddit-deliver config set language de

# Disable translation (original English)
reddit-deliver config set language en
```

### Multiple Webhooks

```bash
# Set Discord webhook
reddit-deliver webhook set discord https://discord.com/api/webhooks/...

# Set Slack webhook
reddit-deliver webhook set slack https://hooks.slack.com/services/...

# Test both
reddit-deliver webhook test discord
reddit-deliver webhook test slack
```

### Check Status

```bash
# View current configuration
reddit-deliver config show

# View recent posts
reddit-deliver history show --limit 10
```

---

## 🐳 Docker Deployment Guide

### Using Docker Compose

The recommended method for production deployments:

```bash
# Clone and navigate to repository
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# Create .env file with your credentials
cp .env.example .env
nano .env

# Start service in background
docker-compose up -d

# View logs
docker-compose logs -f reddit-deliver

# Stop service
docker-compose down

# Restart service
docker-compose restart

# Update to latest version
docker-compose pull
docker-compose up -d
```

### Docker Compose Configuration

The included `docker-compose.yml` provides:

- **Automatic restarts** - Service restarts on failure
- **Volume persistence** - Database survives container restarts
- **Health checks** - Automatic health monitoring
- **Environment isolation** - Credentials managed via .env file
- **Log management** - Structured logging to stdout

### Volume Management

Backup your database:

```bash
# Find volume location
docker volume inspect reddit-deliver-data

# Backup database
docker run --rm \
  -v reddit-deliver-data:/data \
  -v $(pwd):/backup \
  alpine cp /data/reddit-deliver.db /backup/reddit-deliver-backup.db
```

Restore database:

```bash
docker run --rm \
  -v reddit-deliver-data:/data \
  -v $(pwd):/backup \
  alpine cp /backup/reddit-deliver-backup.db /data/reddit-deliver.db
```

### Multi-Architecture Support

Reddit-deliver supports multiple architectures:

| Platform | Architecture | Status |
|----------|--------------|--------|
| Intel/AMD PC | linux/amd64 | ✅ Supported |
| Apple Silicon (M1/M2/M3) | linux/arm64 | ✅ Supported |
| Raspberry Pi 4/5 | linux/arm64 | ✅ Supported |
| AWS Graviton | linux/arm64 | ✅ Supported |

Docker automatically pulls the correct architecture for your platform.

### Scheduling with Cron

For periodic monitoring runs:

```bash
# Add to crontab
crontab -e

# Run every 5 minutes
*/5 * * * * cd /path/to/reddit-deliver && docker-compose run --rm reddit-deliver reddit-deliver monitor start --once

# Run every hour
0 * * * * cd /path/to/reddit-deliver && docker-compose run --rm reddit-deliver reddit-deliver monitor start --once
```

---

## 🔧 Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDDIT_CLIENT_ID` | ✅ Yes | - | Reddit API client ID |
| `REDDIT_CLIENT_SECRET` | ✅ Yes | - | Reddit API client secret |
| `REDDIT_USER_AGENT` | ✅ Yes | - | Reddit API user agent (format: appname/version) |
| `DEEPL_API_KEY` | ✅ Yes | - | DeepL translation API key |
| `DISCORD_WEBHOOK_URL` | ✅ Yes | - | Discord webhook URL for notifications |
| `SLACK_WEBHOOK_URL` | ❌ No | - | Slack webhook URL (optional) |
| `MONITOR_INTERVAL` | ❌ No | 300 | Monitoring interval in seconds |
| `SUBREDDITS` | ❌ No | python | Comma-separated list of subreddits |
| `POST_LIMIT` | ❌ No | 10 | Number of posts to fetch per check |
| `LOG_LEVEL` | ❌ No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Supported Languages (DeepL)

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English (no translation) | `ko` | Korean |
| `ja` | Japanese | `zh` | Chinese (Simplified) |
| `de` | German | `fr` | French |
| `es` | Spanish | `it` | Italian |
| `pt` | Portuguese | `ru` | Russian |
| `nl` | Dutch | `pl` | Polish |

[See full list](https://www.deepl.com/docs-api/translate-text/) of supported languages.

---

## 📁 Project Structure

```
reddit-deliver/
├── src/
│   ├── models/              # SQLAlchemy data models
│   │   ├── __init__.py
│   │   ├── base.py         # Base model class
│   │   ├── config.py       # Configuration model
│   │   ├── subreddit.py    # Subreddit model
│   │   ├── webhook.py      # Webhook model
│   │   └── post.py         # Post history model
│   ├── services/            # Business logic services
│   │   ├── reddit.py       # Reddit API client
│   │   ├── translator.py   # DeepL translation
│   │   ├── webhook.py      # Webhook delivery
│   │   └── monitor.py      # Monitoring orchestration
│   ├── storage/             # Database layer
│   │   ├── database.py     # Database connection
│   │   └── migrations/     # Schema migrations
│   ├── cli/                 # Command-line interface
│   │   ├── main.py         # CLI entry point
│   │   ├── config.py       # Config commands
│   │   ├── subreddit.py    # Subreddit commands
│   │   ├── webhook.py      # Webhook commands
│   │   └── monitor.py      # Monitor commands
│   └── lib/                 # Utilities
│       ├── logger.py       # Logging configuration
│       └── env.py          # Environment helpers
├── data/                    # Runtime data (gitignored)
│   └── reddit-deliver.db   # SQLite database
├── scripts/                 # Container scripts
│   ├── docker-entrypoint.sh   # Container initialization
│   └── health-check.sh        # Health check script
├── .github/
│   └── workflows/           # CI/CD pipelines
│       ├── docker-build.yml   # PR validation
│       └── docker-publish.yml # Release publishing
├── specs/                   # Feature specifications
│   ├── 001-reddit-webhook-monitor/
│   └── 002-docker-deployment/
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # Compose orchestration
├── .dockerignore            # Build optimization
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── setup.py                 # Package configuration
└── README.md                # This file
```

---

## 🛠️ Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Initialize database
python src/storage/migrations/init_schema.py

# Run tests (coming soon)
# pytest tests/

# Run linter
# flake8 src/
```

### Building Docker Image Locally

```bash
# Build single-architecture image
docker build -t reddit-deliver:local .

# Build multi-architecture image
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t reddit-deliver:multiarch \
  --load .

# Test the image
docker run --rm --env-file .env reddit-deliver:local reddit-deliver --version
```

### Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: Ensure all tests pass
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

#### Contribution Guidelines

- Follow existing code style (PEP 8 for Python)
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Keep pull requests focused and small

---

## 🗺️ Roadmap

### ✅ v0.1.0 - MVP (Current)
- [x] Reddit post monitoring
- [x] DeepL translation
- [x] Discord webhook delivery
- [x] Duplicate detection
- [x] CLI configuration
- [x] SQLite persistence

### 🚀 v0.2.0 - Docker Support (In Progress)
- [ ] Multi-stage Dockerfile
- [ ] Docker Compose orchestration
- [ ] GitHub Container Registry publishing
- [ ] Multi-architecture builds (AMD64 + ARM64)
- [ ] Container health checks

### 📋 v0.3.0 - Enhanced Features (Planned)
- [ ] Multiple subreddit management
- [ ] Slack webhook support
- [ ] Language switching per subreddit
- [ ] Advanced filtering (keywords, flairs, authors)
- [ ] Post content formatting options

### 🔮 v0.4.0 - Daemon Mode (Future)
- [ ] Background daemon process
- [ ] Systemd service integration
- [ ] Web dashboard for configuration
- [ ] Metrics and monitoring
- [ ] Rate limiting and backoff strategies

### 💡 Future Ideas
- [ ] Support for more webhooks (Telegram, Microsoft Teams)
- [ ] Reddit comment monitoring
- [ ] Custom post templates
- [ ] Webhook authentication
- [ ] Multi-user support
- [ ] Cloud deployment guides (AWS, GCP, Azure)

---

## ❓ FAQ

### How much does it cost to run?

reddit-deliver uses free tiers of all services:
- **Reddit API**: Free
- **DeepL API**: Free tier includes 500,000 characters/month
- **Discord/Slack**: Webhooks are free
- **Hosting**: Free if self-hosted, or ~$5/month for a small VPS

### How often does it check for new posts?

By default, every 5 minutes (`MONITOR_INTERVAL=300`). You can adjust this in your `.env` file or via cron scheduling.

### Will I get duplicate notifications?

No! reddit-deliver tracks all delivered posts in its database and skips duplicates.

### Can I monitor multiple subreddits?

Yes! Add multiple subreddits via CLI or list them in the `SUBREDDITS` environment variable.

### Does it support other languages?

Yes! DeepL supports 30+ languages. Set your preferred language with:
```bash
reddit-deliver config set language <language_code>
```

### What are the system requirements?

**Minimum**:
- Python 3.11+
- 100MB RAM
- 50MB disk space
- Internet connection

**Recommended**:
- Python 3.11+
- 256MB RAM
- 100MB disk space
- Stable internet connection

### Can I run multiple instances?

Yes, but each instance needs its own database file and configuration. Use separate directories or different container names.

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 techinpark

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **[PRAW](https://praw.readthedocs.io/)** - Python Reddit API Wrapper
- **[DeepL](https://www.deepl.com/)** - High-quality translation API
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit
- **[Click](https://click.palletsprojects.com/)** - CLI framework
- **[Docker](https://www.docker.com/)** - Containerization platform

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/techinpark/reddit-deliver/issues)
- **Discussions**: [GitHub Discussions](https://github.com/techinpark/reddit-deliver/discussions)
- **Email**: Create an issue for support

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=techinpark/reddit-deliver&type=Date)](https://star-history.com/#techinpark/reddit-deliver&Date)

---

<div align="center">

**Made with ❤️ by [techinpark](https://github.com/techinpark)**

[⬆ Back to Top](#-reddit-deliver)

</div>
