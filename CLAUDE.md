# reddit-deliver Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-15

## Active Technologies
- Python 3.11+ + PRAW (Reddit API), DeepL (translation), requests (webhooks), SQLAlchemy (ORM), APScheduler (background jobs) (001-reddit-webhook-monitor)
- Python 3.11+ (existing), Docker 20.10+, GitHub Actions + Docker, Docker Compose, GitHub Actions (docker/build-push-action, docker/setup-buildx-action) (002-docker-deployment)
- Docker volumes for SQLite database persistence (002-docker-deployment)

## Project Structure
```
src/
tests/
```

## Commands
cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style
Python 3.11+: Follow standard conventions

## Recent Changes
- 002-docker-deployment: Added Python 3.11+ (existing), Docker 20.10+, GitHub Actions + Docker, Docker Compose, GitHub Actions (docker/build-push-action, docker/setup-buildx-action)
- 001-reddit-webhook-monitor: Added Python 3.11+ + PRAW (Reddit API), DeepL (translation), requests (webhooks), SQLAlchemy (ORM), APScheduler (background jobs)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
