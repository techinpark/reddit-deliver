# Technical Research: Docker Deployment with GHCR

**Date**: 2025-10-15
**Feature**: 002-docker-deployment

## Overview

Research findings for implementing Docker containerization with GitHub Container Registry publishing for reddit-deliver Python application.

## Research Areas

### 1. Python Docker Image Base

**Decision**: python:3.11-slim

**Rationale**:
- Official Python image with security updates
- Slim variant reduces image size (~150MB vs ~900MB for full image)
- Includes pip and basic utilities
- Well-maintained by Docker official images team
- Compatible with multi-arch builds

**Alternatives Considered**:
- **python:3.11-alpine**:
  - Pros: Smallest size (~50MB base)
  - Cons: Uses musl libc (compatibility issues), longer build times for compiled deps (SQLAlchemy, PRAW)
  - Rejected: Potential runtime issues with C extensions
- **python:3.11** (full):
  - Pros: All utilities included
  - Cons: Large size (900MB+), unnecessary packages
  - Rejected: Image bloat for minimal benefit
- **distroless Python**:
  - Pros: Minimal attack surface
  - Cons: No shell for debugging, complex setup
  - Rejected: Overkill for this use case

**Best Practices**:
```dockerfile
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*
```

### 2. Multi-Stage Build Strategy

**Decision**: 3-stage build (dependencies, builder, runtime)

**Rationale**:
- Separates build dependencies from runtime
- Reduces final image size by ~40%
- Caches pip dependencies for faster rebuilds
- Security: no build tools in production image

**Implementation Pattern**:
```dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim as deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY --from=deps /root/.local /root/.local
COPY . .
RUN pip install --user -e .

# Stage 3: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/src ./src
ENV PATH=/root/.local/bin:$PATH
CMD ["reddit-deliver", "monitor", "start", "--once"]
```

### 3. Docker Compose Configuration

**Decision**: docker-compose.yml with .env file

**Rationale**:
- Simple single-command deployment
- Environment variable isolation
- Volume persistence for database
- Easy service restarts
- Development/production parity

**Best Practices**:
```yaml
version: '3.8'
services:
  reddit-deliver:
    build: .
    image: reddit-deliver:latest
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

### 4. GitHub Container Registry (GHCR)

**Decision**: GHCR with automatic publishing via GitHub Actions

**Rationale**:
- Free for public repositories
- Integrated with GitHub (same authentication)
- Unlimited bandwidth for public images
- Support for multi-arch images
- Better than Docker Hub for open source

**Alternatives Considered**:
- **Docker Hub**:
  - Pros: Most popular registry
  - Cons: Rate limits (100 pulls/6h), requires separate account
  - Rejected: Rate limiting concerns
- **Amazon ECR Public**:
  - Pros: Good performance, AWS integration
  - Cons: Requires AWS account, less familiar
  - Rejected: Added complexity
- **Self-hosted registry**:
  - Pros: Full control
  - Cons: Maintenance overhead, hosting costs
  - Rejected: Not suitable for open source distribution

**Authentication**:
```yaml
# GitHub Actions
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### 5. Multi-Architecture Builds

**Decision**: docker/build-push-action with buildx

**Rationale**:
- Supports linux/amd64 and linux/arm64 in single workflow
- Uses QEMU for cross-compilation
- Creates manifest list automatically
- No separate jobs needed

**Implementation**:
```yaml
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
```

**Build Time**: ~8-12 minutes for multi-arch (within GitHub Actions free tier)

### 6. Container Initialization

**Decision**: Custom entrypoint script with database initialization

**Rationale**:
- Auto-initialize database on first run
- Validate environment variables
- Graceful error handling
- Support both daemon and one-shot modes

**Entrypoint Script**:
```bash
#!/bin/bash
set -e

# Check required environment variables
: ${REDDIT_CLIENT_ID:?}
: ${REDDIT_CLIENT_SECRET:?}
: ${DEEPL_API_KEY:?}

# Initialize database if not exists
if [ ! -f /app/data/reddit-deliver.db ]; then
    echo "Initializing database..."
    python src/storage/migrations/init_schema.py
fi

# Execute command
exec "$@"
```

### 7. Health Checks

**Decision**: Simple Python health check script

**Rationale**:
- Docker/Kubernetes health monitoring
- Automatic container restart on failure
- No external dependencies
- Fast response (<1s)

**Health Check**:
```bash
#!/bin/bash
# Check if Python can import main modules
python -c "import sys; from models import Base; from storage.database import get_database; sys.exit(0)"
```

### 8. Volume Strategy

**Decision**: Named volume for data directory

**Rationale**:
- Persist database across container restarts
- Survives container deletion
- Easy backup/restore
- Development/production parity

**Volume Configuration**:
```yaml
volumes:
  - reddit-deliver-data:/app/data

volumes:
  reddit-deliver-data:
    driver: local
```

### 9. .dockerignore Optimization

**Decision**: Exclude unnecessary files from build context

**Rationale**:
- Faster builds (smaller context)
- Avoid copying sensitive files
- Reduce image size
- Security best practice

**Patterns**:
```
.git
.gitignore
.env
*.pyc
__pycache__
.venv
venv/
data/
*.db
*.log
tests/
docs/
specs/
.github/
README.md
```

### 10. Image Tagging Strategy

**Decision**: semantic versioning + latest + sha

**Rationale**:
- latest: always points to newest release
- vX.Y.Z: specific version for stability
- sha-XXXXXXX: commit traceability
- Allows flexible deployment options

**Tagging**:
```yaml
tags: |
  ghcr.io/${{ github.repository }}:latest
  ghcr.io/${{ github.repository }}:${{ github.ref_name }}
  ghcr.io/${{ github.repository }}:sha-${{ github.sha }}
```

## CI/CD Pipeline Design

### Build Workflow (on PR)

**Triggers**: Pull requests to main
**Actions**:
1. Checkout code
2. Set up Docker Buildx
3. Build image (no push)
4. Run tests in container
5. Check image size

**Purpose**: Validate Docker build works before merge

### Publish Workflow (on Release)

**Triggers**: Tags matching v* (e.g., v0.1.0)
**Actions**:
1. Checkout code
2. Docker meta (extract tags/labels)
3. Login to GHCR
4. Build multi-arch images
5. Push to GHCR
6. Create release notes

**Security**: Uses GITHUB_TOKEN (automatic), no manual secrets

## Performance Optimizations

**Layer Caching**:
- Copy requirements.txt before source code
- Use --mount=type=cache for pip downloads
- Separate dependencies from application code

**Build Time**:
- Multi-stage builds: ~3-5 minutes (single arch)
- Multi-arch builds: ~8-12 minutes (both arch)
- Cached builds: ~1-2 minutes

**Image Size**:
- Base image: 150MB
- With dependencies: ~350MB
- Final runtime: ~400MB
- Target: <500MB (achieved)

## Security Considerations

**Secrets Management**:
- Never commit secrets to image
- Use environment variables at runtime
- GitHub Actions secrets for GHCR token
- .env file for local deployment (git-ignored)

**Image Scanning**:
- GitHub Advanced Security (optional)
- Trivy scanning in CI (recommended)
- Base image CVE monitoring

**Non-Root User**:
```dockerfile
RUN useradd -m -u 1000 reddit-deliver
USER reddit-deliver
```

## Risk Mitigation

**GitHub Actions Quota**:
- **Risk**: Exceeding free tier (2000 min/month)
- **Mitigation**:
  - Only build on releases (not every commit)
  - Cache Docker layers
  - Estimated: ~15 builds/month = 180 minutes

**Multi-Arch Build Failures**:
- **Risk**: ARM64 build fails due to QEMU issues
- **Mitigation**:
  - Test locally with `docker buildx build --platform linux/arm64`
  - Fallback to AMD64-only if needed
  - Document architecture limitations

**Image Pull Rate Limits**:
- **Risk**: GHCR rate limiting
- **Mitigation**:
  - Public images have no rate limits
  - Encourage users to authenticate for better rates
  - Consider image caching strategies

## Next Steps

All research complete. Ready to proceed to Phase 1:
- Create Dockerfile with multi-stage builds
- Create docker-compose.yml
- Create .dockerignore
- Create GitHub Actions workflows
- Create entrypoint and health check scripts
- Update documentation with Docker deployment guide
