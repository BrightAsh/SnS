import requests
from config.settings import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

def search_naver_shopping(query: str, display: int = 1) -> str:
    """
    네이버 쇼핑 API를 사용하여 제품을 검색하고, 가장 첫 번째 상품 링크를 반환합니다.
    :param query: 검색어 (제품명)
    :param display: 한 번에 보여줄 상품 수 (최대 100개)
    :return: 상품 URL 또는 None
    """
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,  # 1개 상품만 반환
    }

    try:
        print(f"[네이버 쇼핑 검색] '{query}' 검색 중...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        items = response.json().get('items', [])
        if items:
            product_url = items[0]['link']  # 첫 번째 상품 URL
            return product_url
        else:
            print("[네이버 쇼핑 검색 결과] 상품 없음")
            return None
    except Exception as e:
        print(f"[네이버 쇼핑 API 오류] {e}")
        return None


if __name__ == "__main__":
    query = "Nike Air Force 1"
    url = search_naver_shopping(query)

    if url:
        print(f"🛍️ 상품 링크: {url}")
    else:
        print("❌ 상품을 찾지 못했습니다.")


