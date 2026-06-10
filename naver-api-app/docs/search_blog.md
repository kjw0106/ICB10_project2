# 네이버 검색 - 블로그 검색 API 명세

네이버 블로그의 글들을 검색하여 결과를 반환받을 수 있는 비로그인 방식의 오픈 API입니다.

## 1. 개요 및 한도
* **설명**: 네이버 블로그 검색 결과를 JSON 또는 XML 형식으로 반환합니다.
* **하루 호출 한도**: 검색 API 전체 통합하여 하루 총 25,000회 제한
* **방식**: 비로그인 방식 (HTTP Header에 Client ID, Secret 전송)

## 2. API 스펙
* **요청 URL**: 
  * JSON 포맷: `https://openapi.naver.com/v1/search/blog.json`
  * XML 포맷: `https://openapi.naver.com/v1/search/blog.xml`
* **프로토콜**: HTTPS
* **HTTP Method**: GET

### 요청 헤더 (HTTP Headers)
```http
X-Naver-Client-Id: {발급받은 Client ID}
X-Naver-Client-Secret: {발급받은 Client Secret}
```

### 요청 파라미터 (Query String)
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
| :--- | :--- | :---: | :---: | :--- |
| `query` | String | Y | - | 검색어. 반드시 **UTF-8**로 인코딩해야 합니다. |
| `display` | Integer | N | 10 | 한 번에 표시할 검색 결과 개수 (최소 10, 최대 100) |
| `start` | Integer | N | 1 | 검색 시작 위치 (최소 1, 최대 1000) |
| `sort` | String | N | sim | 검색 결과 정렬 방법<br>- `sim`: 정확도순 내림차순 정렬<br>- `date`: 날짜순 내림차순 정렬 |

### 응답 결과 (Response Fields - JSON 기준)
* **성공 시**: HTTP Status 200 (JSON 형식 반환)
* **주요 응답 필드**:
  * `lastBuildDate`: 검색 결과를 생성한 시간 (RFC 822 형식)
  * `total`: 총 검색 결과 개수
  * `start`: 검색 시작 위치
  * `display`: 표시할 검색 결과 개수
  * `items`: 개별 검색 결과 아이템 배열
    * `title`: 블로그 포스트 제목 (검색 키워드와 매칭된 단어는 `<b>` 태그로 감싸져 제공됨)
    * `link`: 블로그 포스트 상세 URL
    * `description`: 포스트 내용 본문 요약 (검색 키워드와 매칭된 단어는 `<b>` 태그 포함)
    * `bloggername`: 블로그 이름
    * `bloggerlink`: 블로그 홈 URL
    * `postdate`: 블로그 글 작성일 (예: `20161208` 형태)

## 3. 에러 코드
| 에러 코드 | HTTP 상태 코드 | 에러 메시지 및 설명 |
| :---: | :---: | :--- |
| **SE01** | 400 | Incorrect query request (잘못된 쿼리 요청) |
| **SE02** | 400 | Invalid display value (허용 범위 1~100을 벗어난 display 값) |
| **SE03** | 400 | Invalid start value (허용 범위 1~1000을 벗어난 start 값) |
| **SE04** | 400 | Invalid sort value (부적절한 sort 정렬 파라미터 값) |
| **SE05** | 404 | Invalid search api (존재하지 않는 검색 API 경로) |
| **SE06** | 400 | Malformed encoding (검색어가 UTF-8 형식이 아님) |
| **SE99** | 500 | System Error (네이버 내부 시스템 서버 에러) |

## 4. 요청 예시 (cURL)
```bash
curl "https://openapi.naver.com/v1/search/blog.json?query=%EB%A6%AC%EB%B7%B0&display=10&start=1&sort=sim" \
  -H "X-Naver-Client-Id: YOUR_CLIENT_ID" \
  -H "X-Naver-Client-Secret: YOUR_CLIENT_SECRET"
```
