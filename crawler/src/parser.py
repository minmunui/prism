import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional


class NaverNewsParser:
    """네이버 뉴스 파싱 클래스"""
    
    # CSS 셀렉터 상수
    SELECTORS = {
        'title': '#title_area > span',
        'content': '#dic_area',
        'created_at': '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_journalist > div.media_end_head_journalist_info > div.media_end_head_info_datestamp > div > div > div:nth-child(1) > span',
        'modified_at': '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_journalist > div.media_end_head_journalist_info > div.media_end_head_info_datestamp > div > div > div:nth-child(2) > span',
        'author': '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_journalist > div.media_end_head_journalist_info > div.media_end_head_journalist_name_area > a',
        'media': '#JOURNALIST_CARD_LIST > div > div > div.media_journalistcard_intro > div > div > div.media_journalistcard_summary_info > div > span',
        'images': '#dic_area img'
    }
    
    def __init__(self, timeout: int = 10):
        """
        Args:
            timeout: 요청 타임아웃 (초)
        """
        self.timeout = timeout
    
    def fetch_html(self, url: str) -> Optional[str]:
        """URL에서 HTML을 가져옵니다."""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"요청 실패: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """제목 추출"""
        element = soup.select_one(self.SELECTORS['title'])
        return element.text.strip() if element else ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """본문 추출 (이미지 태그는 '<이미지>'로 대체)"""
        content_area = soup.select_one(self.SELECTORS['content'])
        if not content_area:
            return ''
        
        # <br/> 태그를 줄바꿈으로, <img> 태그를 '<이미지>'로 변환
        content_html = content_area.decode_contents()
        content_html = content_html.replace('<br/>', '\n')
        content_html = re.sub(r'<img[^>]*>', '<이미지>', content_html)
        
        return BeautifulSoup(content_html, 'html.parser').text.strip()
    
    def _extract_dates(self, soup: BeautifulSoup) -> Dict[str, str]:
        """작성일, 수정일 추출"""
        created_element = soup.select_one(self.SELECTORS['created_at'])
        modified_element = soup.select_one(self.SELECTORS['modified_at'])
        
        return {
            'created_at': created_element.text.strip() if created_element else '',
            'modified_at': modified_element.text.strip() if modified_element else ''
        }
    
    def _extract_author(self, soup: BeautifulSoup) -> Dict[str, str]:
        """기자 정보 추출"""
        author_element = soup.select_one(self.SELECTORS['author'])
        
        return {
            'author': author_element.text.strip() if author_element else '',
            'author_link': author_element.get('href', '') if author_element else ''
        }
    
    def _extract_media(self, soup: BeautifulSoup) -> str:
        """언론사 추출"""
        media_element = soup.select_one(self.SELECTORS['media'])
        return media_element.text.strip() if media_element else ''
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """이미지 목록 추출"""
        img_tags = soup.select(self.SELECTORS['images'])
        images = []
        
        for img in img_tags:
            src = img.get('data-src') or img.get('src')
            alt = img.get('alt', '')
            
            if src:
                images.append({'src': src, 'alt': alt})
        
        return images
    
    def parse_url(self, url: str) -> Optional[Dict]:
        """
        네이버 뉴스 URL을 파싱하여 기사 정보를 반환합니다.
        
        Args:
            url: 네이버 뉴스 기사 URL
            
        Returns:
            기사 정보 딕셔너리 또는 실패 시 None
        """
        html = self.fetch_html(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 각 정보 추출
        article_data = {
            'title': self._extract_title(soup),
            'content': self._extract_content(soup),
            **self._extract_dates(soup),
            **self._extract_author(soup),
            'media': self._extract_media(soup),
            'link': url,
            'images': self._extract_images(soup)
        }
        
        return article_data


# 사용 예시
if __name__ == '__main__':
    url = 'https://n.news.naver.com/mnews/article/661/0000063068'
    
    parser = NaverNewsParser()
    result = parser.parse_url(url)
    
    if result:
        print(f"제목: {result['title']}")
        print(f"작성일: {result['created_at']}")
        print(f"수정일: {result['modified_at']}")
        print(f"기자: {result['author']}")
        print(f"언론사: {result['media']}")
        print(f"이미지 수: {len(result['images'])}")
        print(f"\n본문:\n{result['content'][:200]}...")
    else:
        print("파싱 실패")
