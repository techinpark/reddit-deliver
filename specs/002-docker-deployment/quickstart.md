# Docker Deployment Quick Start

**Feature**: 002-docker-deployment
**Date**: 2025-10-15

## Prerequisites

- Docker 20.10+ installed
- Docker Compose V2+ installed
- GitHub account (for pulling from GHCR)

## Option 1: Pull Pre-built Image from GHCR

**Fastest method** - Use pre-built multi-architecture images from GitHub Container Registry.

### Step 1: Create Configuration

Create a `.env` file with your API credentials:

```bash
# Reddit API Configuration
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=reddit-deliver/0.1.0

# DeepL Translation API
DEEPL_API_KEY=your_deepl_api_key_here

# Discord Webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url

# Monitoring Configuration
MONITOR_INTERVAL=300
SUBREDDITS=python,programming,docker
POST_LIMIT=10
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  reddit-deliver:
    image: ghcr.io/yourusername/reddit-deliver:latest
    container_name: reddit-deliver
    env_file: .env
    volumes:
      - reddit-deliver-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  reddit-deliver-data:
    driver: local
```

### Step 3: Start Service

```bash
docker-compose up -d
```

### Step 4: View Logs

```bash
docker-compose logs -f reddit-deliver
```

### Step 5: Stop Service

```bash
docker-compose down
```

---

## Option 2: Build Image Locally

**For development or customization** - Build the Docker image from source.

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/reddit-deliver.git
cd reddit-deliver
```

### Step 2: Create Configuration

Create `.env` file (same as Option 1 above).

### Step 3: Build Image

```bash
docker build -t reddit-deliver:local .
```

**Build time**: ~3-5 minutes (first build), ~1-2 minutes (cached)

### Step 4: Run Container

```bash
docker run -d \
  --name reddit-deliver \
  --env-file .env \
  -v reddit-deliver-data:/app/data \
  --restart unless-stopped \
  reddit-deliver:local
```

### Step 5: View Logs

```bash
docker logs -f reddit-deliver
```

### Step 6: Stop Container

```bash
docker stop reddit-deliver
docker rm reddit-deliver
```

---

## Option 3: Docker Compose with Local Build

**Combine local build with Compose orchestration.**

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/reddit-deliver.git
cd reddit-deliver
```

### Step 2: Create Configuration

Create `.env` file (same as Option 1 above).

### Step 3: Use Provided docker-compose.yml

The repository includes a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  reddit-deliver:
    build: .
    image: reddit-deliver:latest
    container_name: reddit-deliver
    env_file: .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Step 4: Build and Start

```bash
docker-compose up -d --build
```

---

## Common Commands

### Check Container Status

```bash
docker ps -a | grep reddit-deliver
```

### View Real-time Logs

```bash
docker-compose logs -f
```

### Restart Service

```bash
docker-compose restart
```

### Run One-time Monitoring Cycle

```bash
docker-compose run --rm reddit-deliver reddit-deliver monitor start --once
```

### Access Container Shell

```bash
docker-compose exec reddit-deliver bash
```

### View Database

```bash
docker-compose exec reddit-deliver sqlite3 /app/data/reddit-deliver.db
```

---

## Architecture Selection

Docker automatically pulls the correct image for your platform:

| Platform | Architecture | Image Tag |
|----------|--------------|-----------|
| Intel/AMD Mac/PC | linux/amd64 | Pulled automatically |
| Apple Silicon (M1/M2) | linux/arm64 | Pulled automatically |
| Raspberry Pi 4/5 | linux/arm64 | Pulled automatically |

**Verify architecture**:

```bash
docker inspect reddit-deliver:latest | grep Architecture
```

---

## Volume Management

### Backup Database

```bash
# Find volume location
docker volume inspect reddit-deliver-data

# Copy database out
docker run --rm \
  -v reddit-deliver-data:/data \
  -v $(pwd):/backup \
  alpine cp /data/reddit-deliver.db /backup/reddit-deliver-backup.db
```

### Restore Database

```bash
docker run --rm \
  -v reddit-deliver-data:/data \
  -v $(pwd):/backup \
  alpine cp /backup/reddit-deliver-backup.db /data/reddit-deliver.db
```

### Clean Up Volumes

```bash
docker-compose down -v  # WARNING: Deletes all data
```

---

## Troubleshooting

### Container Exits Immediately

**Check logs**:
```bash
docker-compose logs reddit-deliver
```

**Common causes**:
- Missing environment variables (REDDIT_CLIENT_ID, etc.)
- Invalid API credentials
- Database initialization failed

### Database Locked Error

**Solution**: Stop all containers accessing the database:
```bash
docker-compose down
docker-compose up -d
```

### Image Pull Fails

**Error**: `unauthorized: authentication required`

**Solution**: Login to GHCR:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin
```

Or make repository public for anonymous pulls.

### Out of Disk Space

**Check Docker disk usage**:
```bash
docker system df
```

**Clean up unused images**:
```bash
docker system prune -a
```

### Health Check Failing

**Check health status**:
```bash
docker inspect reddit-deliver | grep -A 10 Health
```

**Common causes**:
- Python import errors
- Missing dependencies
- Database corruption

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDDIT_CLIENT_ID` | ✅ Yes | - | Reddit API client ID |
| `REDDIT_CLIENT_SECRET` | ✅ Yes | - | Reddit API client secret |
| `REDDIT_USER_AGENT` | ✅ Yes | - | Reddit API user agent |
| `DEEPL_API_KEY` | ✅ Yes | - | DeepL translation API key |
| `DISCORD_WEBHOOK_URL` | ✅ Yes | - | Discord webhook URL |
| `MONITOR_INTERVAL` | ❌ No | 300 | Monitoring interval (seconds) |
| `SUBREDDITS` | ❌ No | python | Comma-separated subreddits |
| `POST_LIMIT` | ❌ No | 10 | Posts to fetch per subreddit |
| `LOG_LEVEL` | ❌ No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

---

## Production Deployment Tips

### 1. Use Specific Version Tags

Instead of `latest`, pin to specific versions:

```yaml
services:
  reddit-deliver:
    image: ghcr.io/yourusername/reddit-deliver:v0.1.0
```

### 2. Enable Automatic Restarts

```yaml
services:
  reddit-deliver:
    restart: unless-stopped
```

### 3. Configure Log Rotation

```yaml
services:
  reddit-deliver:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. Use Docker Secrets (Swarm/Kubernetes)

Instead of `.env` file:

```yaml
services:
  reddit-deliver:
    secrets:
      - reddit_client_id
      - reddit_client_secret

secrets:
  reddit_client_id:
    external: true
  reddit_client_secret:
    external: true
```

### 5. Monitor with Healthchecks.io

Add health check ping:

```yaml
services:
  reddit-deliver:
    environment:
      - HEALTHCHECK_URL=https://hc-ping.com/your-uuid
```

---

## Next Steps

- **Customize monitoring**: Edit `SUBREDDITS` and `POST_LIMIT` in `.env`
- **Set up monitoring dashboard**: Use Portainer, Grafana, or similar
- **Configure log aggregation**: Send logs to Loki, Elasticsearch, etc.
- **Add more webhooks**: Support Slack, Telegram, etc.
- **Schedule with cron**: Use host cron to trigger one-shot runs
- **Deploy to cloud**: AWS ECS, Google Cloud Run, Railway, Render

---

## Support

**Issues**: https://github.com/yourusername/reddit-deliver/issues
**Documentation**: https://github.com/yourusername/reddit-deliver/docs
**Discussions**: https://github.com/yourusername/reddit-deliver/discussions
