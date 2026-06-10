"""
네이버 오픈 API와 연동하여 다양한 검색 및 트렌드 데이터를 수집하는 모듈입니다.
데이터랩(검색어/쇼핑인사이트 트렌드) 및 일반 서비스 검색(블로그, 뉴스, 카페글, 쇼핑)에 대한
API 요청 처리와 에러 핸들링을 제공합니다.
"""

import requests
import json

class NaverApiClient:
    """
    네이버 오픈 API와 연동하여 데이터를 수집하는 클라이언트 클래스
    """
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        
    def _get_headers(self, is_json: bool = False) -> dict:
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        if is_json:
            headers["Content-Type"] = "application/json"
        return headers

    def _handle_response(self, response: requests.Response):
        """
        API 응답을 처리하고 에러가 발생한 경우 적절한 예외를 발생시킵니다.
        """
        if response.status_code == 200:
            return response.json()
        
        # 에러 핸들링
        try:
            err_data = response.json()
            err_msg = err_data.get("errorMessage", err_data.get("message", "알 수 없는 에러가 발생했습니다."))
            err_code = err_data.get("errorCode", str(response.status_code))
        except Exception:
            err_msg = response.text
            err_code = str(response.status_code)
            
        raise Exception(f"네이버 API 에러 (코드: {err_code}): {err_msg}")

    def test_connection(self) -> bool:
        """
        API 키의 유효성을 검증하기 위한 간단한 블로그 검색 테스트
        """
        url = "https://openapi.naver.com/v1/search/blog.json"
        headers = self._get_headers()
        params = {"query": "테스트", "display": 1}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            self._handle_response(response)
            return True
        except Exception as e:
            raise e

    def get_search_trend(self, start_date: str, end_date: str, time_unit: str, keyword_groups: list, device: str = None, gender: str = None, ages: list = None) -> dict:
        """
        통합 검색어 트렌드 조회 API (POST)
        """
        url = "https://openapi.naver.com/v1/datalab/search"
        headers = self._get_headers(is_json=True)
        
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "keywordGroups": keyword_groups
        }
        if device:
            body["device"] = device
        if gender:
            body["gender"] = gender
        if ages:
            body["ages"] = ages
            
        response = requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), timeout=10)
        return self._handle_response(response)

    def search_blog(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> dict:
        """
        블로그 검색 API (GET)
        """
        url = "https://openapi.naver.com/v1/search/blog.json"
        headers = self._get_headers()
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return self._handle_response(response)

    def search_news(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> dict:
        """
        뉴스 검색 API (GET)
        """
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = self._get_headers()
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return self._handle_response(response)

    def search_cafearticle(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> dict:
        """
        카페글 검색 API (GET)
        """
        url = "https://openapi.naver.com/v1/search/cafearticle.json"
        headers = self._get_headers()
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return self._handle_response(response)

    def search_shopping(self, query: str, display: int = 10, start: int = 1, sort: str = "sim", filter_val: str = None, exclude: str = None) -> dict:
        """
        쇼핑 검색 API (GET)
        """
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = self._get_headers()
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }
        if filter_val:
            params["filter"] = filter_val
        if exclude:
            params["exclude"] = exclude
            
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return self._handle_response(response)

    def get_shopping_trend(self, start_date: str, end_date: str, time_unit: str, category_id: str, keywords: list, device: str = "", gender: str = "", ages: list = None) -> dict:
        """
        쇼핑인사이트 키워드별 트렌드 조회 API (POST)
        """
        url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
        headers = self._get_headers(is_json=True)
        
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "category": category_id,
            "keyword": keywords
        }
        if device:
            body["device"] = device
        if gender:
            body["gender"] = gender
        if ages:
            body["ages"] = ages
            
        response = requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), timeout=10)
        return self._handle_response(response)
