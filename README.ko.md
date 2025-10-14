# 🤖 reddit-deliver

**[English](README.md)** | **[한국어](README.ko.md)**

> 웹훅 전달 및 다국어 번역을 지원하는 Reddit 게시물 모니터링 서비스

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://github.com/techinpark/reddit-deliver/pkgs/container/reddit-deliver)
[![GitHub issues](https://img.shields.io/github/issues/techinpark/reddit-deliver)](https://github.com/techinpark/reddit-deliver/issues)

좋아하는 서브레딧의 소식을 놓치지 마세요! **reddit-deliver**는 Reddit 커뮤니티를 자동으로 모니터링하고, 게시물을 원하는 언어로 번역한 뒤, Discord나 Slack 웹훅을 통해 알림을 전달합니다.

---

## ✨ 주요 기능

- 🔍 **스마트 모니터링** - 좋아하는 서브레딧의 새 게시물을 자동으로 추적
- 🌍 **다국어 번역** - DeepL API를 사용한 게시물 번역 (30개 이상 언어 지원)
- 📢 **웹훅 알림** - Discord, Slack 또는 커스텀 웹훅으로 전달
- 🚫 **중복 감지** - 동일한 게시물을 두 번 받지 않음
- 💾 **영구 저장소** - 설정 및 이력 관리를 위한 SQLite 데이터베이스
- 🐳 **Docker 지원** - Docker Compose를 사용한 원클릭 배포
- 🔧 **CLI 인터페이스** - 명령줄 도구를 통한 간편한 설정
- ⚡ **경량화** - 최소한의 리소스 사용, 셀프 호스팅에 완벽

---

## 📦 설치 방법

### 옵션 1: Docker Compose (권장)

가장 빠른 시작 방법!

```bash
# 저장소 클론
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# 환경 변수 템플릿 복사
cp .env.example .env

# API 인증 정보로 .env 파일 수정
nano .env

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 옵션 2: Docker (수동)

```bash
# 최신 이미지 다운로드
docker pull ghcr.io/techinpark/reddit-deliver:latest

# 인증 정보가 담긴 .env 파일 생성
# 컨테이너 실행
docker run -d \
  --name reddit-deliver \
  --env-file .env \
  -v reddit-deliver-data:/app/data \
  --restart unless-stopped \
  ghcr.io/techinpark/reddit-deliver:latest
```

### 옵션 3: 로컬 설치

```bash
# 저장소 클론
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 모드로 설치
pip install -e .

# 데이터베이스 초기화
python src/storage/migrations/init_schema.py
```

---

## 🚀 빠른 시작 가이드

### 1. API 인증 정보 받기

#### Reddit API
1. [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)로 이동
2. "Create App" 또는 "Create Another App" 클릭
3. 양식 작성:
   - **name**: `reddit-deliver` (또는 원하는 이름)
   - **type**: "script" 선택
   - **redirect uri**: `http://localhost:8080` (필수이지만 사용되지 않음)
4. "Create app" 클릭
5. **client ID** (앱 이름 아래)와 **secret** 복사

#### DeepL API
1. [https://www.deepl.com/pro-api](https://www.deepl.com/pro-api)로 이동
2. **무료 계정** 가입 (월 50만 글자 제공)
3. 이메일 인증 및 결제 수단 추가 (무료 플랜은 요금 부과되지 않음)
4. [계정 설정](https://www.deepl.com/account/summary)으로 이동
5. **API 키** 복사

#### Discord 웹훅
1. Discord를 열고 서버로 이동
2. **서버 설정** → **연동** → **웹훅**으로 이동
3. **새 웹훅** 클릭
4. 이름 설정 (예: "Reddit Bot"), 채널 선택
5. **웹훅 URL 복사** 클릭

#### Slack 웹훅 (선택 사항)
1. [https://api.slack.com/apps](https://api.slack.com/apps)로 이동
2. **Create New App** → **From scratch** 클릭
3. 앱 이름 지정 및 워크스페이스 선택
4. **Incoming Webhooks**로 이동 → 활성화
5. **Add New Webhook to Workspace** 클릭
6. 채널 선택 후 웹훅 URL 복사

### 2. 환경 변수 설정

`.env` 파일 생성:

```bash
# Reddit API 설정
REDDIT_CLIENT_ID=여기에_클라이언트_ID_입력
REDDIT_CLIENT_SECRET=여기에_클라이언트_시크릿_입력
REDDIT_USER_AGENT=reddit-deliver/0.1.0

# DeepL 번역 API
DEEPL_API_KEY=여기에_DeepL_API_키_입력

# Discord 웹훅 (필수)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/여기에_웹훅_URL_입력

# 선택 사항: Slack 웹훅
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/여기에_웹훅_URL_입력

# 모니터링 설정
MONITOR_INTERVAL=300        # 확인 간격(초) (기본값: 5분)
SUBREDDITS=python,programming,docker,ClaudeAI  # 쉼표로 구분된 목록
POST_LIMIT=10               # 서브레딧당 가져올 게시물 수
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

### 3. 초기 설정

```bash
# 설정 초기화
reddit-deliver config init

# 번역 언어 설정 (예: ko, ja, de, fr, es, it, pt, ru, zh)
reddit-deliver config set language ko

# 모니터링할 서브레딧 추가
reddit-deliver subreddit add ClaudeAI
reddit-deliver subreddit add python
reddit-deliver subreddit add programming

# 모니터링 중인 서브레딧 목록
reddit-deliver subreddit list

# Discord 웹훅 설정
reddit-deliver webhook set discord https://discord.com/api/webhooks/여기에_웹훅_URL_입력

# 웹훅 연결 테스트
reddit-deliver webhook test discord
```

### 4. 모니터링 시작

```bash
# 단일 모니터링 주기 실행 (테스트용)
reddit-deliver monitor start --once

# 지속적인 모니터링 (데몬 모드 - 곧 제공 예정)
# reddit-deliver monitor start
```

---

## 🎯 사용 예제

### 여러 서브레딧 모니터링

```bash
# 여러 서브레딧 추가
reddit-deliver subreddit add MachineLearning
reddit-deliver subreddit add kubernetes
reddit-deliver subreddit add golang

# 모니터링 중인 모든 서브레딧 확인
reddit-deliver subreddit list
```

### 번역 언어 변경

```bash
# 일본어로 변경
reddit-deliver config set language ja

# 독일어로 변경
reddit-deliver config set language de

# 번역 비활성화 (원본 영어)
reddit-deliver config set language en
```

### 여러 웹훅 사용

```bash
# Discord 웹훅 설정
reddit-deliver webhook set discord https://discord.com/api/webhooks/...

# Slack 웹훅 설정
reddit-deliver webhook set slack https://hooks.slack.com/services/...

# 둘 다 테스트
reddit-deliver webhook test discord
reddit-deliver webhook test slack
```

### 상태 확인

```bash
# 현재 설정 확인
reddit-deliver config show

# 최근 게시물 확인
reddit-deliver history show --limit 10
```

---

## 🐳 Docker 배포 가이드

### Docker Compose 사용

프로덕션 배포를 위한 권장 방법:

```bash
# 저장소 클론 및 이동
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# 인증 정보로 .env 파일 생성
cp .env.example .env
nano .env

# 백그라운드에서 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f reddit-deliver

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 최신 버전으로 업데이트
docker-compose pull
docker-compose up -d
```

### Docker Compose 구성

포함된 `docker-compose.yml`이 제공하는 기능:

- **자동 재시작** - 실패 시 서비스 자동 재시작
- **볼륨 영속성** - 컨테이너 재시작에도 데이터베이스 유지
- **헬스 체크** - 자동 상태 모니터링
- **환경 격리** - .env 파일을 통한 인증 정보 관리
- **로그 관리** - stdout으로의 구조화된 로깅

### 볼륨 관리

데이터베이스 백업:

```bash
# 볼륨 위치 찾기
docker volume inspect reddit-deliver-data

# 데이터베이스 백업
docker run --rm \
  -v reddit-deliver-data:/data \
  -v $(pwd):/backup \
  alpine cp /data/reddit-deliver.db /backup/reddit-deliver-backup.db
```

데이터베이스 복원:

```bash
docker run --rm \
  -v reddit-deliver-data:/data \
  -v $(pwd):/backup \
  alpine cp /backup/reddit-deliver-backup.db /data/reddit-deliver.db
```

### 멀티 아키텍처 지원

Reddit-deliver는 여러 아키텍처를 지원합니다:

| 플랫폼 | 아키텍처 | 상태 |
|----------|--------------|--------|
| Intel/AMD PC | linux/amd64 | ✅ 지원 |
| Apple Silicon (M1/M2/M3) | linux/arm64 | ✅ 지원 |
| Raspberry Pi 4/5 | linux/arm64 | ✅ 지원 |
| AWS Graviton | linux/arm64 | ✅ 지원 |

Docker가 자동으로 플랫폼에 맞는 올바른 아키텍처를 다운로드합니다.

### Cron으로 스케줄링

주기적인 모니터링 실행:

```bash
# crontab에 추가
crontab -e

# 5분마다 실행
*/5 * * * * cd /path/to/reddit-deliver && docker-compose run --rm reddit-deliver reddit-deliver monitor start --once

# 매 시간마다 실행
0 * * * * cd /path/to/reddit-deliver && docker-compose run --rm reddit-deliver reddit-deliver monitor start --once
```

---

## 🔧 설정 참고

### 환경 변수

| 변수 | 필수 | 기본값 | 설명 |
|----------|----------|---------|-------------|
| `REDDIT_CLIENT_ID` | ✅ 예 | - | Reddit API 클라이언트 ID |
| `REDDIT_CLIENT_SECRET` | ✅ 예 | - | Reddit API 클라이언트 시크릿 |
| `REDDIT_USER_AGENT` | ✅ 예 | - | Reddit API 사용자 에이전트 (형식: 앱이름/버전) |
| `DEEPL_API_KEY` | ✅ 예 | - | DeepL 번역 API 키 |
| `DISCORD_WEBHOOK_URL` | ✅ 예 | - | 알림을 위한 Discord 웹훅 URL |
| `SLACK_WEBHOOK_URL` | ❌ 아니오 | - | Slack 웹훅 URL (선택 사항) |
| `MONITOR_INTERVAL` | ❌ 아니오 | 300 | 모니터링 간격(초) |
| `SUBREDDITS` | ❌ 아니오 | python | 쉼표로 구분된 서브레딧 목록 |
| `POST_LIMIT` | ❌ 아니오 | 10 | 확인당 가져올 게시물 수 |
| `LOG_LEVEL` | ❌ 아니오 | INFO | 로깅 레벨 (DEBUG, INFO, WARNING, ERROR) |

### 지원 언어 (DeepL)

| 코드 | 언어 | 코드 | 언어 |
|------|----------|------|----------|
| `en` | 영어 (번역 안 함) | `ko` | 한국어 |
| `ja` | 일본어 | `zh` | 중국어 (간체) |
| `de` | 독일어 | `fr` | 프랑스어 |
| `es` | 스페인어 | `it` | 이탈리아어 |
| `pt` | 포르투갈어 | `ru` | 러시아어 |
| `nl` | 네덜란드어 | `pl` | 폴란드어 |

[전체 목록](https://www.deepl.com/docs-api/translate-text/)을 확인하세요.

---

## 📁 프로젝트 구조

```
reddit-deliver/
├── src/
│   ├── models/              # SQLAlchemy 데이터 모델
│   │   ├── __init__.py
│   │   ├── base.py         # 베이스 모델 클래스
│   │   ├── config.py       # 설정 모델
│   │   ├── subreddit.py    # 서브레딧 모델
│   │   ├── webhook.py      # 웹훅 모델
│   │   └── post.py         # 게시물 이력 모델
│   ├── services/            # 비즈니스 로직 서비스
│   │   ├── reddit.py       # Reddit API 클라이언트
│   │   ├── translator.py   # DeepL 번역
│   │   ├── webhook.py      # 웹훅 전달
│   │   └── monitor.py      # 모니터링 오케스트레이션
│   ├── storage/             # 데이터베이스 레이어
│   │   ├── database.py     # 데이터베이스 연결
│   │   └── migrations/     # 스키마 마이그레이션
│   ├── cli/                 # 명령줄 인터페이스
│   │   ├── main.py         # CLI 진입점
│   │   ├── config.py       # 설정 명령어
│   │   ├── subreddit.py    # 서브레딧 명령어
│   │   ├── webhook.py      # 웹훅 명령어
│   │   └── monitor.py      # 모니터 명령어
│   └── lib/                 # 유틸리티
│       ├── logger.py       # 로깅 설정
│       └── env.py          # 환경 헬퍼
├── data/                    # 런타임 데이터 (gitignore됨)
│   └── reddit-deliver.db   # SQLite 데이터베이스
├── scripts/                 # 컨테이너 스크립트
│   ├── docker-entrypoint.sh   # 컨테이너 초기화
│   └── health-check.sh        # 헬스 체크 스크립트
├── .github/
│   └── workflows/           # CI/CD 파이프라인
│       ├── docker-build.yml   # PR 검증
│       └── docker-publish.yml # 릴리스 퍼블리싱
├── specs/                   # 기능 명세
│   ├── 001-reddit-webhook-monitor/
│   └── 002-docker-deployment/
├── Dockerfile               # 멀티 스테이지 프로덕션 빌드
├── docker-compose.yml       # Compose 오케스트레이션
├── .dockerignore            # 빌드 최적화
├── .env.example             # 환경 변수 템플릿
├── requirements.txt         # Python 의존성
├── setup.py                 # 패키지 설정
└── README.md                # 이 파일
```

---

## 🛠️ 개발

### 로컬 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/techinpark/reddit-deliver.git
cd reddit-deliver

# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate

# 개발 의존성 설치
pip install -r requirements.txt
pip install -e .

# 데이터베이스 초기화
python src/storage/migrations/init_schema.py

# 테스트 실행 (곧 제공 예정)
# pytest tests/

# 린터 실행
# flake8 src/
```

### 로컬에서 Docker 이미지 빌드

```bash
# 단일 아키텍처 이미지 빌드
docker build -t reddit-deliver:local .

# 멀티 아키텍처 이미지 빌드
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t reddit-deliver:multiarch \
  --load .

# 이미지 테스트
docker run --rm --env-file .env reddit-deliver:local reddit-deliver --version
```

### 기여하기

기여를 환영합니다! 다음과 같이 도와주실 수 있습니다:

1. **저장소 포크**
2. **기능 브랜치 생성**: `git checkout -b feature/amazing-feature`
3. **변경 사항 작성**
4. **테스트 실행**: 모든 테스트가 통과하는지 확인
5. **변경 사항 커밋**: `git commit -m 'Add amazing feature'`
6. **브랜치에 푸시**: `git push origin feature/amazing-feature`
7. **Pull Request 열기**

#### 기여 가이드라인

- 기존 코드 스타일 준수 (Python의 경우 PEP 8)
- 명확한 커밋 메시지 작성
- 새 기능에 대한 테스트 추가
- 필요에 따라 문서 업데이트
- Pull Request는 집중적이고 작게 유지

---

## 🗺️ 로드맵

### ✅ v0.1.0 - MVP (현재)
- [x] Reddit 게시물 모니터링
- [x] DeepL 번역
- [x] Discord 웹훅 전달
- [x] 중복 감지
- [x] CLI 설정
- [x] SQLite 영속성

### 🚀 v0.2.0 - Docker 지원 (진행 중)
- [ ] 멀티 스테이지 Dockerfile
- [ ] Docker Compose 오케스트레이션
- [ ] GitHub Container Registry 퍼블리싱
- [ ] 멀티 아키텍처 빌드 (AMD64 + ARM64)
- [ ] 컨테이너 헬스 체크

### 📋 v0.3.0 - 향상된 기능 (계획됨)
- [ ] 여러 서브레딧 관리
- [ ] Slack 웹훅 지원
- [ ] 서브레딧별 언어 전환
- [ ] 고급 필터링 (키워드, 플레어, 작성자)
- [ ] 게시물 콘텐츠 포맷팅 옵션

### 🔮 v0.4.0 - 데몬 모드 (미래)
- [ ] 백그라운드 데몬 프로세스
- [ ] Systemd 서비스 통합
- [ ] 설정을 위한 웹 대시보드
- [ ] 메트릭 및 모니터링
- [ ] 속도 제한 및 백오프 전략

### 💡 향후 아이디어
- [ ] 더 많은 웹훅 지원 (Telegram, Microsoft Teams)
- [ ] Reddit 댓글 모니터링
- [ ] 커스텀 게시물 템플릿
- [ ] 웹훅 인증
- [ ] 다중 사용자 지원
- [ ] 클라우드 배포 가이드 (AWS, GCP, Azure)

---

## ❓ 자주 묻는 질문

### 실행 비용이 얼마나 드나요?

reddit-deliver는 모든 서비스의 무료 플랜을 사용합니다:
- **Reddit API**: 무료
- **DeepL API**: 무료 플랜에 월 50만 글자 포함
- **Discord/Slack**: 웹훅은 무료
- **호스팅**: 셀프 호스팅 시 무료, 또는 소형 VPS의 경우 월 약 $5

### 얼마나 자주 새 게시물을 확인하나요?

기본적으로 5분마다 확인합니다 (`MONITOR_INTERVAL=300`). `.env` 파일이나 cron 스케줄링을 통해 조정할 수 있습니다.

### 중복 알림을 받게 되나요?

아니요! reddit-deliver는 전달된 모든 게시물을 데이터베이스에 추적하여 중복을 건너뜁니다.

### 여러 서브레딧을 모니터링할 수 있나요?

네! CLI를 통해 여러 서브레딧을 추가하거나 `SUBREDDITS` 환경 변수에 나열하세요.

### 다른 언어를 지원하나요?

네! DeepL은 30개 이상의 언어를 지원합니다. 다음 명령으로 원하는 언어를 설정하세요:
```bash
reddit-deliver config set language <언어_코드>
```

### 시스템 요구 사항은 무엇인가요?

**최소 사양**:
- Python 3.11+
- 100MB RAM
- 50MB 디스크 공간
- 인터넷 연결

**권장 사양**:
- Python 3.11+
- 256MB RAM
- 100MB 디스크 공간
- 안정적인 인터넷 연결

### 여러 인스턴스를 실행할 수 있나요?

네, 하지만 각 인스턴스는 자체 데이터베이스 파일과 설정이 필요합니다. 별도의 디렉토리나 다른 컨테이너 이름을 사용하세요.

---

## 📝 라이선스

이 프로젝트는 **MIT 라이선스**로 제공됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

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

## 🙏 감사의 말

- **[PRAW](https://praw.readthedocs.io/)** - Python Reddit API Wrapper
- **[DeepL](https://www.deepl.com/)** - 고품질 번역 API
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL 툴킷
- **[Click](https://click.palletsprojects.com/)** - CLI 프레임워크
- **[Docker](https://www.docker.com/)** - 컨테이너화 플랫폼

---

## 📞 지원

- **이슈**: [GitHub Issues](https://github.com/techinpark/reddit-deliver/issues)
- **토론**: [GitHub Discussions](https://github.com/techinpark/reddit-deliver/discussions)
- **이메일**: 지원이 필요하면 이슈를 생성하세요

---

## ⭐ Star 히스토리

이 프로젝트가 유용하다면 Star를 눌러주세요! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=techinpark/reddit-deliver&type=Date)](https://star-history.com/#techinpark/reddit-deliver&Date)

---

<div align="center">

**[techinpark](https://github.com/techinpark)이 ❤️로 만듦**

[⬆ 맨 위로](#-reddit-deliver)

</div>
