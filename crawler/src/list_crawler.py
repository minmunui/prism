"""
네이버 뉴스 섹션 크롤러 (Selenium 없이)
requests만 사용하여 여러 페이지의 기사 수집
"""

from datetime import datetime
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time


class NaverNewsSectionCrawler:
    """네이버 뉴스 섹션 크롤러"""

    # 섹션 코드
    SECTIONS = {
        "정치": "100",
        "경제": "101",
        "사회": "102",
        "생활/문화": "103",
        "세계": "104",
        "IT/과학": "105",
        "오피니언": "110",
    }

    def __init__(self, timeout: int = 10):
        """
        Args:
            timeout: 요청 타임아웃 (초)
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

    def fetch_page(self, section_id: str = None, page: int = 1, target_date: Optional[str] = None) -> Optional[List[Dict]]:
        """
        특정 섹션의 특정 페이지 기사 가져오기

        Args:
            section_id: 섹션 코드 (예: '100' 또는 '정치')
            page: 페이지 번호 (1부터 시작)
            target_date: 특정 날짜(YYYYMMDD)로 필터링

        Returns:
            기사 목록 또는 None
        """
        # 섹션명을 코드로 변환
        if section_id in self.SECTIONS:
            section_id = self.SECTIONS[section_id]

        url = "https://news.naver.com/main/list.naver"
        params = {
            "mode": "LSD",
            "mid": "shm",
            "page": page,
            "date": target_date if target_date else datetime.now().strftime('%Y%m%d'),
        }

        if section_id:
            params["sid1"] = section_id

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            articles = self._parse_articles(soup)

            return articles

        except requests.RequestException as e:
            print(f"페이지 {page} 요청 실패: {e}")
            return None

    def _parse_articles(self, soup: BeautifulSoup) -> List[Dict]:
        """기사 목록 파싱"""
        articles = []

        # 헤드라인과 일반 뉴스 리스트 모두 선택
        for dl in soup.select("#main_content > div.list_body.newsflash_body > ul > li > dl"):
            
            
            img_src = dl.select_one("dt.photo img")['src'] if dl.select_one("dt.photo img") else None
            title = dl.select_one("dt:not(.photo) a").text if dl.select_one("dt:not(.photo) a") else None
            link = dl.select_one("dt:not(.photo) a").get("href", "") if dl.select_one("dt:not(.photo) a") else None
            press = dl.select_one("dd span.writing").text if dl.select_one("dd span.writing") else ""
            date = dl.select_one("dd span.date").text if dl.select_one("dd span.date") else ""
            description = dl.select_one("dd span.lede").text if dl.select_one("dd span.lede") else ""

            articles.append(
                {
                    "img_src": img_src,
                    "title": title,
                    "link": link,
                    "press": press,
                    "date": date,
                    "description": description,
                }
            )

        return articles

    def fetch_multiple_pages(
        self, section_id: str = None, max_pages: int = 10, target_date=None, delay: float = 0.5
    ) -> List[Dict]:
        """
        여러 페이지의 기사를 한 번에 수집

        Args:
            section_id: 섹션 코드 (예: '100' 또는 '정치')
            max_pages: 수집할 페이지 수
            target_date: 특정 날짜(YYYYMMDD)로 필터링 (None이면 오늘 날짜)
            delay: 페이지 간 대기 시간 (초, 서버 부담 방지)

        Returns:
            모든 기사 목록
        """
        all_articles = []

        if target_date is None:
            target_date = datetime.now().strftime('%Y%m%d')
            print(f"오늘 날짜로 설정합니다. {target_date}")

        last_articles = []
        for page in range(1, max_pages + 1):
            print(f"페이지 {page}/{max_pages} 수집 중...", end=" ")

            articles = self.fetch_page(section_id, page, target_date=target_date)


            if last_articles and articles == last_articles:
                print("⚠️ 중복 기사 발견, 수집 중단")
                break

            last_articles = articles

            if articles:
                all_articles.extend(articles)
                print(f"✓ {len(articles)}개 기사 수집")
                
            else:
                print("✗ 수집 실패")
                break

            # 서버 부담 방지를 위한 대기
            if page < max_pages:
                time.sleep(delay)

        # 중복 제거 (링크 기준)
        seen = set()
        unique_articles = []
        for article in all_articles:
            if article["link"] not in seen:
                seen.add(article["link"])
                unique_articles.append(article)

        print(f"\n총 {len(unique_articles)}개의 고유 기사를 수집했습니다.")
        return unique_articles

# 사용 예시
if __name__ == "__main__":
    crawler = NaverNewsSectionCrawler()

    # 방법 1: 페이지 단위로 수집
    print("\n[ 방법 1 ] 정치 섹션 5페이지 수집")
    print("-" * 60)
    articles = crawler.fetch_multiple_pages(
        section_id="정치", max_pages=100  # 또는 '100'
    )

    print("\n처음 10개 기사:")
    for i, article in enumerate(articles[:10], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   📰 {article['press']} | ⏰ {article['date']}")
        if article["description"]:
            print(f"   💬 {article['description'][:50]}...")
        print(f"   🔗 {article['link']}")

    with open("naver_economy_news.json", "w", encoding="utf-8") as f:
        import json

        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\n수집 완료! 총 {len(articles)}개")
