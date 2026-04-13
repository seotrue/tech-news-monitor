#!/usr/bin/env python3
"""
다중 사이트 RSS/HTML 모니터 - 새 글 알림
- roboco.io: RSS 피드 사용
- news.hada.io: HTML 크롤링

실행 환경:
- Python 3.8+
- Gmail SMTP 앱 비밀번호 필요
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import hashlib


class SiteMonitor:
    """사이트 모니터링 기본 클래스"""
    
    def __init__(self, site_name: str, url: str):
        self.site_name = site_name
        self.url = url
    
    def fetch_posts(self) -> List[Dict]:
        """새 글 가져오기 (각 사이트별 구현 필요)"""
        raise NotImplementedError
    
    def generate_post_id(self, post: Dict) -> str:
        """글 고유 ID 생성"""
        # 제목 + URL로 해시 생성
        content = f"{post.get('title', '')}{post.get('link', '')}"
        return hashlib.md5(content.encode()).hexdigest()


class RobocoMonitor(SiteMonitor):
    """roboco.io RSS 모니터"""
    
    def __init__(self):
        super().__init__("ROBOCO", "https://roboco.io/index.xml")
    
    def fetch_posts(self) -> List[Dict]:
        """RSS 피드에서 글 가져오기"""
        feed = feedparser.parse(self.url)
        
        if feed.bozo:
            raise Exception(f"RSS 피드 파싱 실패: {feed.bozo_exception}")
        
        posts = []
        for entry in feed.entries[:10]:  # 최신 10개만
            posts.append({
                'site': self.site_name,
                'title': entry.get('title', '제목 없음'),
                'link': entry.get('link', '#'),
                'date': entry.get('published', '날짜 없음'),
                'summary': entry.get('summary', '')[:200],
            })
        
        return posts


class HadaMonitor(SiteMonitor):
    """news.hada.io HTML 크롤링 모니터"""
    
    def __init__(self):
        super().__init__("GeekNews", "https://news.hada.io/new")
    
    def fetch_posts(self) -> List[Dict]:
        """HTML 크롤링으로 글 가져오기"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(self.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = []
        
        # news.hada.io 구조: 각 글이 특정 패턴으로 나열됨
        # 링크와 제목이 있는 항목 찾기
        items = soup.find_all('a', href=lambda x: x and '/topic?id=' in x)
        
        seen_links = set()
        for item in items[:10]:  # 최신 10개만
            link = item.get('href', '')
            if not link or link in seen_links:
                continue
            
            # 상대 경로를 절대 경로로 변환
            if link.startswith('/'):
                link = f"https://news.hada.io{link}"
            
            seen_links.add(link)
            
            # 제목 추출
            title = item.get_text(strip=True)
            if not title or title.startswith('#'):  # # 제거
                title = title[1:].strip() if title else '제목 없음'
            
            posts.append({
                'site': self.site_name,
                'title': title,
                'link': link,
                'date': '최신',  # hada.io는 상대시간만 표시
                'summary': '',
            })
        
        return posts


class MultiSiteMonitor:
    """다중 사이트 모니터 통합 관리"""
    
    def __init__(
        self,
        state_file: str = "last_checked.json",
        gmail_user: Optional[str] = None,
        gmail_app_password: Optional[str] = None,
        recipient_email: Optional[str] = None
    ):
        self.state_file = Path(state_file)
        self.gmail_user = gmail_user
        self.gmail_app_password = gmail_app_password
        self.recipient_email = recipient_email or gmail_user
        
        # 모니터링할 사이트들
        self.monitors = [
            RobocoMonitor(),
            HadaMonitor(),
        ]
    
    def load_last_checked(self) -> Dict:
        """마지막 확인 상태 로드"""
        if not self.state_file.exists():
            return {}
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_last_checked(self, state: Dict):
        """마지막 확인 상태 저장"""
        state['last_check_time'] = datetime.now().isoformat()
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def get_new_posts(self, site_name: str, posts: List[Dict], last_post_ids: List[str]) -> List[Dict]:
        """새 글 필터링"""
        if not last_post_ids:
            # 첫 실행: 최신 1개만 반환
            return posts[:1] if posts else []
        
        new_posts = []
        for post in posts:
            # 글 ID 생성
            post_id = self._generate_post_id(post)
            
            if post_id not in last_post_ids:
                new_posts.append(post)
            else:
                break  # 이미 확인한 글을 만나면 중단
        
        return new_posts
    
    def _generate_post_id(self, post: Dict) -> str:
        """글 고유 ID 생성"""
        content = f"{post.get('title', '')}{post.get('link', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def send_email(self, all_new_posts: Dict[str, List[Dict]]):
        """이메일 발송"""
        # 새 글이 있는지 확인
        total_count = sum(len(posts) for posts in all_new_posts.values())
        
        if total_count == 0:
            print("📭 새 글이 없습니다.")
            return
        
        # 이메일 본문 생성
        html_content = self._create_email_html(all_new_posts)
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🆕 새 글 {total_count}개 업데이트!'
        msg['From'] = self.gmail_user
        msg['To'] = self.recipient_email
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Gmail SMTP 발송
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.gmail_user, self.gmail_app_password)
                smtp.send_message(msg)
            print(f"✅ 이메일 발송 완료: 총 {total_count}개 새 글")
        except Exception as e:
            print(f"❌ 이메일 발송 실패: {e}")
            raise  # 상위에서 catch하여 처리
    
    def _create_email_html(self, all_new_posts: Dict[str, List[Dict]]) -> str:
        """이메일 HTML 생성"""
        
        # 사이트별 색상
        site_colors = {
            'ROBOCO': '#4CAF50',
            'GeekNews': '#2196F3',
        }
        
        sections_html = ""
        
        for site_name, posts in all_new_posts.items():
            if not posts:
                continue
            
            color = site_colors.get(site_name, '#666')
            
            posts_html = ""
            for post in posts:
                title = post.get('title', '제목 없음')
                link = post.get('link', '#')
                date = post.get('date', '날짜 없음')
                summary = post.get('summary', '')
                
                # 요약이 너무 길면 자르기
                if summary and len(summary) > 200:
                    summary = summary[:200] + '...'
                
                posts_html += f"""
                <div style="margin-bottom: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 4px;">
                    <h3 style="margin-top: 0; margin-bottom: 5px;">
                        <a href="{link}" style="color: #333; text-decoration: none;">{title}</a>
                    </h3>
                    <p style="color: #666; font-size: 13px; margin: 5px 0;">📅 {date}</p>
                    {f'<p style="color: #444; line-height: 1.5; margin: 10px 0;">{summary}</p>' if summary else ''}
                    <a href="{link}" style="color: {color}; text-decoration: none; font-size: 14px;">
                        전체 글 보기 →
                    </a>
                </div>
                """
            
            sections_html += f"""
            <div style="margin-bottom: 40px;">
                <h2 style="color: {color}; border-bottom: 3px solid {color}; padding-bottom: 10px; margin-bottom: 20px;">
                    {site_name} ({len(posts)}개)
                </h2>
                {posts_html}
            </div>
            """
        
        html = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #eee; margin-bottom: 30px;">
                <h1 style="color: #333; margin: 0;">🔔 새 글 알림</h1>
                <p style="color: #666; margin: 10px 0 0 0;">roboco.io & GeekNews</p>
            </div>
            
            {sections_html}
            
            <hr style="margin-top: 40px; border: none; border-top: 1px solid #ddd;">
            <p style="color: #999; font-size: 12px; text-align: center; margin-top: 20px;">
                자동 발송 이메일 | GitHub Actions
            </p>
        </body>
        </html>
        """
        return html
    
    def run(self):
        """메인 실행 로직"""
        print(f"🔍 사이트 모니터링 시작...")
        
        # 1. 이전 상태 로드
        last_state = self.load_last_checked()
        
        # 2. 각 사이트별로 새 글 확인
        all_new_posts = {}
        new_state = {}
        
        for monitor in self.monitors:
            print(f"📡 {monitor.site_name} 확인 중...")
            
            try:
                # 최신 글 가져오기
                posts = monitor.fetch_posts()
                
                if not posts:
                    print(f"  ⚠️  {monitor.site_name}: 글이 없음")
                    continue
                
                # 이전에 확인한 글 ID 목록
                last_post_ids = last_state.get(monitor.site_name, [])
                
                # 새 글 필터링
                new_posts = self.get_new_posts(monitor.site_name, posts, last_post_ids)
                
                if new_posts:
                    all_new_posts[monitor.site_name] = new_posts
                    print(f"  ✨ {monitor.site_name}: 새 글 {len(new_posts)}개 발견!")
                else:
                    print(f"  📭 {monitor.site_name}: 새 글 없음")
                
                # 현재 글들의 ID 저장 (최신 10개)
                current_post_ids = [self._generate_post_id(post) for post in posts[:10]]
                new_state[monitor.site_name] = current_post_ids
                
            except Exception as e:
                print(f"  ❌ {monitor.site_name} 확인 실패: {e}")
                # 실패해도 계속 진행
                continue
        
        # 3. 이메일 발송
        if all_new_posts:
            try:
                self.send_email(all_new_posts)
            except Exception as e:
                print(f"⚠️  이메일 발송 실패했지만 상태는 저장합니다: {e}")
        else:
            print("📭 모든 사이트에 새 글이 없습니다.")
        
        # 4. 상태 저장 (새 글 유무와 관계없이 항상 저장)
        if new_state:
            self.save_last_checked(new_state)
            print(f"💾 상태 저장 완료: {len(new_state)}개 사이트")


if __name__ == "__main__":
    import os
    
    # 환경 변수에서 이메일 정보 가져오기
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    if not gmail_user or not gmail_app_password:
        print("❌ 환경 변수 설정 필요:")
        print("   GMAIL_USER=your.email@gmail.com")
        print("   GMAIL_APP_PASSWORD=your-app-specific-password")
        exit(1)
    
    monitor = MultiSiteMonitor(
        gmail_user=gmail_user,
        gmail_app_password=gmail_app_password,
        recipient_email=recipient_email
    )
    
    monitor.run()