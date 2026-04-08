# 기술 뉴스 모니터

roboco.io와 GeekNews(news.hada.io)에 새 글이 올라오면 자동으로 이메일 알림을 보내주는 시스템입

## 특징

-  **다중 사이트 지원**: roboco.io + GeekNews 동시 모니터링
-  **하이브리드 방식**: RSS(roboco.io) + HTML 크롤링(hada.io)
-  **GitHub Actions**: 무료로 자동 실행 (월 2,000분)
-  **상태 관리**: 사이트별 중복 알림 방지
-  **깔끔한 이메일**: 사이트별로 구분된 HTML 형식


### 1. Gmail 앱 비밀번호 생성

1. https://myaccount.google.com/security 접속
2. 2단계 인증 활성화
3. 앱 비밀번호 생성 (16자리)

### 2. GitHub Secrets

Settings → Secrets and variables → Actions

- `GMAIL_USER` - 보낼 Gmail
- `GMAIL_APP_PASSWORD` - 앱 비밀번호 (공백 빼고)
- `RECIPIENT_EMAIL` - 받을 메일

### 3. 실행

Actions 탭 가서 Run workflow 누르면 됨.

## 로컬 실행

```bash
pip install -r requirements.txt

export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@gmail.com"

python multi_site_monitor.py
```

## 커스텀

- 사이트 추가: `multi_site_monitor.py`에서 `RSS_FEEDS` 딕셔너리 수정
- 실행 시간: `.github/workflows/rss_monitor.yml`의 cron 수정 (지금은 9시, 18시)
