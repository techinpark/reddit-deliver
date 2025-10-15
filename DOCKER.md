# Docker로 reddit-deliver 실행하기

## 빠른 시작

### 1. 환경 설정

먼저 `.env` 파일을 생성하세요:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 필요한 API 키와 설정을 입력하세요:

- **필수**: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `DISCORD_WEBHOOK_URL`
- **번역 서비스 선택**: `DEEPL_API_KEY` 또는 `GEMINI_API_KEY` 중 하나
- **선택**: 기타 설정 (모니터링 간격, subreddit 목록 등)

### 2. 디렉토리 생성

데이터와 설정을 저장할 디렉토리를 생성하세요:

```bash
mkdir -p data config
```

### 3. Docker Compose로 실행

```bash
docker compose up -d
```

이 명령어로 다음 작업이 자동으로 수행됩니다:
- Docker 이미지 빌드
- 컨테이너 생성 및 실행
- 백그라운드에서 모니터링 시작

### 4. 로그 확인

```bash
docker compose logs -f
```

## 주요 명령어

### 서비스 중지

```bash
docker compose down
```

### 서비스 재시작

```bash
docker compose restart
```

### 이미지 재빌드

```bash
docker compose build --no-cache
docker compose up -d
```

### 컨테이너 상태 확인

```bash
docker compose ps
```

### 컨테이너 내부 접근

```bash
docker compose exec reddit-deliver /bin/bash
```

## CLI 명령어 실행

Docker 컨테이너 내부에서 CLI 명령어를 실행할 수 있습니다:

```bash
# 설정 초기화
docker compose exec reddit-deliver reddit-deliver config init

# Subreddit 추가
docker compose exec reddit-deliver reddit-deliver subreddit add python

# 번역 서비스 설정 (gemini 또는 deepl)
docker compose exec reddit-deliver reddit-deliver config set translator_service gemini

# 웹훅 설정
docker compose exec reddit-deliver reddit-deliver webhook set discord YOUR_WEBHOOK_URL
```

## 데이터 영속성

다음 디렉토리가 호스트 시스템에 마운트되어 데이터가 영구적으로 저장됩니다:

- `./data`: SQLite 데이터베이스 및 애플리케이션 데이터
- `./config`: 설정 파일

컨테이너를 삭제해도 이 데이터는 유지됩니다.

## 트러블슈팅

### 권한 문제

```bash
sudo chown -R $USER:$USER data config
```

### 포트 충돌

docker-compose.yml에서 포트 설정을 확인하세요.

### 로그 확인

```bash
docker compose logs --tail=100 reddit-deliver
```

## 환경 변수 업데이트

`.env` 파일을 수정한 후 서비스를 재시작하세요:

```bash
docker compose down
docker compose up -d
```
