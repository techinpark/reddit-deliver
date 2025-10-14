# Tasks: Docker Deployment with GitHub Container Registry

**Input**: Design documents from `/specs/002-docker-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, contracts/github-actions-workflows.md, quickstart.md

**Tests**: Tests are OPTIONAL and not explicitly requested in the feature specification. This implementation focuses on infrastructure and deployment artifacts.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: Repository root for Docker files, `.github/workflows/` for CI/CD, `scripts/` for utilities
- Paths reference existing `src/` structure from Feature 001

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Docker infrastructure setup

- [ ] T001 [P] [Setup] Create `.dockerignore` file at repository root with patterns: `.git`, `.gitignore`, `.env`, `*.pyc`, `__pycache__`, `.venv`, `venv/`, `data/`, `*.db`, `*.log`, `tests/`, `docs/`, `specs/`, `.github/`, `README.md`
- [ ] T002 [P] [Setup] Create `scripts/` directory at repository root for container lifecycle scripts
- [ ] T003 [P] [Setup] Create `.github/workflows/` directory (if not exists) for CI/CD workflows

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Docker files that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [Foundational] Create multi-stage `Dockerfile` at repository root with three stages:
  - Stage 1 (deps): FROM python:3.11-slim, install system dependencies (gcc), copy requirements.txt, pip install --user
  - Stage 2 (builder): FROM python:3.11-slim, copy dependencies from stage 1, copy source code, pip install -e .
  - Stage 3 (runtime): FROM python:3.11-slim, copy artifacts from builder, set PATH, create non-root user (reddit-deliver), add ENTRYPOINT and CMD
- [ ] T005 [P] [Foundational] Create `scripts/docker-entrypoint.sh` with:
  - Shebang and `set -e`
  - Environment variable validation (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, DEEPL_API_KEY)
  - Database initialization check (if /app/data/reddit-deliver.db not exists)
  - exec "$@" to pass control to CMD
- [ ] T006 [P] [Foundational] Create `scripts/health-check.sh` with Python import test for core modules (models.Base, storage.database.get_database)
- [ ] T007 [Foundational] Make scripts executable: `chmod +x scripts/docker-entrypoint.sh scripts/health-check.sh`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Docker Containerization (Priority: P1) 🎯 MVP

**Goal**: Users can build and run reddit-deliver as a Docker container locally

**Independent Test**: Build Docker image locally (`docker build -t reddit-deliver .`) and verify it runs successfully with environment variables

### Implementation for User Story 1

- [ ] T008 [US1] Update `Dockerfile` ENTRYPOINT to reference `/app/scripts/docker-entrypoint.sh`
- [ ] T009 [US1] Update `Dockerfile` CMD to default command: `["reddit-deliver", "monitor", "start", "--once"]`
- [ ] T010 [US1] Add HEALTHCHECK instruction to `Dockerfile` using `scripts/health-check.sh` (interval: 30s, timeout: 10s, retries: 3)
- [ ] T011 [US1] Add volume declaration in `Dockerfile` for `/app/data` directory
- [ ] T012 [US1] Add environment variable documentation as comments in `Dockerfile` (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, DEEPL_API_KEY, DISCORD_WEBHOOK_URL, MONITOR_INTERVAL, SUBREDDITS, POST_LIMIT)
- [ ] T013 [US1] Test local build: `docker build -t reddit-deliver:local .` and verify build completes in <5 minutes
- [ ] T014 [US1] Test container startup: Create test .env file and run `docker run --rm --env-file .env reddit-deliver:local reddit-deliver --version`
- [ ] T015 [US1] Verify image size is under 500MB: `docker image inspect reddit-deliver:local --format='{{.Size}}'`

**Checkpoint**: At this point, User Story 1 should be fully functional - users can build and run Docker containers locally

---

## Phase 4: User Story 2 - Docker Compose Orchestration (Priority: P1)

**Goal**: Users can deploy reddit-deliver using Docker Compose with simple configuration

**Independent Test**: Run `docker-compose up` and verify service starts with proper configuration from .env file

### Implementation for User Story 2

- [ ] T016 [US2] Create `docker-compose.yml` at repository root with:
  - Version: '3.8'
  - Service: reddit-deliver (build: ., image: reddit-deliver:latest, container_name: reddit-deliver)
  - env_file: .env
  - Volume: reddit-deliver-data:/app/data (named volume)
  - restart: unless-stopped
  - healthcheck: test command using Python import check, interval 30s, timeout 10s, retries 3
  - Named volume declaration: reddit-deliver-data with driver: local
- [ ] T017 [P] [US2] Create `docker-compose.dev.yml` override file with:
  - Volume override: ./data:/app/data (bind mount for development)
  - environment: LOG_LEVEL=DEBUG
  - Command override for development mode
- [ ] T018 [P] [US2] Create `.env.example` file at repository root with template environment variables:
  - REDDIT_CLIENT_ID=your_client_id_here
  - REDDIT_CLIENT_SECRET=your_client_secret_here
  - REDDIT_USER_AGENT=reddit-deliver/0.1.0
  - DEEPL_API_KEY=your_deepl_api_key_here
  - DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
  - MONITOR_INTERVAL=300
  - SUBREDDITS=python,programming,docker
  - POST_LIMIT=10
- [ ] T019 [US2] Add `.env` to `.gitignore` (if not already present)
- [ ] T020 [US2] Test Docker Compose build and startup: `docker-compose up -d` and verify service starts
- [ ] T021 [US2] Test volume persistence: Create container, stop, restart, verify data directory persists
- [ ] T022 [US2] Test logs: `docker-compose logs -f reddit-deliver` and verify monitoring activity is visible

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can deploy via Docker Compose

---

## Phase 5: User Story 3 - GitHub Container Registry Publishing (Priority: P2)

**Goal**: Docker images are automatically built and published to GitHub Container Registry (GHCR)

**Independent Test**: Push code to GitHub with version tag, verify image is built and published to ghcr.io

### Implementation for User Story 3

- [ ] T023 [P] [US3] Create `.github/workflows/docker-build.yml` for PR validation:
  - name: Docker Build CI
  - on: pull_request to main branch, paths: Dockerfile, src/**, requirements.txt, .github/workflows/docker-build.yml
  - job: build-test on ubuntu-latest
  - steps: checkout@v4, setup-buildx-action@v3, build-push-action@v5 (push: false, tags: reddit-deliver:test, cache-from/to: type=gha)
  - step: Test container startup with `docker run --rm reddit-deliver:test reddit-deliver --version`
  - step: Check image size (fail if >500MB)
- [ ] T024 [P] [US3] Create `.github/workflows/docker-publish.yml` for release publishing:
  - name: Publish Docker Image
  - on: push tags v*, workflow_dispatch
  - env: REGISTRY=ghcr.io, IMAGE_NAME=${{ github.repository }}
  - job: publish on ubuntu-latest
  - permissions: contents: read, packages: write
  - steps: checkout@v4, metadata-action@v5 (extract tags/labels), setup-qemu-action@v3, setup-buildx-action@v3
  - step: login-action@v3 to GHCR (registry: ghcr.io, username: github.actor, password: GITHUB_TOKEN)
  - step: build-push-action@v5 (context: ., platforms: linux/amd64,linux/arm64, push: true, tags/labels from meta, cache-from/to: type=gha)
  - step: Echo image digest
- [ ] T025 [US3] Update `docker-compose.yml` to support pulling from GHCR by adding comments showing both build and image options
- [ ] T026 [US3] Test PR workflow: Create test branch, open PR, verify docker-build.yml runs successfully
- [ ] T027 [US3] Document GitHub repository settings requirements in quickstart.md:
  - Settings → Actions → General → Workflow permissions: "Read and write permissions"
  - Settings → Actions → General → Enable "Allow GitHub Actions to create and approve pull requests"

**Checkpoint**: All P1 and P2 user stories complete - GitHub Actions automates image building and publishing

---

## Phase 6: User Story 4 - Multi-Architecture Support (Priority: P3)

**Goal**: Docker images support both AMD64 and ARM64 architectures (Apple Silicon, Raspberry Pi)

**Independent Test**: Build multi-arch image and verify it runs on both Intel and ARM machines

### Implementation for User Story 4

- [ ] T028 [US4] Verify `docker-publish.yml` platforms setting includes both linux/amd64 and linux/arm64 (already configured in T024)
- [ ] T029 [US4] Test local multi-arch build: `docker buildx create --use && docker buildx build --platform linux/amd64,linux/arm64 -t reddit-deliver:multiarch .`
- [ ] T030 [US4] Create documentation in quickstart.md explaining architecture selection and verification
- [ ] T031 [US4] Test ARM64 image (if ARM64 machine available): Pull image and verify correct architecture with `docker inspect`
- [ ] T032 [US4] Test AMD64 image: Pull image and verify correct architecture with `docker inspect`

**Checkpoint**: All user stories complete - multi-arch images available for diverse platforms

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and improvements that affect multiple user stories

- [ ] T033 [P] [Polish] Create comprehensive `docs/docker-deployment.md` documentation covering:
  - Prerequisites (Docker, Docker Compose, GitHub account)
  - Local build instructions (User Story 1)
  - Docker Compose deployment (User Story 2)
  - Pulling from GHCR (User Story 3)
  - Multi-arch support details (User Story 4)
  - Troubleshooting section
  - Environment variables reference
  - Volume management and backup
  - Production deployment tips
- [ ] T034 [P] [Polish] Update main `README.md` with Docker deployment section:
  - Quick start with Docker Compose
  - Link to detailed docs/docker-deployment.md
  - Badge for GHCR image
  - Architecture support badges (AMD64, ARM64)
- [ ] T035 [P] [Polish] Add `CHANGELOG.md` entry for Feature 002 documenting:
  - Docker containerization support
  - Docker Compose orchestration
  - GitHub Container Registry publishing
  - Multi-architecture support (AMD64 + ARM64)
- [ ] T036 [Polish] Validate quickstart.md scenarios:
  - Test Option 1 (Pull from GHCR)
  - Test Option 2 (Build locally)
  - Test Option 3 (Docker Compose with local build)
  - Verify all commands work as documented
- [ ] T037 [Polish] Security hardening review:
  - Verify .dockerignore excludes sensitive files (.env, *.db)
  - Verify non-root user in Dockerfile
  - Verify no secrets in image layers
  - Document security best practices in docs/docker-deployment.md
- [ ] T038 [Polish] Performance optimization validation:
  - Verify layer caching works (rebuild should be <2 minutes)
  - Verify image size is under 500MB
  - Verify startup time is under 30 seconds
  - Document build times in research.md if different from estimates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1) - Docker Containerization: Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1) - Docker Compose: Depends on User Story 1 (needs working Dockerfile)
  - User Story 3 (P2) - GHCR Publishing: Depends on User Story 1 (needs working Dockerfile), independent of US2
  - User Story 4 (P3) - Multi-Arch: Depends on User Story 3 (extends docker-publish.yml), independent of US2
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ↓
US1: Docker Containerization (P1) ← MVP
    ↓
    ├── US2: Docker Compose (P1)
    └── US3: GHCR Publishing (P2)
            ↓
        US4: Multi-Arch (P3)
```

### Within Each User Story

- Foundational tasks (Dockerfile, scripts) before implementation
- Core implementation before testing
- Testing before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks (T001, T002, T003) can run in parallel
- **Phase 2 (Foundational)**: T005 and T006 can run in parallel (different files)
- **Phase 4 (US2)**: T017 and T018 can run in parallel (different files)
- **Phase 5 (US3)**: T023 and T024 can run in parallel (different workflow files)
- **Phase 7 (Polish)**: T033, T034, T035 can run in parallel (different files)

**Note**: User Stories must be executed sequentially due to dependencies, but tasks within each story marked [P] can be parallelized.

---

## Parallel Example: Setup Phase

```bash
# Launch all setup tasks together:
Task: "Create .dockerignore file at repository root"
Task: "Create scripts/ directory at repository root"
Task: "Create .github/workflows/ directory"
```

## Parallel Example: Foundational Phase

```bash
# After T004 (Dockerfile) completes, launch entrypoint and health check scripts in parallel:
Task: "Create scripts/docker-entrypoint.sh"
Task: "Create scripts/health-check.sh"
```

## Parallel Example: User Story 3

```bash
# Launch both GitHub Actions workflows together:
Task: "Create .github/workflows/docker-build.yml"
Task: "Create .github/workflows/docker-publish.yml"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007) - CRITICAL
3. Complete Phase 3: User Story 1 (T008-T015) - Local Docker builds
4. Complete Phase 4: User Story 2 (T016-T022) - Docker Compose
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready - users can now deploy with Docker Compose

**This is the recommended MVP scope** - delivers immediate value for self-hosted deployments.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Local Docker support ✓
3. Add User Story 2 → Test independently → Docker Compose support ✓ (MVP!)
4. Add User Story 3 → Test independently → GHCR publishing ✓
5. Add User Story 4 → Test independently → Multi-arch support ✓
6. Polish → Complete documentation and optimization

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T007)
2. Once Foundational is done:
   - Developer A: User Story 1 (T008-T015)
   - Wait for US1 completion, then:
     - Developer A: User Story 2 (T016-T022)
     - Developer B: User Story 3 (T023-T027) - can start after US1
3. After US3 completes:
   - Developer B: User Story 4 (T028-T032)
4. Developers A+B: Polish tasks (T033-T038) in parallel

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (US1 - Docker Containerization)**: 8 tasks
- **Phase 4 (US2 - Docker Compose)**: 7 tasks
- **Phase 5 (US3 - GHCR Publishing)**: 5 tasks
- **Phase 6 (US4 - Multi-Arch)**: 5 tasks
- **Phase 7 (Polish)**: 6 tasks

**Total**: 38 tasks

### Tasks Per User Story

- **User Story 1 (P1)**: 8 tasks (T008-T015)
- **User Story 2 (P1)**: 7 tasks (T016-T022)
- **User Story 3 (P2)**: 5 tasks (T023-T027)
- **User Story 4 (P3)**: 5 tasks (T028-T032)
- **Setup + Foundational**: 7 tasks (T001-T007)
- **Polish**: 6 tasks (T033-T038)

### Parallel Opportunities Identified

- **11 tasks marked [P]** for parallel execution within their phases
- **4 user stories** that can be worked on sequentially with some parallelization within stories
- **Estimated MVP time**: 1-2 days for experienced developer (Phases 1-4 only)
- **Estimated full feature time**: 3-4 days for experienced developer (all phases)

### Independent Test Criteria

- **US1**: Build image locally, run container with env vars, verify startup and version command
- **US2**: Run docker-compose up, verify service starts, check logs, test volume persistence
- **US3**: Push tagged code, verify GitHub Actions runs, check GHCR for published image
- **US4**: Inspect image manifest, verify both AMD64 and ARM64 platforms available

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (e.g., after completing each user story phase)
- Stop at any checkpoint to validate story independently
- User Story 1+2 = MVP (local deployment capability)
- User Story 3 = Distribution capability (GHCR publishing)
- User Story 4 = Platform diversity (multi-arch)
- Avoid: vague tasks, same file conflicts, breaking changes between stories
- All file paths are relative to repository root unless specified otherwise
- GitHub Actions workflows require repository settings configuration (documented in T027)
