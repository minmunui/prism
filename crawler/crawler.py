from src.list_crawler import NaverNewsSectionCrawler
from src.parser import NaverNewsParser

def crawl_and_parse(section_id: str, max_pages: int):
    crawler = NaverNewsSectionCrawler()
    parser = NaverNewsParser()
    
    articles = crawler.fetch_multiple_pages(section_id=section_id, max_pages=max_pages)
    
    detailed_articles = []
    for idx, article in enumerate(articles, 1):
        parsed_article = parser.parse_url(article['link'])
        if parsed_article:
            detailed_articles.append(parsed_article)
            print(f"상세 파싱 완료 {idx}/{len(articles)} : {parsed_article['title']}")

    return detailed_articles

# 사용 예시
if __name__ == "__main__":
    articles = crawl_and_parse(None, 1000)
    
    with open('detailed_articles.json', 'w', encoding='utf-8') as f:
        import json
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"총 {len(articles)}개의 상세 기사를 저장했습니다.")