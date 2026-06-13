"""
네이버 오픈 API 수집 및 분석을 위한 Streamlit 대시보드 메인 애플리케이션 파일입니다.
사이드바를 통해 API Key 및 검색 필터를 입력받고, 6가지 분석 페이지와 홈 화면을 제공합니다.
모든 시각화는 Plotly를 활용하여 인터랙티브하게 구성되어 있습니다.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from dotenv import load_dotenv

# 상대경로 임포트를 위한 sys.path 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api_client import NaverApiClient

# .env 파일 경로 탐색 (.env가 src 상위 폴더 또는 워크스페이스 루트에 있을 수 있음)
dotenv_path_local = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
dotenv_path_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')

if os.path.exists(dotenv_path_local):
    load_dotenv(dotenv_path_local, override=True)
elif os.path.exists(dotenv_path_root):
    load_dotenv(dotenv_path_root, override=True)
else:
    load_dotenv(override=True)

# 노르딕 모던(Nord) 스타일 디자인 컬러 팔레트 정의
NORD_PALETTE = ["#88C0D0", "#81A1C1", "#5E81AC", "#8FBCBB", "#BF616A", "#D08770", "#EBCB8B", "#A3BE8C", "#B48EAD"]
NORD_BLUE = "#81A1C1"
NORD_CONTINUOUS = ["#E5E9F0", "#81A1C1", "#5E81AC"]

# 페이지 기본 설정
st.set_page_config(
    page_title="네이버 API 통합 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- 세션 상태 초기화 & API 정보 로드 -----------------
# Streamlit Secrets에서 먼저 키 값을 가져온 뒤, 없으면 환경 변수(.env)에서 가져옵니다.
env_client_id = st.secrets.get("NAVER_CLIENT_ID", os.environ.get("NAVER_CLIENT_ID", "")).strip()
env_client_secret = st.secrets.get("NAVER_CLIENT_SECRET", os.environ.get("NAVER_CLIENT_SECRET", "")).strip()

# 세션 상태에 클라이언트 정보 등록
if "client_id" not in st.session_state:
    st.session_state["client_id"] = env_client_id
if "client_secret" not in st.session_state:
    st.session_state["client_secret"] = env_client_secret

# ----------------- 사이드바 (공통 입력 영역) -----------------
# --- 🔑 API & 테마 설정 아코디언 ---
with st.sidebar.expander("🔑 API & 테마 설정", expanded=False):
    if env_client_id and env_client_secret:
        st.success("✅ `.env` 키 로드 완료")
        masked_id = env_client_id[:4] + "*" * (len(env_client_id) - 4) if len(env_client_id) > 4 else "****"
        st.caption(f"연동 ID: {masked_id}")
        st.session_state["client_id"] = env_client_id
        st.session_state["client_secret"] = env_client_secret
    else:
        st.warning("⚠️ `.env` 키 미로드 (수동 입력 필요)")
        st.info("프로젝트 폴더 내 `.env` 파일에 키를 저장하면 편리합니다.")
        client_id_input = st.text_input(
            "Client ID", 
            value=st.session_state["client_id"],
            type="password",
            help="네이버 개발자 센터에서 발급받은 Client ID를 입력하세요."
        )
        client_secret_input = st.text_input(
            "Client Secret", 
            value=st.session_state["client_secret"],
            type="password",
            help="네이버 개발자 센터에서 발급받은 Client Secret을 입력하세요."
        )
        st.session_state["client_id"] = client_id_input.strip()
        st.session_state["client_secret"] = client_secret_input.strip()
        
    st.markdown("---")
    theme_choice = st.selectbox(
        "차트 그래픽 테마",
        ["Nord Modern", "Cyberpunk Dark", "Light Clean", "Warm Autumn"],
        help="차트에 입힐 컬러 팔레트와 스타일을 설정합니다."
    )

# --- ⚙️ 공통 전처리 설정 아코디언 ---
with st.sidebar.expander("⚙️ 공통 전처리 설정", expanded=False):
    exclude_kws_input = st.text_input(
        "제외 키워드 (쉼표 구분)",
        value="",
        help="제목이나 내용에 포함될 시 분석에서 제외할 키워드를 입력하세요."
    )
    exclude_keywords = [k.strip() for k in exclude_kws_input.split(",") if k.strip()]

    exclude_malls_input = st.text_input(
        "제외 쇼핑몰 (쉼표 구분)",
        value="",
        help="쇼핑 데이터 분석 시 결과에서 배제할 쇼핑몰명을 입력하세요."
    )
    exclude_malls = [m.strip() for m in exclude_malls_input.split(",") if m.strip()]

st.sidebar.markdown("---")
st.sidebar.title("🔍 검색 조건 설정")

# 검색 키워드 입력
default_keywords = "아이폰, 갤럭시"
keywords_raw = st.sidebar.text_input(
    "검색어 (쉼표로 구분)", 
    value=default_keywords,
    help="여러 검색어를 입력할 때는 쉼표(,)로 구분해 주세요. (예: 아이폰, 갤럭시)"
)
keywords_list = [k.strip() for k in keywords_raw.split(",") if k.strip()]
if len(keywords_list) > 5:
    st.sidebar.caption("⚠️ 비교 가능한 키워드는 최대 5개로 제한됩니다. 입력된 키워드 중 상위 5개만 반영됩니다.")

# 검색 기간 설정
today = datetime.today()
default_start_date = today - timedelta(days=30)
date_range = st.sidebar.date_input(
    "검색 기간",
    value=(default_start_date, today),
    max_value=today,
    help="데이터랩 및 쇼핑인사이트 분석 기간을 설정합니다."
)

start_date_str = ""
end_date_str = ""
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date_str = date_range[0].strftime("%Y-%m-%d")
    end_date_str = date_range[1].strftime("%Y-%m-%d")

# API 인스턴스 생성 (세션 상태에 저장된 최종 키를 사용)
api_client = None
current_id = st.session_state["client_id"]
current_secret = st.session_state["client_secret"]
if current_id and current_secret:
    api_client = NaverApiClient(current_id, current_secret)

# 메뉴 네비게이션
st.sidebar.markdown("---")
st.sidebar.title("📌 분석 메뉴")
menu = st.sidebar.radio(
    "이동할 페이지 선택",
    [
        "🏠 홈 & API 연결 확인",
        "📈 통합 검색어 트렌드",
        "🛍️ 쇼핑 상품 분석",
        "📝 블로그 반응 분석",
        "☕ 카페글 반응 분석",
        "📰 뉴스 보도 분석",
        "🛒 쇼핑 트렌드 분석"
    ]
)

# ----------------- 공통 함수 및 데코레이터 -----------------
def get_theme_settings(theme_name: str) -> dict:
    """
    선택한 테마명에 따른 Plotly 차트 템플릿 및 컬러 세팅을 반환합니다.
    """
    themes = {
        "Nord Modern": {
            "palette": ["#88C0D0", "#81A1C1", "#5E81AC", "#8FBCBB", "#BF616A", "#D08770", "#EBCB8B", "#A3BE8C", "#B48EAD"],
            "continuous": ["#E5E9F0", "#81A1C1", "#5E81AC"],
            "template": "plotly_white"
        },
        "Cyberpunk Dark": {
            "palette": ["#FF007F", "#00F0FF", "#FFDD00", "#7000FF", "#00FF66", "#FF5F00", "#AA00FF"],
            "continuous": ["#1A1B35", "#FF007F", "#00F0FF"],
            "template": "plotly_dark"
        },
        "Light Clean": {
            "palette": ["#F4A261", "#2A9D8F", "#E76F51", "#264653", "#E9C46A", "#A8DADC", "#457B9D"],
            "continuous": ["#F1FAEE", "#A8DADC", "#457B9D"],
            "template": "ggplot2"
        },
        "Warm Autumn": {
            "palette": ["#8C2F39", "#B2533E", "#D57E52", "#F1C27B", "#A7727D", "#EED4E8", "#C38154"],
            "continuous": ["#F5F5F7", "#D57E52", "#8C2F39"],
            "template": "seaborn"
        }
    }
    return themes.get(theme_name, themes["Nord Modern"])

def customize_plotly_chart(fig, theme_choice: str):
    """
    Plotly 차트의 한글 폰트 깨짐 방지 및 그리드선을 정돈하고 툴팁 설정을 보완합니다.
    """
    font_family = "Pretendard, Nanum Square, Malgun Gothic, sans-serif"
    fig.update_layout(font=dict(family=font_family))
    fig.update_layout(hoverlabel=dict(font_size=12, font_family=font_family))
    
    theme = get_theme_settings(theme_choice)
    grid_color = "rgba(255, 255, 255, 0.1)" if theme["template"] == "plotly_dark" else "rgba(200, 200, 200, 0.15)"
    
    # X축 그리드 숨기기 (시계열 눈금 강조) 및 Y축 그리드선 옅게 세팅
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=grid_color)
    return fig

def apply_global_filters(df: pd.DataFrame, text_columns: list) -> pd.DataFrame:
    """
    사이드바 공통 전처리 설정값을 사용하여 데이터프레임을 필터링합니다.
    """
    if df.empty:
        return df
        
    # 1. 제외 키워드 필터링
    if exclude_keywords:
        for col in text_columns:
            if col in df.columns:
                for kw in exclude_keywords:
                    df = df[~df[col].astype(str).str.contains(kw, case=False, na=False)]
                    
    # 2. 제외 쇼핑몰 필터링
    if exclude_malls and "mallName" in df.columns:
        for mall in exclude_malls:
            df = df[~df["mallName"].astype(str).str.contains(mall, case=False, na=False)]
            
    return df

def check_api_connection():
    if not api_client:
        st.warning("👉 사이드바에서 **Client ID**와 **Client Secret**을 입력해 주셔야 서비스 이용이 가능합니다.")
        return False
    return True

def handle_api_error(error_message: str):
    """
    API 오류가 발생했을 때 적절한 경고 및 가이드를 제공하는 공통 핸들러
    """
    st.error(f"🚨 오류 발생: {error_message}")
    if "024" in error_message or "Authentication failed" in error_message:
        if "Scope Status Invalid" in error_message:
            st.info(
                "💡 **해결 방법 (권한 설정 오류 - Scope Status Invalid)**:\n\n"
                "이 에러는 사용 중인 네이버 API 키에 **해당 기능(예: 검색)의 접근 권한**이 비활성화되어 있을 때 발생합니다.\n\n"
                "**권한 설정 점검:**\n"
                "1. [네이버 개발자 센터](https://developers.naver.com/) 로그인\n"
                "2. **Application > 내 애플리케이션 > API 설정** 탭 이동\n"
                "3. **사용 API**에 **'검색'**, **'데이터랩 (검색어트렌드)'**, **'데이터랩 (쇼핑인사이트)'**이 모두 추가되어 있는지 확인하고 하단의 **수정하기** 버튼을 눌러 저장해 주세요."
            )
        elif "NID AUTH Result Invalid" in error_message:
            st.info(
                "💡 **해결 방법 (인증 키 불일치 오류 - NID AUTH Result Invalid)**:\n\n"
                "이 에러는 입력된 **Client ID** 또는 **Client Secret** 자체가 틀렸거나 네이버 서버에서 인증하지 못할 때 발생합니다.\n\n"
                "**확인해보실 사항:**\n"
                "1. **ID/Secret 뒤바뀜 확인**: 사이드바의 `Client ID` 칸과 `Client Secret` 칸에 값이 서로 바뀌어 입력되지 않았는지 확인해 주세요.\n"
                "2. **정확한 복사 여부**: 앞뒤에 보이지 않는 공백(스페이스)이나 줄바꿈 문자 등이 포함되지 않았는지 다시 한번 복사해서 입력해 주세요.\n"
                "3. **설정 반영 시간**: 개발자 센터에서 사용 API 설정을 수정한 지 얼마 안 되었다면, 네이버 서버에 반영되는 데 **최대 3~5분** 정도 걸릴 수 있습니다. 잠시 후 새로고침하여 다시 시도해 보세요.\n"
                "4. **애플리케이션 일치 여부**: API 설정을 수정한 애플리케이션의 Client ID와 현재 대시보드에 입력한 Client ID가 동일한지 다시 확인해 주세요."
            )
        else:
            st.info(
                "💡 **해결 방법 (인증 오류)**:\n\n"
                "네이버 개발자 센터에서 API 권한 및 Client ID / Secret 값을 다시 한번 확인해 주세요. "
                "복사/붙여넣기 시 공백이나 줄바꿈 문자가 들어갔는지 확인이 필요합니다."
            )

# ----------------- 1. 홈 & API 연결 확인 -----------------
def render_home_page():
    st.title("🏠 네이버 API 통합 대시보드")
    st.subheader("네이버 오픈 API 데이터를 수집하고 인터랙티브하게 시각화 분석하는 플랫폼입니다.")
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 💡 분석 가능한 주요 영역
        * **통합 검색어 트렌드**: 키워드 간의 네이버 전체 검색량 추이를 비교합니다.
        * **쇼핑 상품 분석**: 네이버 쇼핑 검색결과의 가격 분포, 브랜드 및 제조사 비율을 분석합니다.
        * **블로그 반응**: 최근 블로그 포스트의 여론 분석 및 등록 추세를 확인합니다.
        * **카페글 반응**: 카페에서의 관련 글 작성량 및 트렌드를 모니터링합니다.
        * **뉴스 보도**: 언론사들의 관련 보도 집중도 및 보도 추이를 추적합니다.
        * **쇼핑 트렌드**: 네이버 쇼핑 내에서 카테고리별 검색 클릭률 변화를 모니터링합니다.
        """)
        
    with col2:
        st.markdown("### ⚡ API 연결 상태 테스트")
        if api_client:
            if st.button("연결 테스트 실행"):
                with st.spinner("네이버 API와 통신 중..."):
                    try:
                        api_client.test_connection()
                        st.success("✅ 네이버 API 연결에 성공했습니다! 정상적으로 데이터를 가져올 수 있습니다.")
                    except Exception as e:
                        handle_api_error(str(e))
        else:
            st.info("프로젝트 폴더 내 `.env` 파일에 API Key를 먼저 입력하시면 연결 상태를 테스트할 수 있습니다.")

# ----------------- 2. 통합 검색어 트렌드 -----------------
def render_search_trend_page():
    st.title("📈 통합 검색어 트렌드 분석")
    st.markdown("네이버 통합 검색 내에서 입력된 검색어들의 상대적 검색량 추이를 보여줍니다.")
    
    if not check_api_connection():
        return
        
    if not keywords_list:
        st.warning("검색어를 입력해 주세요.")
        return

    if not start_date_str or not end_date_str:
        st.warning("검색 기간을 올바르게 선택해 주세요 (시작일과 종료일이 모두 필요합니다).")
        return
        
    # 최대 5개 그룹 지원하므로 처리
    st.info(f"검색 기간: {start_date_str} ~ {end_date_str} | 대상 검색어: {', '.join(keywords_list[:5])}")
    
    # API 요청을 위한 데이터 구조 설계
    # 각 키워드를 각각의 그룹명과 키워드로 등록해 일대일 비교가 용이하도록 구성
    keyword_groups = []
    for kw in keywords_list[:5]:
        keyword_groups.append({
            "groupName": kw,
            "keywords": [kw]
        })
        
    with st.spinner("검색어 트렌드 분석 중..."):
        try:
            res = api_client.get_search_trend(
                start_date=start_date_str,
                end_date=end_date_str,
                time_unit="date",
                keyword_groups=keyword_groups
            )
            
            # 응답 데이터 파싱 및 시각화용 데이터프레임 변환
            results = res.get("results", [])
            if not results or len(results[0].get("data", [])) == 0:
                st.info("선택한 기간 동안의 데이터가 존재하지 않습니다.")
                return
                
            # 데이터 변환
            df_list = []
            for group in results:
                title = group.get("title")
                data_points = group.get("data", [])
                for dp in data_points:
                    df_list.append({
                        "날짜": dp.get("period"),
                        "검색어": title,
                        "검색 비율(%)": dp.get("ratio")
                    })
            
            df = pd.DataFrame(df_list)
            df = apply_global_filters(df, ["검색어"])
            df["날짜"] = pd.to_datetime(df["날짜"])
            
            # 테마 설정 획득
            theme = get_theme_settings(theme_choice)
            
            # 시각화 (Plotly)
            fig = px.line(
                df, 
                x="날짜", 
                y="검색 비율(%)", 
                color="검색어",
                title="일자별 검색어 상대적 트렌드 (가장 높은 날을 100으로 기준)",
                labels={"날짜": "기간", "검색 비율(%)": "상대적 검색량 (%)"},
                template=theme["template"],
                color_discrete_sequence=theme["palette"]
            )
            fig = customize_plotly_chart(fig, theme_choice)
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            # 통계 요약 피드백
            st.markdown("### 📊 요약 분석 정보")
            max_df = df.loc[df.groupby("검색어")["검색 비율(%)"].idxmax()]
            
            cols = st.columns(len(max_df))
            for i, row in enumerate(max_df.itertuples()):
                with cols[i]:
                    st.metric(
                        label=f"{row.검색어} 최대 수치일",
                        value=row.날짜.strftime("%Y-%m-%d"),
                        delta=f"비율: {row._3:.1f}%"
                    )
                    
            # 데이터 표 표시
            with st.expander("원본 데이터 테이블 보기"):
                trend_pivot = df.pivot(index="날짜", columns="검색어", values="검색 비율(%)")
                st.dataframe(trend_pivot, use_container_width=True)
                csv_data = trend_pivot.to_csv().encode('utf-8-sig')
                st.download_button(
                    label="📥 트렌드 데이터 다운로드 (CSV)",
                    data=csv_data,
                    file_name=f"naver_search_trend_{datetime.now().strftime('%Y%m%d%H%M')}.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            handle_api_error(str(e))

# ----------------- 3. 쇼핑 상품 분석 -----------------
def render_shopping_search_page():
    st.title("🛍️ 쇼핑 상품 및 가격 분석")
    st.markdown("네이버 쇼핑에서 검색 결과의 가격 분포와 판매 쇼핑몰, 제조사/브랜드 점유율을 분석합니다.")
    
    if not check_api_connection():
        return
        
    if not keywords_list:
        st.warning("검색어를 입력해 주세요.")
        return
        
    # 컨트롤러 가로형 배치
    col_ctl1, col_ctl2, col_ctl3 = st.columns(3)
    with col_ctl1:
        target_kw = st.selectbox("분석 대상 검색어 선택", keywords_list)
    with col_ctl2:
        display_count = st.slider("조회할 상품 개수", min_value=10, max_value=100, value=50, step=10)
    with col_ctl3:
        sort_option = st.selectbox(
            "정렬 옵션", 
            ["sim", "date", "asc", "dsc"], 
            format_func=lambda x: {"sim": "유사도순", "date": "최신등록순", "asc": "가격낮은순", "dsc": "가격높은순"}[x]
        )
    
    with st.spinner("쇼핑 데이터 가져오는 중..."):
        try:
            res = api_client.search_shopping(query=target_kw, display=display_count, sort=sort_option)
            items = res.get("items", [])
            
            if not items:
                st.info("검색된 쇼핑 상품이 없습니다.")
                return
                
            # Pandas DataFrame 구축
            df = pd.DataFrame(items)
            
            # HTML 태그 제거용 텍스트 클리닝 (제목)
            df["title_clean"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
            
            # 공통 필터 적용
            df = apply_global_filters(df, ["title_clean", "brand", "maker"])
            
            if df.empty:
                st.info("필터링 적용 후 남은 쇼핑 상품 데이터가 없습니다.")
                return
                
            # 데이터 전처리: 가격 숫자로 변환
            df["lprice"] = pd.to_numeric(df["lprice"], errors="coerce").fillna(0).astype(int)
            df["hprice"] = pd.to_numeric(df["hprice"], errors="coerce").fillna(0).astype(int)
            
            # 기본 지표 카드
            valid_price = df[df["lprice"] > 0]["lprice"]
            min_price = int(valid_price.min()) if not valid_price.empty else 0
            max_price = int(valid_price.max()) if not valid_price.empty else 0
            avg_price = int(valid_price.mean()) if not valid_price.empty else 0
            
            st.markdown("### 💵 요약 가격 정보")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("총 검색 상품 수", f"{len(df)}개")
            c2.metric("최저 가격", f"{min_price:,.0f} 원")
            c3.metric("최고 가격", f"{max_price:,.0f} 원")
            c4.metric("평균 가격", f"{avg_price:,.0f} 원")
            
            st.markdown("---")
            
            # 테마 획득
            theme = get_theme_settings(theme_choice)
            
            # 시각화 영역 분할
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("#### 📈 가격 분포 분석")
                if not valid_price.empty:
                    fig_hist = px.histogram(
                        df[df["lprice"] > 0], 
                        x="lprice", 
                        nbins=20,
                        title="최저가 기준 가격 분포 히스토그램",
                        labels={"lprice": "최저 가격 (원)", "count": "상품 수"},
                        template=theme["template"],
                        color_discrete_sequence=[theme["palette"][0]]
                    )
                    fig_hist = customize_plotly_chart(fig_hist, theme_choice)
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.write("가격 데이터가 존재하지 않습니다.")
                    
            with col_chart2:
                st.markdown("#### 🏢 판매 쇼핑몰 점유율 (상위 10개)")
                mall_counts = df["mallName"].value_counts().head(10).reset_index()
                mall_counts.columns = ["쇼핑몰명", "상품 수"]
                fig_mall = px.bar(
                    mall_counts,
                    x="상품 수",
                    y="쇼핑몰명",
                    orientation="h",
                    title="쇼핑몰별 등록 상품 분포",
                    labels={"상품 수": "상품 수", "쇼핑몰명": "쇼핑몰"},
                    template=theme["template"],
                    color="상품 수",
                    color_continuous_scale=theme["continuous"]
                )
                fig_mall = customize_plotly_chart(fig_mall, theme_choice)
                fig_mall.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_mall, use_container_width=True)
                
            col_chart3, col_chart4 = st.columns(2)
            
            with col_chart3:
                st.markdown("#### 🏷️ 브랜드 점유율 (상위 7개)")
                brand_counts = df[df["brand"] != ""]["brand"].value_counts().head(7).reset_index()
                if not brand_counts.empty:
                    brand_counts.columns = ["브랜드", "상품 수"]
                    fig_brand = px.pie(
                        brand_counts,
                        values="상품 수",
                        names="브랜드",
                        title="주요 브랜드 점유율",
                        template=theme["template"],
                        color_discrete_sequence=theme["palette"]
                    )
                    fig_brand = customize_plotly_chart(fig_brand, theme_choice)
                    st.plotly_chart(fig_brand, use_container_width=True)
                else:
                    st.info("브랜드 메타데이터가 비어 있어 차트를 그릴 수 없습니다.")
                    
            with col_chart4:
                st.markdown("#### 🛠️ 제조사 점유율 (상위 7개)")
                maker_counts = df[df["maker"] != ""]["maker"].value_counts().head(7).reset_index()
                if not maker_counts.empty:
                    maker_counts.columns = ["제조사", "상품 수"]
                    fig_maker = px.pie(
                        maker_counts,
                        values="상품 수",
                        names="제조사",
                        title="주요 제조사 점유율",
                        template=theme["template"],
                        hole=0.4,
                        color_discrete_sequence=theme["palette"]
                    )
                    fig_maker = customize_plotly_chart(fig_maker, theme_choice)
                    st.plotly_chart(fig_maker, use_container_width=True)
                else:
                    st.info("제조사 메타데이터가 비어 있어 차트를 그릴 수 없습니다.")
            
            # 상품 목록 테이블
            st.markdown("### 📋 수집된 상품 목록")
            display_df = df[["title_clean", "lprice", "mallName", "brand", "maker", "link"]].rename(
                columns={
                    "title_clean": "상품명",
                    "lprice": "최저가",
                    "mallName": "쇼핑몰",
                    "brand": "브랜드",
                    "maker": "제조사",
                    "link": "링크"
                }
            )
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "최저가": st.column_config.NumberColumn("최저가 (원)", format="%d 원"),
                    "링크": st.column_config.LinkColumn("상품 링크", display_text="바로가기")
                }
            )
            csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 쇼핑 분석 데이터 다운로드 (CSV)",
                data=csv_data,
                file_name=f"naver_shopping_analysis_{target_kw}_{datetime.now().strftime('%Y%m%d%H%M')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            handle_api_error(str(e))

# ----------------- 4. 블로그 반응 분석 -----------------
def render_blog_search_page():
    st.title("📝 블로그 반응 분석")
    st.markdown("네이버 블로그 검색결과를 바탕으로 포스트 트렌드와 발행량 변동을 확인합니다.")
    
    if not check_api_connection():
        return
        
    if not keywords_list:
        st.warning("검색어를 입력해 주세요.")
        return
        
    col_ctl1, col_ctl2, col_ctl3 = st.columns(3)
    with col_ctl1:
        target_kw = st.selectbox("분석 대상 검색어 선택", keywords_list)
    with col_ctl2:
        display_count = st.slider("수집할 블로그 수", min_value=10, max_value=100, value=50, step=10)
    with col_ctl3:
        sort_option = st.selectbox(
            "정렬 옵션", 
            ["sim", "date"], 
            format_func=lambda x: {"sim": "유사도순", "date": "최신날짜순"}[x]
        )
    
    with st.spinner("블로그 포스트 수집 중..."):
        try:
            res = api_client.search_blog(query=target_kw, display=display_count, sort=sort_option)
            items = res.get("items", [])
            
            if not items:
                st.info("검색된 블로그 글이 없습니다.")
                return
                
            df = pd.DataFrame(items)
            
            # HTML 태그 제거 및 날짜 형식 변환
            df["title_clean"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
            df["description_clean"] = df["description"].str.replace("<b>", "").str.replace("</b>", "")
            
            # 공통 필터 적용
            df = apply_global_filters(df, ["title_clean", "description_clean", "bloggername"])
            
            if df.empty:
                st.info("필터링 적용 후 남은 블로그 데이터가 없습니다.")
                return
                
            df["post_date"] = pd.to_datetime(df["postdate"], format="%Y%m%d", errors="coerce")
            
            # 발행 날짜별 추이 분석
            date_counts = df["post_date"].value_counts().sort_index().reset_index()
            date_counts.columns = ["작성일", "발행 건수"]
            
            theme = get_theme_settings(theme_choice)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("#### 📅 일자별 블로그 글 등록량 추이")
                fig_date = px.line(
                    date_counts,
                    x="작성일",
                    y="발행 건수",
                    title="검색 결과 내 등록 일자별 추세 (최근 날짜 중심)",
                    labels={"작성일": "작성일", "발행 건수": "글 수"},
                    markers=True,
                    template=theme["template"],
                    color_discrete_sequence=[theme["palette"][0]]
                )
                fig_date = customize_plotly_chart(fig_date, theme_choice)
                st.plotly_chart(fig_date, use_container_width=True)
                
            with col2:
                st.markdown("#### ✍️ 주요 블로러 채널 순위")
                blogger_counts = df["bloggername"].value_counts().head(10).reset_index()
                blogger_counts.columns = ["블로거 이름", "작성 글 수"]
                fig_blog = px.bar(
                    blogger_counts,
                    x="작성 글 수",
                    y="블로거 이름",
                    title="검색 결과 내 상위 노출 빈도",
                    orientation="h",
                    template=theme["template"],
                    color_discrete_sequence=[theme["palette"][0]]
                )
                fig_blog = customize_plotly_chart(fig_blog, theme_choice)
                fig_blog.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_blog, use_container_width=True)
                
            # 블로그 원본 목록
            st.markdown("### 📋 수집된 블로그 포스트 목록")
            display_df = df[["title_clean", "bloggername", "post_date", "link", "description_clean"]].rename(
                columns={
                    "title_clean": "제목",
                    "bloggername": "블로그명",
                    "post_date": "작성일",
                    "link": "포스트 링크",
                    "description_clean": "내용 요약"
                }
            )
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "포스트 링크": st.column_config.LinkColumn("포스트 링크", display_text="바로가기")
                }
            )
            csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 블로그 데이터 다운로드 (CSV)",
                data=csv_data,
                file_name=f"naver_blog_data_{target_kw}_{datetime.now().strftime('%Y%m%d%H%M')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            handle_api_error(str(e))

# ----------------- 5. 카페글 반응 분석 -----------------
def render_cafe_search_page():
    st.title("☕ 카페글 반응 분석")
    st.markdown("네이버 카페 게시글 검색결과를 통해 커뮤니티 내 여론 및 언급 빈도를 확인합니다.")
    
    if not check_api_connection():
        return
        
    if not keywords_list:
        st.warning("검색어를 입력해 주세요.")
        return
        
    col_ctl1, col_ctl2, col_ctl3 = st.columns(3)
    with col_ctl1:
        target_kw = st.selectbox("분석 대상 검색어 선택", keywords_list)
    with col_ctl2:
        display_count = st.slider("수집할 카페글 수", min_value=10, max_value=100, value=50, step=10)
    with col_ctl3:
        sort_option = st.selectbox(
            "정렬 옵션", 
            ["sim", "date"], 
            format_func=lambda x: {"sim": "유사도순", "date": "최신날짜순"}[x]
        )
    
    with st.spinner("카페글 수집 중..."):
        try:
            res = api_client.search_cafearticle(query=target_kw, display=display_count, sort=sort_option)
            items = res.get("items", [])
            
            if not items:
                st.info("검색된 카페글이 없습니다.")
                return
                
            df = pd.DataFrame(items)
            
            df["title_clean"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
            df["description_clean"] = df["description"].str.replace("<b>", "").str.replace("</b>", "")
            
            # 공통 필터 적용
            df = apply_global_filters(df, ["title_clean", "description_clean", "cafename"])
            
            if df.empty:
                st.info("필터링 적용 후 남은 카페글 데이터가 없습니다.")
                return
                
            theme = get_theme_settings(theme_choice)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("#### 🏠 언급량이 많은 인기 카페 (상위 10개)")
                cafe_counts = df["cafename"].value_counts().head(10).reset_index()
                cafe_counts.columns = ["카페명", "게시글 수"]
                fig_cafe = px.bar(
                    cafe_counts,
                    x="게시글 수",
                    y="카페명",
                    title="검색어가 자주 언급되는 상위 카페",
                    orientation="h",
                    template=theme["template"],
                    color="게시글 수",
                    color_continuous_scale=theme["continuous"]
                )
                fig_cafe = customize_plotly_chart(fig_cafe, theme_choice)
                fig_cafe.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_cafe, use_container_width=True)
                
            with col2:
                st.markdown("#### 📊 상위 카페 점유율 비율")
                fig_pie = px.pie(
                    cafe_counts,
                    values="게시글 수",
                    names="카페명",
                    title="언급 비중 비율",
                    template=theme["template"],
                    color_discrete_sequence=theme["palette"]
                )
                fig_pie = customize_plotly_chart(fig_pie, theme_choice)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            # 카페글 목록
            st.markdown("### 📋 수집된 카페글 목록")
            display_df = df[["title_clean", "cafename", "link", "description_clean"]].rename(
                columns={
                    "title_clean": "제목",
                    "cafename": "카페명",
                    "link": "글 링크",
                    "description_clean": "내용 요약"
                }
            )
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "글 링크": st.column_config.LinkColumn("글 링크", display_text="바로가기")
                }
            )
            csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 카페 데이터 다운로드 (CSV)",
                data=csv_data,
                file_name=f"naver_cafe_data_{target_kw}_{datetime.now().strftime('%Y%m%d%H%M')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            handle_api_error(str(e))

# ----------------- 6. 뉴스 보도 분석 -----------------
def render_news_search_page():
    st.title("📰 뉴스 보도 분석")
    st.markdown("네이버 뉴스 검색결과를 모니터링하고 주요 보도 매체 분포를 분석합니다.")
    
    if not check_api_connection():
        return
        
    if not keywords_list:
        st.warning("검색어를 입력해 주세요.")
        return
        
    col_ctl1, col_ctl2, col_ctl3 = st.columns(3)
    with col_ctl1:
        target_kw = st.selectbox("분석 대상 검색어 선택", keywords_list)
    with col_ctl2:
        display_count = st.slider("수집할 뉴스 기사 수", min_value=10, max_value=100, value=50, step=10)
    with col_ctl3:
        sort_option = st.selectbox(
            "정렬 옵션", 
            ["sim", "date"], 
            format_func=lambda x: {"sim": "유사도순", "date": "최신날짜순"}[x]
        )
    
    with st.spinner("뉴스 기사 수집 중..."):
        try:
            res = api_client.search_news(query=target_kw, display=display_count, sort=sort_option)
            items = res.get("items", [])
            
            if not items:
                st.info("검색된 뉴스 기사가 없습니다.")
                return
                
            df = pd.DataFrame(items)
            
            df["title_clean"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
            df["description_clean"] = df["description"].str.replace("<b>", "").str.replace("</b>", "")
            
            # 공통 필터 적용
            df = apply_global_filters(df, ["title_clean", "description_clean"])
            
            if df.empty:
                st.info("필터링 적용 후 남은 뉴스 데이터가 없습니다.")
                return
                
            # 날짜 파싱 (예: "Mon, 26 Sep 2016 07:50:00 +0900")
            df["pub_date"] = pd.to_datetime(df["pubDate"], errors="coerce")
            df["pub_day"] = df["pub_date"].dt.date
            
            # 일자별 기사 발행 추이
            day_counts = df["pub_day"].value_counts().sort_index().reset_index()
            day_counts.columns = ["보도일", "기사 수"]
            
            theme = get_theme_settings(theme_choice)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("#### 📅 일자별 기사 발행 추이")
                if not day_counts.empty:
                    fig_day = px.line(
                        day_counts,
                        x="보도일",
                        y="기사 수",
                        title="기사 발생 타임라인 추이",
                        labels={"보도일": "날짜", "기사 수": "보도량"},
                        markers=True,
                        template=theme["template"],
                        color_discrete_sequence=[theme["palette"][0]]
                    )
                    fig_day = customize_plotly_chart(fig_day, theme_choice)
                    st.plotly_chart(fig_day, use_container_width=True)
                else:
                    st.write("작성일 데이터를 파싱할 수 없습니다.")
                    
            with col2:
                # 네이버 링크 유무에 따른 구분 (link에 'news.naver.com'이 포함되어 있으면 네이버 뉴스 링크 제공 언론사)
                df["is_naver_news"] = df["link"].apply(lambda x: "네이버 뉴스 제휴" if "news.naver.com" in str(x) else "일반 포털 뉴스")
                naver_news_counts = df["is_naver_news"].value_counts().reset_index()
                naver_news_counts.columns = ["구분", "기사 수"]
                
                st.markdown("#### 🔗 네이버 뉴스 제휴 여부 비율")
                fig_link = px.pie(
                    naver_news_counts,
                    values="기사 수",
                    names="구분",
                    title="네이버 자체 제공 vs 외부 언론사 링크 비율",
                    template=theme["template"],
                    color_discrete_sequence=theme["palette"]
                )
                fig_link = customize_plotly_chart(fig_link, theme_choice)
                st.plotly_chart(fig_link, use_container_width=True)
                
            # 뉴스 목록
            st.markdown("### 📋 수집된 뉴스 목록")
            display_df = df[["title_clean", "pub_date", "link", "description_clean"]].rename(
                columns={
                    "title_clean": "뉴스 제목",
                    "pub_date": "보도 일시",
                    "link": "뉴스 링크",
                    "description_clean": "보도 본문 요약"
                }
            )
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "뉴스 링크": st.column_config.LinkColumn("뉴스 링크", display_text="바로가기")
                }
            )
            csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 뉴스 데이터 다운로드 (CSV)",
                data=csv_data,
                file_name=f"naver_news_data_{target_kw}_{datetime.now().strftime('%Y%m%d%H%M')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            handle_api_error(str(e))

# ----------------- 7. 쇼핑 트렌드 분석 -----------------
def render_shopping_trend_page():
    st.title("🛒 쇼핑 트렌드 분석 (쇼핑인사이트)")
    st.markdown("네이버 쇼핑 서비스 내에서 특정 쇼핑 분야별 검색어의 클릭 변화 추이를 보여줍니다.")
    
    if not check_api_connection():
        return
        
    if not keywords_list:
        st.warning("검색어를 입력해 주세요.")
        return

    if not start_date_str or not end_date_str:
        st.warning("검색 기간을 올바르게 선택해 주세요.")
        return
        
    # 쇼핑인사이트에 필요한 카테고리 정보 정의
    categories = {
        "패션의류": "50000000",
        "패션잡화": "50000001",
        "화장품/미용": "50000002",
        "디지털/가전": "50000003",
        "가구/인테리어": "50000004",
        "출산/육아": "50000005",
        "식품": "50000006",
        "스포츠/레저": "50000007",
        "생활/건강": "50000008",
        "여가/생활편의": "50000009",
        "면세점": "50000010",
        "도서": "50005542"
    }
    
    selected_category_name = st.selectbox("쇼핑 카테고리 선택", list(categories.keys()))
    category_code = categories[selected_category_name]
    
    st.info(f"설정 카테고리: {selected_category_name} (코드: {category_code}) | 검색 기간: {start_date_str} ~ {end_date_str}")
    
    # API 요청을 위한 키워드 리스트 구성 (최대 5개)
    keywords_payload = []
    for kw in keywords_list[:5]:
        keywords_payload.append({
            "name": kw,
            "param": [kw]
        })
        
    with st.spinner("쇼핑 트렌드 수집 중..."):
        try:
            res = api_client.get_shopping_trend(
                start_date=start_date_str,
                end_date=end_date_str,
                time_unit="date",
                category_id=category_code,
                keywords=keywords_payload
            )
            
            results = res.get("results", [])
            if not results or len(results[0].get("data", [])) == 0:
                st.info("해당 조건의 데이터가 존재하지 않습니다.")
                return
                
            df_list = []
            for group in results:
                title = group.get("title")
                data_points = group.get("data", [])
                for dp in data_points:
                    df_list.append({
                        "날짜": dp.get("period"),
                        "키워드": title,
                        "클릭 비율(%)": dp.get("ratio")
                    })
            
            df = pd.DataFrame(df_list)
            df = apply_global_filters(df, ["키워드"])
            df["날짜"] = pd.to_datetime(df["날짜"])
            
            theme = get_theme_settings(theme_choice)
            
            # 시각화 (Plotly)
            fig = px.line(
                df,
                x="날짜",
                y="클릭 비율(%)",
                color="키워드",
                title=f"'{selected_category_name}' 카테고리 내 키워드별 클릭 점유 비율 추이",
                labels={"날짜": "날짜", "클릭 비율(%)": "상대적 클릭수 비율 (%)"},
                template=theme["template"],
                color_discrete_sequence=theme["palette"]
            )
            fig = customize_plotly_chart(fig, theme_choice)
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            # 데이터 표 표시
            with st.expander("원본 데이터 테이블 보기"):
                trend_pivot = df.pivot(index="날짜", columns="키워드", values="클릭 비율(%)")
                st.dataframe(trend_pivot, use_container_width=True)
                csv_data = trend_pivot.to_csv().encode('utf-8-sig')
                st.download_button(
                    label="📥 쇼핑 트렌드 데이터 다운로드 (CSV)",
                    data=csv_data,
                    file_name=f"naver_shopping_trend_{datetime.now().strftime('%Y%m%d%H%M')}.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            handle_api_error(str(e))

# ----------------- 라우터에 따라 렌더링 실행 -----------------
if menu == "🏠 홈 & API 연결 확인":
    render_home_page()
elif menu == "📈 통합 검색어 트렌드":
    render_search_trend_page()
elif menu == "🛍️ 쇼핑 상품 분석":
    render_shopping_search_page()
elif menu == "📝 블로그 반응 분석":
    render_blog_search_page()
elif menu == "☕ 카페글 반응 분석":
    render_cafe_search_page()
elif menu == "📰 뉴스 보도 분석":
    render_news_search_page()
elif menu == "🛒 쇼핑 트렌드 분석":
    render_shopping_trend_page()
