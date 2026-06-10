# 네이버 검색 - 쇼핑 검색 API 명세

네이버 쇼핑 상품 리스트 및 가격 비교 데이터를 검색하여 결과를 반환받을 수 있는 비로그인 방식의 오픈 API입니다.

## 1. 개요 및 한도
* **설명**: 네이버 쇼핑에서 특정 상품을 검색하여 매칭된 상품들의 목록을 JSON 또는 XML 형식으로 반환합니다.
* **하루 호출 한도**: 검색 API 전체 통합하여 하루 총 25,000회 제한
* **방식**: 비로그인 방식 (HTTP Header에 Client ID, Secret 전송)

## 2. API 스펙
* **요청 URL**: 
  * JSON 포맷: `https://openapi.naver.com/v1/search/shop.json`
  * XML 포맷: `https://openapi.naver.com/v1/search/shop.xml`
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
| `sort` | String | N | sim | 검색 결과 정렬 방법<br>- `sim`: 정확도순 내림차순 정렬<br>- `date`: 날짜순 내림차순 정렬<br>- `asc`: 가격 낮은 순 정렬<br>- `dsc`: 가격 높은 순 정렬 |
| `filter` | String | N | - | 검색 결과 필터 타입<br>- `naverpay`: 네이버페이 연동 상품만 필터링 |
| `exclude` | String | N | - | 검색 결과 제외 상품 타입 (`{option}:{option}` 형태로 설정)<br>- `used`: 중고 상품 제외<br>- `rental`: 렌탈 상품 제외<br>- `cbshop`: 해외직구/구매대행 상품 제외 |

### 응답 결과 (Response Fields - JSON 기준)
* **성공 시**: HTTP Status 200 (JSON 형식 반환)
* **주요 응답 필드**:
  * `lastBuildDate`: 검색 결과를 생성한 시간
  * `total`: 총 검색 결과 개수
  * `start`: 검색 시작 위치
  * `display`: 표시할 검색 결과 개수
  * `items`: 개별 검색 결과 상품 배열
    * `title`: 상품 이름 (검색어 매칭 단어는 `<b>` 태그 포함)
    * `link`: 상품 상세 URL
    * `image`: 상품 섬네일 이미지 URL
    * `lprice`: 최저가 (최저가 정보가 없으면 `0` 반환. 가격 비교 정보가 없으면 일반 판매가)
    * `hprice`: 최고가 (최고가 정보가 없거나 가격 비교 정보가 없으면 `0` 반환)
    * `mallName`: 판매 쇼핑몰 이름 (쇼핑몰명이 없으면 '네이버' 반환)
    * `productId`: 네이버 쇼핑 상품 ID (상대고유번호)
    * `productType`: 상품 유형 코드 (1~12)
    * `maker`: 제조사
    * `brand`: 브랜드
    * `category1`: 대분류 카테고리
    * `category2`: 중분류 카테고리
    * `category3`: 소분류 카테고리
    * `category4`: 세분류 카테고리

### 상품군 타입 (`productType`) 코드 세부 사항
| 상품군 | 상품 종류 | 코드값 |
| :--- | :--- | :---: |
| **일반상품** | 가격비교 상품 | `1` |
| | 가격비교 비매칭 일반상품 | `2` |
| | 가격비교 매칭 일반상품 | `3` |
| **중고상품** | 가격비교 상품 | `4` |
| | 가격비교 비매칭 일반상품 | `5` |
| | 가격비교 매칭 일반상품 | `6` |
| **단종상품** | 가격비교 상품 | `7` |
| | 가격비교 비매칭 일반상품 | `8` |
| | 가격비교 매칭 일반상품 | `9` |
| **판매예정** | 가격비교 상품 | `10` |
| | 가격비교 비매칭 일반상품 | `11` |
| | 가격비교 매칭 일반상품 | `12` |

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
curl "https://openapi.naver.com/v1/search/shop.json?query=%EC%A3%BC%EC%8B%9D&display=10&start=1&sort=sim&exclude=used:rental" \
  -H "X-Naver-Client-Id: YOUR_CLIENT_ID" \
  -H "X-Naver-Client-Secret: YOUR_CLIENT_SECRET"
```
