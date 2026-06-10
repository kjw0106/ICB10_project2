# 네이버 데이터랩 - 통합 검색어 트렌드 API 명세

네이버 데이터랩의 검색어 트렌드 데이터를 조회할 수 있는 비로그인 방식의 오픈 API입니다.

## 1. 개요 및 한도
* **설명**: 네이버 통합검색 내에서 특정 검색 주제어들의 검색량 추이를 JSON 형식으로 받아올 수 있습니다.
* **하루 호출 한도**: 1,000회 (Client ID당 집계)
* **방식**: 비로그인 방식 (HTTP Header에 Client ID, Secret 전송)

## 2. API 스펙
* **요청 URL**: `https://openapi.naver.com/v1/datalab/search`
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
| `startDate` | string | Y | 조회 기간 시작 날짜 (`yyyy-mm-dd` 형식, 2016-01-01부터 조회 가능) |
| `endDate` | string | Y | 조회 기간 종료 날짜 (`yyyy-mm-dd` 형식) |
| `timeUnit` | string | Y | 구간 단위 (`date`: 일간, `week`: 주간, `month`: 월간) |
| `keywordGroups` | array | Y | 주제어 및 검색어 그룹 설정 (최대 5개 그룹) |
| `keywordGroups[].groupName` | string | Y | 주제어 (그룹을 대표하는 이름) |
| `keywordGroups[].keywords` | array | Y | 주제어 그룹에 속하는 연관 검색어 배열 (최대 20개) |
| `device` | string | N | 검색 기기 범위 (설정 안 함: 전체, `pc`: PC, `mo`: 모바일) |
| `gender` | string | N | 검색자 성별 (설정 안 함: 전체, `m`: 남성, `f`: 여성) |
| `ages` | array | N | 검색자 연령대 배열 (설정 안 함: 전체, `1`: 0~12세 ... `11`: 60세 이상) |

### 응답 결과 (Response Fields)
* **성공 시**: HTTP Status 200 (JSON 형식 반환)
* **응답 필드**:
  * `startDate`: 조회 시작일
  * `endDate`: 조회 종료일
  * `timeUnit`: 구간 단위
  * `results`: 검색 결과 그룹 배열
    * `title`: 주제어 이름
    * `keywords`: 포함된 키워드 배열
    * `data`: 상세 트렌드 데이터 배열
      * `period`: 해당 구간 시작일 (`yyyy-mm-dd`)
      * `ratio`: 기간 내 최대 검색량을 100으로 둔 **상대적인 검색량 비율 (Float)**

## 3. 에러 코드
* **400 Bad Request**: 파라미터 구성 오류, 날짜 형식 포맷 불일치 등
* **403 Forbidden**: 애플리케이션 설정에서 "데이터랩 (검색어트렌드)" API가 등록되어 있지 않은 경우 발생
* **500 Internal Server Error**: 네이버 서버 내부 시스템 에러

## 4. 요청 예시 (cURL)
```bash
curl https://openapi.naver.com/v1/datalab/search \
  -H "X-Naver-Client-Id: YOUR_CLIENT_ID" \
  -H "X-Naver-Client-Secret: YOUR_CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "2017-01-01",
    "endDate": "2017-04-30",
    "timeUnit": "month",
    "keywordGroups": [
      {
        "groupName": "한글",
        "keywords": ["한글", "korean"]
      },
      {
        "groupName": "영어",
        "keywords": ["영어", "english"]
      }
    ],
    "device": "pc",
    "ages": ["1", "2"],
    "gender": "f"
  }'
```
