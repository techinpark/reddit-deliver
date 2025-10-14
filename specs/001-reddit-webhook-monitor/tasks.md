# Tasks: Reddit Monitoring and Webhook Delivery System

**Input**: Design documents from `/specs/001-reddit-webhook-monitor/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-interface.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths use absolute references from project root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (src/, tests/, data/, config/)
- [X] T002 Initialize Python project with pyproject.toml and requirements.txt
- [X] T003 [P] Create .env.example file with required environment variables
- [X] T004 [P] Create .gitignore with .env, data/, *.log entries
- [X] T005 [P] Configure structured logging setup in src/lib/logger.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create SQLAlchemy base model in src/models/__init__.py
- [X] T007 [P] Create UserConfig model in src/models/user_config.py
- [X] T008 [P] Create Subreddit model in src/models/subreddit.py
- [X] T009 [P] Create WebhookConfig model in src/models/webhook_config.py
- [X] T010 [P] Create Post model in src/models/post.py
- [X] T011 [P] Create Translation model in src/models/translation.py
- [X] T012 Create database initialization module in src/storage/database.py with engine setup and session management
- [X] T013 Create database schema initialization script in src/storage/migrations/init_schema.py
- [X] T014 [P] Implement rate limiter utility in src/lib/rate_limiter.py for API throttling
- [X] T015 Create CLI entry point skeleton in src/cli/main.py with argparse structure
- [X] T016 Create CLI base utilities in src/cli/__init__.py (output formatters, error handlers)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Monitor Single Subreddit and Receive Notifications (Priority: P1) 🎯 MVP

**Goal**: Users can register a subreddit URL and receive new posts via webhook in their preferred language.

**Independent Test**: Can be fully tested by registering r/ClaudeAI, posting new content, and verifying webhook delivery with translated content and original link.

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement Reddit client service in src/services/reddit_client.py (PRAW initialization, authentication, subreddit fetching)
- [X] T018 [P] [US1] Implement translation service in src/services/translator.py (DeepL API integration, language detection, caching)
- [X] T019 [P] [US1] Implement webhook sender service in src/services/webhook_sender.py (Discord format, HTTP POST with retry)
- [X] T020 [US1] Implement monitoring orchestrator in src/services/monitor.py (poll subreddits, coordinate translation + webhook)
- [X] T021 [US1] Create config CLI commands in src/cli/config.py (init, set, get for language and poll_interval)
- [X] T022 [US1] Create subreddit CLI commands in src/cli/subreddit.py (add command only for US1)
- [X] T023 [US1] Create webhook CLI commands in src/cli/webhook.py (set command for Discord only for US1)
- [X] T024 [US1] Create monitor CLI commands in src/cli/monitor_cmd.py (start --once command for single check cycle)
- [X] T025 [US1] Integrate all CLI commands into src/cli/main.py entry point
- [X] T026 [US1] Create requirements.txt with core dependencies (praw, deepl, requests, sqlalchemy, pydantic, pyyaml)
- [X] T027 [US1] Add duplicate post detection logic to monitor service (check Post.id before creating)
- [X] T028 [US1] Add error handling and logging to all US1 services

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can monitor one subreddit and receive translated Discord notifications.

---

## Phase 4: User Story 2 - Configure Multiple Subreddits (Priority: P2)

**Goal**: Users can register and monitor multiple subreddit URLs simultaneously.

**Independent Test**: Register 3 different subreddits and verify each sends notifications independently.

### Implementation for User Story 2

- [ ] T029 [US2] Extend subreddit CLI commands in src/cli/subreddit.py (add list, remove, enable, disable commands)
- [ ] T030 [US2] Update monitor service in src/services/monitor.py to iterate over all enabled subreddits
- [ ] T031 [US2] Add concurrent subreddit checking logic using threading or asyncio in src/services/monitor.py
- [ ] T032 [US2] Add subreddit enable/disable filtering logic to monitor service
- [ ] T033 [US2] Update CLI output formatting for list command with status indicators

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can monitor multiple subreddits simultaneously.

---

## Phase 5: User Story 3 - Configure Webhook Destinations (Priority: P2)

**Goal**: Users can choose between Discord and Slack webhooks and configure the destination URL.

**Independent Test**: Configure Discord webhook, verify notifications arrive; switch to Slack webhook, verify notifications arrive there instead.

### Implementation for User Story 3

- [ ] T034 [P] [US3] Add Slack webhook format support to src/services/webhook_sender.py
- [ ] T035 [US3] Implement webhook type detection logic in src/services/webhook_sender.py (Discord vs Slack)
- [ ] T036 [US3] Update webhook CLI commands in src/cli/webhook.py (add test, enable, disable commands)
- [ ] T037 [US3] Add webhook URL validation (regex matching for Discord/Slack formats) to webhook CLI
- [ ] T038 [US3] Implement webhook test function in src/services/webhook_sender.py (send test message)
- [ ] T039 [US3] Update monitor service to support both Discord and Slack webhooks

**Checkpoint**: All webhook destinations (Discord and Slack) should now be independently functional.

---

## Phase 6: User Story 4 - Configure Translation Language (Priority: P3)

**Goal**: Users can select their preferred target language for post translations.

**Independent Test**: Set language to Korean, verify posts are translated to Korean; change to Japanese, verify new posts are in Japanese.

### Implementation for User Story 4

- [ ] T040 [US4] Add language validation to config CLI in src/cli/config.py (check against DeepL supported languages)
- [ ] T041 [US4] Implement source language detection in src/services/translator.py
- [ ] T042 [US4] Add same-language detection skip logic in src/services/translator.py (avoid translating if source == target)
- [ ] T043 [US4] Update translation caching to consider target_lang in lookup (Translation table query)
- [ ] T044 [US4] Add language configuration display to monitor status output

**Checkpoint**: All user stories should now be independently functional. Language configuration works for all supported DeepL languages.

---

## Phase 7: Background Monitoring & Advanced Features

**Purpose**: Enhancements that span multiple user stories

- [ ] T045 [P] Integrate APScheduler for interval-based monitoring in src/services/monitor.py
- [ ] T046 Add daemon mode support to monitor CLI in src/cli/monitor.py (--daemon flag, PID file management)
- [ ] T047 Implement monitor stop command in src/cli/monitor.py (kill daemon process)
- [ ] T048 Implement monitor status command in src/cli/monitor.py (read PID, check process, display stats)
- [ ] T049 [P] Create history CLI commands in src/cli/history.py (posts command with filtering)
- [ ] T050 Add retry logic with exponential backoff to src/services/webhook_sender.py
- [ ] T051 Add translation API quota tracking and warnings to src/services/translator.py
- [ ] T052 Implement post content truncation for webhook limits in src/services/webhook_sender.py
- [ ] T053 Add comprehensive error handling for Reddit API rate limits in src/services/reddit_client.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T054 [P] Create config.yaml template file in config/config.yaml
- [ ] T055 [P] Create README.md with installation and usage instructions
- [ ] T056 [P] Add --json output format support to all CLI commands
- [ ] T057 [P] Add --verbose logging option to CLI entry point
- [ ] T058 Add human-readable timestamp formatting for CLI outputs
- [ ] T059 Implement graceful shutdown handling (SIGINT/SIGTERM) in monitor service
- [ ] T060 Add validation for environment variables on startup
- [ ] T061 Create example .env file with all required keys documented
- [ ] T062 Add CLI version command (--version flag)
- [ ] T063 Optimize database queries with proper indexes (already defined in schema)
- [ ] T064 Add progress indicators for long-running operations (translation, webhook delivery)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1) can start after Foundational
  - User Story 2 (P2) depends on US1 completion (extends subreddit management)
  - User Story 3 (P2) can start after US1 (parallel with US2)
  - User Story 4 (P3) can start after US1 (parallel with US2/US3)
- **Background Monitoring (Phase 7)**: Depends on US1 being complete
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Extends US1 subreddit CLI - depends on T022 (subreddit add command)
- **User Story 3 (P2)**: Extends US1 webhook CLI - depends on T023 (webhook set command)
- **User Story 4 (P3)**: Enhances US1 translation - depends on T018 (translation service)

### Within Each User Story

- Setup tasks before models
- Models before services (foundation models created in Phase 2)
- Services before CLI commands
- CLI commands before integration into main entry point
- Error handling added after core implementation

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational model tasks (T007-T011) marked [P] can run in parallel
- Within User Story 1:
  - T017 (Reddit client), T018 (Translation), T019 (Webhook) can run in parallel
  - T021 (config CLI), T022 (subreddit CLI), T023 (webhook CLI), T024 (monitor CLI) can run after services, in parallel
- User Story 3 and User Story 4 can be developed in parallel after US1 completes
- Phase 8 polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 Core Services

```bash
# Launch all core services for User Story 1 together:
Task T017: "Implement Reddit client service in src/services/reddit_client.py"
Task T018: "Implement translation service in src/services/translator.py"
Task T019: "Implement webhook sender service in src/services/webhook_sender.py"

# Then launch all CLI commands together:
Task T021: "Create config CLI commands in src/cli/config.py"
Task T022: "Create subreddit CLI commands in src/cli/subreddit.py"
Task T023: "Create webhook CLI commands in src/cli/webhook.py"
Task T024: "Create monitor CLI commands in src/cli/monitor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Register r/ClaudeAI
   - Run monitor --once
   - Verify Discord notification with Korean translation
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
   - Single subreddit monitoring works
   - Translation to Korean works
   - Discord webhook delivery works
3. Add User Story 2 → Test independently → Deploy/Demo
   - Multiple subreddit monitoring works
   - All previous features still work
4. Add User Story 3 → Test independently → Deploy/Demo
   - Slack webhook option works
   - Discord still works
5. Add User Story 4 → Test independently → Deploy/Demo
   - Language switching works
   - All webhook destinations work with new languages
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T017-T028)
   - Developer B: User Story 3 (waits for US1 webhook service, then T034-T039)
   - Developer C: User Story 4 (waits for US1 translation service, then T040-T044)
3. Developer A completes US1, then starts US2 (T029-T033)
4. Stories complete and integrate independently

---

## Task Count Summary

| Phase | Task Range | Count | Can Start After |
|-------|------------|-------|-----------------|
| Setup | T001-T005 | 5 | Immediately |
| Foundational | T006-T016 | 11 | Setup complete |
| User Story 1 (P1) | T017-T028 | 12 | Foundational complete |
| User Story 2 (P2) | T029-T033 | 5 | US1 complete |
| User Story 3 (P2) | T034-T039 | 6 | US1 complete |
| User Story 4 (P3) | T040-T044 | 5 | US1 complete |
| Background Monitoring | T045-T053 | 9 | US1 complete |
| Polish | T054-T064 | 11 | All US complete |
| **TOTAL** | | **64** | |

---

## Critical Path for MVP (User Story 1 Only)

**Minimum viable path** (28 tasks):

```
T001 → T002 → T003 → T004 → T005 (Setup: 5 tasks)
  ↓
T006 → [T007, T008, T009, T010, T011] → T012 → T013 → T014 → T015 → T016 (Foundational: 11 tasks)
  ↓
[T017, T018, T019] → T020 → [T021, T022, T023, T024] → T025 → T026 → T027 → T028 (US1: 12 tasks)
```

**Estimated effort for MVP**: 28 tasks, approximately 3-5 days for single developer

---

## Validation Checklist

After completing each user story:

### User Story 1 Validation
- [ ] Can initialize config with `reddit-deliver config init`
- [ ] Can set language with `reddit-deliver config set language ko`
- [ ] Can add subreddit with `reddit-deliver subreddit add ClaudeAI`
- [ ] Can set webhook with `reddit-deliver webhook set discord <url>`
- [ ] Can run single check with `reddit-deliver monitor start --once`
- [ ] New Reddit post is detected within 5 minutes
- [ ] Post title and content are translated to Korean
- [ ] Discord webhook receives notification with translated text and original link
- [ ] No duplicate notifications for same post

### User Story 2 Validation
- [ ] Can add multiple subreddits
- [ ] Can list all subreddits with status
- [ ] Can remove a subreddit
- [ ] Can enable/disable individual subreddits
- [ ] Monitor checks all enabled subreddits
- [ ] Each subreddit sends independent notifications

### User Story 3 Validation
- [ ] Can configure Slack webhook
- [ ] Can test webhook delivery
- [ ] Discord notifications use Discord format
- [ ] Slack notifications use Slack format
- [ ] Invalid webhook URLs are rejected
- [ ] Can switch between Discord and Slack

### User Story 4 Validation
- [ ] Can change translation language
- [ ] Posts are translated to new language
- [ ] Same-language posts skip translation
- [ ] Invalid language codes are rejected
- [ ] Language persists across monitor restarts

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- No test tasks included as tests were not explicitly requested in spec
- All environment variables must be documented in .env.example
- Database schema automatically created on first run via T013
