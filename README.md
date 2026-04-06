# 다중 사이트 RSS/HTML 모니터

roboco.io와 GeekNews(news.hada.io)에 새 글이 올라오면 자동으로 이메일 알림을 보내주는 시스템입니다.

## 🎯 특징

- ✅ **다중 사이트 지원**: roboco.io + GeekNews 동시 모니터링
- ✅ **하이브리드 방식**: RSS(roboco.io) + HTML 크롤링(hada.io)
- ✅ **GitHub Actions**: 무료로 자동 실행 (월 2,000분)
- ✅ **상태 관리**: 사이트별 중복 알림 방지
- ✅ **깔끔한 이메일**: 사이트별로 구분된 HTML 형식

## 📋 설치 방법

### 1. Gmail 앱 비밀번호 생성

1. https://myaccount.google.com/security 접속
2. 2단계 인증 활성화
3. 앱 비밀번호 생성 (16자리)

### 2. GitHub 저장소 생성

1. https://github.com/new 접속
2. 저장소명 입력
3. Create repository

### 3. GitHub Secrets 설정

Settings → Secrets and variables → Actions에서 추가:

- `GMAIL_USER`: Gmail 주소
- `GMAIL_APP_PASSWORD`: 앱 비밀번호 (공백 제거!)
- `RECIPIENT_EMAIL`: 받을 이메일

### 4. 첫 실행 테스트

Actions 탭 → RSS Monitor → Run workflow

## 📅 자동 실행 스케줄

- 매일 오전 9시 (KST)
- 매일 오후 6시 (KST)

## 🔧 로컬 테스트

```bash
pip install -r requirements.txt

export GMAIL_USER="your.email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"

python multi_site_monitor.py
```

## 📝 라이선스

MIT License

# 다중 사이트 RSS/HTML 모니터

roboco.io와 GeekNews(news.hada.io)에 새 글이 올라오면 자동으로 이메일 알림을 보내주는 시스템입니다.

## 🎯 특징

- ✅ **다중 사이트 지원**: roboco.io + GeekNews 동시 모니터링
- ✅ **하이브리드 방식**: RSS(roboco.io) + HTML 크롤링(hada.io)
- ✅ **GitHub Actions**: 무료로 자동 실행 (월 2,000분)
- ✅ **상태 관리**: 사이트별 중복 알림 방지
- ✅ **깔끔한 이메일**: 사이트별로 구분된 HTML 형식

## 📋 설치 방법

### 1. Gmail 앱 비밀번호 생성

1. https://myaccount.google.com/security 접속
2. 2단계 인증 활성화
3. 앱 비밀번호 생성 (16자리)

### 2. GitHub 저장소 생성

1. https://github.com/new 접속
2. 저장소명 입력
3. Create repository

### 3. GitHub Secrets 설정

Settings → Secrets and variables → Actions에서 추가:

- `GMAIL_USER`: Gmail 주소
- `GMAIL_APP_PASSWORD`: 앱 비밀번호 (공백 제거!)
- `RECIPIENT_EMAIL`: 받을 이메일

### 4. 첫 실행 테스트

Actions 탭 → RSS Monitor → Run workflow

## 📅 자동 실행 스케줄

- 매일 오전 9시 (KST)
- 매일 오후 6시 (KST)

## 🔧 로컬 테스트

```bash
pip install -r requirements.txt

export GMAIL_USER="your.email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"

python multi_site_monitor.py
```

## 📝 라이선스

MIT License
