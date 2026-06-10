# 네이버 데이터랩 - 쇼핑인사이트(쇼핑 트렌드) API 명세

네이버 통합검색의 쇼핑 영역 및 네이버쇼핑에서의 클릭 추이를 카테고리별/키워드별로 조회할 수 있는 비로그인 방식의 오픈 API입니다.

## 1. 개요 및 한도
* **설명**: 쇼핑 분야 내 기기별, 성별, 연령별 트렌드 및 분야 내 키워드별 검색 클릭 트렌드를 조회합니다.
* **하루 호출 한도**: 1,000회 (Client ID당 집계)
* **방식**: 비로그인 방식 (HTTP Header에 Client ID, Secret 전송)

## 2. API 스펙 (키워드별 트렌드 조회 기준)
* **요청 URL**: `https://openapi.naver.com/v1/datalab/shopping/category/keywords`
* **프로토콜**: HTTPS
* **HTTP Method**: POST
* **Content-Type**: `application/json`

### 요청 헤더 (HTTP Headers)
```http
X-Naver-Client-Id: {발급받은 Client ID}
X-Naver-Client-Secret: {발급받은 Client Secret}
Content-Type: application/json
```

### 요청 파라미터 (JSON Body)
| 파라미터 | 타입 | 필수 | 설명 |
| :--- | :--- | :---: | :--- |
| `startDate` | string | Y | 조회 기간 시작 날짜 (`yyyy-mm-dd` 형식, 2017-08-01부터 조회 가능) |
| `endDate` | string | Y | 조회 기간 종료 날짜 (`yyyy-mm-dd` 형식) |
| `timeUnit` | string | Y | 구간 단위 (`date`: 일간, `week`: 주간, `month`: 월간) |
| `category` | string | Y | 쇼핑 분야 코드 (예: 패션의류는 `50000000`) |
| `keyword` | array | Y | 검색 키워드 그룹 이름과 검색 키워드 쌍의 배열 (최대 5개) |
| `keyword[].name` | string | Y | 검색 키워드 그룹 이름 |
| `keyword[].param` | array | Y | 비교할 검색어 (1개만 설정할 수 있음) |
| `device` | string | N | 기기 범위 (설정 안 함: 전체, `pc`: PC, `mo`: 모바일) |
| `gender` | string | N | 성별 (설정 안 함: 전체, `m`: 남성, `f`: 여성) |
| `ages` | array | N | 연령대 배열 (설정 안 함: 전체, `10`: 10대 ... `60`: 60대 이상) |

### 응답 결과 (Response Fields)
* **성공 시**: HTTP Status 200 (JSON 형식 반환)
* **응답 필드**:
  * `startDate`, `endDate`, `timeUnit`
  * `results`: 검색 결과 키워드 그룹 배열
    * `title`: 검색 키워드 그룹 이름
    * `keyword`: 검색 키워드 배열
    * `data`: 상세 클릭 트렌드 데이터 배열
      * `period`: 해당 구간 시작일 (`yyyy-mm-dd`)
      * `ratio`: 기간 내 최대 클릭량을 100으로 둔 **상대적인 클릭량 비율 (Float)**

## 3. 카테고리 코드 예시
* 패션의류: `50000000`
* 화장품/미용: `50000002`
* 디바이스/가전: 등 (네이버쇼핑 URL 내 `cat_id` 파라미터 값 참고)

## 4. 요청 예시 (cURL)
```bash
curl https://openapi.naver.com/v1/datalab/shopping/category/keywords \
  -H "X-Naver-Client-Id: YOUR_CLIENT_ID" \
  -H "X-Naver-Client-Secret: YOUR_CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "2017-08-01",
    "endDate": "2017-09-30",
    "timeUnit": "month",
    "category": "50000000",
    "keyword": [
      {"name": "정장", "param": ["정장"]},
      {"name": "비즈니스 캐주얼", "param": ["비지니스 캐주얼"]}
    ],
    "device": "",
    "gender": "",
    "ages": []
  }'
```
