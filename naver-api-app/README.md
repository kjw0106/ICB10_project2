# 📱 네이버 API 연동 데이터 시각화 대시보드 (naver-api-app)

이 프로젝트는 네이버 오픈 API(검색어 트렌드, 쇼핑 트렌드 및 서비스 검색 API)를 활용하여 데이터를 수집하고 시각화하는 Streamlit 대시보드 웹 애플리케이션입니다.

---

## 🔗 Streamlit 접속 주소
- 🚀 **Streamlit Cloud 배포 주소**: [https://icb10project2-pdmcyvdabv6nkcglkqvrjr.streamlit.app/](https://icb10project2-pdmcyvdabv6nkcglkqvrjr.streamlit.app/)
- 💻 **로컬 접속 주소**: [http://localhost:8501](http://localhost:8501)
- 🌐 **네트워크 접속 주소**: http://192.168.55.161:8501

---

## 🛠️ 최근 작업 내역 (Updated: 2026-06-13)

### 1. Git post-commit 훅 설정 및 자동 푸시 기능 연동
* **목적**: 변경사항 발생 시 일일이 푸시를 수행하지 않고, 커밋 성공 시점에 원격 저장소로 즉시 동기화되도록 설정.
* **적용 파일**: `.git/hooks/post-commit` (쉘 스크립트 작성)
* **결과**: `git commit` 수행 시 원격 저장소(`origin/main`)로 자동 푸시가 트리거되며, 테스트 브랜치 및 메인 브랜치에서 안정적으로 작동함을 확인하였습니다.

### 2. Streamlit 대시보드 로컬 실행 및 클라우드 배포
* **가상환경 연동**: 최상단 공통 가상환경 `.venv`를 활용하여 `requirements.txt`에 기록된 의존성 패키지(Streamlit, Pandas, Plotly 등)를 설치하고 실행 환경을 구성했습니다.
* **백그라운드 구동**: `--server.headless true` 옵션을 인가하여 백그라운드 태스크로 구동하였으며, 사용자가 안내해주신 원격 클라우드 배포 주소와의 연동을 완료하였습니다.

### 3. 네이버 API 수집 및 분석 대시보드 기능 구현 현황
현재 대시보드는 총 6가지 영역에 대해 Plotly 기반의 인터랙티브 분석을 수행하고 있습니다.
* **🏠 홈 & API 연결 확인**: 네이버 개발자 센터에서 발급받은 API 키의 유효성을 실시간으로 확인하고 API 접근 권한 상태를 검증합니다.
* **📈 통합 검색어 트렌드**: 최대 5개 검색 키워드에 대해 조회 기간 동안의 일자별 네이버 상대 검색량 비율 트렌드를 Plotly 라인 차트로 비교 분석하고 요약 지표를 제공합니다.
* **🛍️ 쇼핑 상품 분석**: 특정 키워드의 쇼핑 검색 결과 데이터를 수집하여 가격 분포(히스토그램), 브랜드 점유율 및 제조사 비율(파이 차트)을 다각도로 시각화합니다.
* **📝 블로그 반응 분석**: 최신 블로그 포스트의 검색 결과 추세, 핵심 유입 키워드 노출 현황을 통해 사용자 반응 및 여론 트렌드를 모니터링합니다.
* **☕ 카페글 반응 분석**: 네이버 카페 검색글의 발생 빈도와 작성 트렌드를 분석하여 커뮤니티 내부의 여론 집중도를 분석합니다.
* **📰 뉴스 보도 분석**: 주요 언론사들의 관련 기사 보도 강도와 시계열 트렌드를 수집하여 언론 미디어의 관심 흐름을 시각화합니다.
* **🛒 쇼핑 트렌드 분석**: 네이버 쇼핑인사이트 오픈 API를 활용하여 지정 카테고리 내 핵심 키워드별 클릭률 변화를 모니터링합니다.

---

## 📂 프로젝트 구조

```
naver-api-app/
├── src/
│   ├── app.py            # Streamlit 메인 시각화 애플리케이션
│   └── api_client.py     # 네이버 오픈 API 연동용 SDK 클라이언트
├── docs/                 # 네이버 API 스펙 명세서 마크다운 파일 모음
│   ├── datalab_search.md
│   ├── datalab_shopping.md
│   └── ...
├── data/                 # API 호출 결과 데이터 저장 디렉토리 (비어있음)
├── report/               # 데이터 분석 보고서 산출물 디렉토리 (비어있음)
├── images/               # 이미지 자산 디렉토리
├── requirements.txt      # 프로젝트 패키지 의존성 파일
├── .env                  # 네이버 API Client ID/Secret 설정 파일
└── README.md             # 프로젝트 개요 및 실행 정보 (본 파일)
```

---

## 🚀 로컬 실행 방법

1. **가상환경 활성화 (Powershell 기준)**:
   ```powershell
   .venv\Scripts\activate
   ```

2. **패키지 설치**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Streamlit 서버 실행**:
   ```bash
   streamlit run naver-api-app/src/app.py
   ```
