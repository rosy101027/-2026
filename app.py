import math
import requests
import pandas as pd
import streamlit as st
import pydeck as pdk
from datetime import datetime

st.set_page_config(
    page_title="대한민국 하천 위험도 지도",
    page_icon="🌊",
    layout="wide",
)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

st.markdown("""
<style>
.main {background-color: #f5f8fc;}
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
.hero {
    padding: 1.5rem; border-radius: 18px;
    background: linear-gradient(120deg, #092c4c, #176b87);
    color: white; margin-bottom: 1rem;
}
.hero h1 {color:white; margin:0;}
.hero p {color:#e5f4ff; margin:.4rem 0 0 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🌊 대한민국 하천 범람 위험도 지도</h1>
<p>하천 주변 기상정보를 조회하고, 확인 가능한 자료를 바탕으로 예비 위험지수를 살펴보는 연구용 도구</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "안전 안내: 이 사이트의 점수는 공식 범람 확률이나 재난 예측이 아닙니다. "
    "강수 예보만으로 계산한 참고용 지수이며, 실제 위험 판단·대피 결정에는 사용할 수 없습니다. "
    "실제 안전 정보는 기상청·홍수통제소·행정안전부의 공식 안내를 확인하세요."
)

def geocode_place(query: str):
    params = {
        "name": query,
        "count": 8,
        "language": "ko",
        "format": "json",
    }
    r = requests.get(GEOCODING_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("results", [])

def get_weather(lat: float, lon: float):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "precipitation,rain",
        "hourly": "precipitation",
        "daily": "precipitation_sum",
        "forecast_days": 2,
        "timezone": "Asia/Seoul",
    }
    r = requests.get(FORECAST_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def rainfall_score(mm):
    # 임의의 구간형 연구용 지수. 공식 경보 기준이나 통계적 범람확률이 아님.
    if mm < 10:
        return 5
    if mm < 30:
        return 15
    if mm < 50:
        return 30
    if mm < 80:
        return 45
    if mm < 110:
        return 60
    if mm < 150:
        return 75
    return 90

def format_location(item):
    bits = [item.get("name", "")]
    admin = item.get("admin1")
    country = item.get("country")
    if admin and admin not in bits:
        bits.append(admin)
    if country:
        bits.append(country)
    return " · ".join([x for x in bits if x])

with st.sidebar:
    st.header("🔎 하천 검색")
    river_name = st.text_input("하천 이름", placeholder="예: 한강, 낙동강, 청계천")
    st.caption("검색은 지명 검색 서비스 결과를 사용합니다. 하천 자체의 정확한 측정 지점이 아닐 수 있습니다.")
    search_button = st.button("하천 위치 및 날씨 조회", type="primary", use_container_width=True)
    st.divider()
    st.subheader("하상계수 자료")
    coefficient = st.number_input(
        "검증된 하상계수 (모르면 비워두세요)",
        min_value=0.0,
        max_value=100000.0,
        value=0.0,
        step=0.1,
        help="0은 미입력으로 처리됩니다. 출처가 확인된 값만 입력하세요."
    )
    coefficient_source = st.text_input(
        "하상계수 자료 출처 (선택)",
        placeholder="예: 수문조사연보, 보고서명, URL"
    )
    st.caption("전국 모든 하천의 하상계수를 자동으로 확인할 수 있는 단일 공개 자료는 이 초기 버전에 연결되어 있지 않습니다. 확인되지 않은 값은 추정하지 않습니다.")

if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "weather_result" not in st.session_state:
    st.session_state.weather_result = None
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if search_button:
    if not river_name.strip():
        st.error("하천 이름을 입력해 주세요.")
    else:
        try:
            with st.spinner("하천 이름과 관련된 위치를 찾고 있습니다..."):
                places = geocode_place(river_name.strip())
            if not places:
                st.session_state.search_result = None
                st.error("검색 결과가 없습니다. 하천명이나 인근 도시명을 함께 입력해 보세요.")
            else:
                st.session_state.search_result = places
                st.session_state.weather_result = None
                st.session_state.selected_place = None
        except requests.RequestException as e:
            st.error(f"위치 검색 중 오류가 발생했습니다: {e}")

places = st.session_state.search_result

if places:
    st.subheader("📍 검색된 위치 선택")
    options = {f"{format_location(p)}  (위도 {p['latitude']:.3f}, 경도 {p['longitude']:.3f})": i
               for i, p in enumerate(places)}
    selected_label = st.selectbox("조회할 위치", list(options.keys()))
    selected = places[options[selected_label]]
    if st.button("선택한 위치의 강수 정보 가져오기", type="primary"):
        try:
            with st.spinner("해당 위치의 최신 기상정보를 가져오고 있습니다..."):
                weather = get_weather(selected["latitude"], selected["longitude"])
            st.session_state.selected_place = selected
            st.session_state.weather_result = weather
        except requests.RequestException as e:
            st.error(f"날씨 자료 조회 중 오류가 발생했습니다: {e}")

place = st.session_state.selected_place
weather = st.session_state.weather_result

if place and weather:
    current = weather.get("current", {})
    hourly = weather.get("hourly", {})
    daily = weather.get("daily", {})
    current_rain = float(current.get("precipitation") or 0)
    daily_values = daily.get("precipitation_sum") or []
    forecast_rain = float(daily_values[0]) if daily_values and daily_values[0] is not None else 0.0
    score = rainfall_score(forecast_rain)

    st.divider()
    st.subheader(f"🌧️ {river_name} 주변 기상 조회 결과")
    c1, c2, c3 = st.columns(3)
    c1.metric("현재 강수량", f"{current_rain:.1f} mm", help="현재 시각의 강수량 관측·추정값")
    c2.metric("오늘 예상 강수량", f"{forecast_rain:.1f} mm", help="Open-Meteo 일별 예보의 강수량 합계")
    c3.metric("강수 기반 예비 위험지수", f"{score} / 100", help="범람 확률이 아닌 임의 구간형 참고 지수")

    st.markdown("### 🗺️ 조회 위치 지도")
    map_df = pd.DataFrame([{
        "lat": place["latitude"],
        "lon": place["longitude"],
        "name": format_location(place),
        "size": 180,
    }])
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_radius="size",
        get_fill_color=[230, 70, 60, 180],
        pickable=True,
    )
    view = pdk.ViewState(
        latitude=place["latitude"],
        longitude=place["longitude"],
        zoom=9,
        pitch=0,
    )
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "{name}"},
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    ), use_container_width=True)

    st.markdown("### 📊 시간별 강수 예보")
    times = hourly.get("time", [])
    values = hourly.get("precipitation", [])
    if times and values:
        chart_df = pd.DataFrame({"시간": times[:48], "예상 강수량 (mm)": values[:48]})
        chart_df["시간"] = pd.to_datetime(chart_df["시간"]).dt.strftime("%m-%d %H시")
        st.bar_chart(chart_df.set_index("시간"))
    else:
        st.info("시간별 강수 예보를 표시할 자료가 없습니다.")

    st.markdown("### 🧮 하천 자료 확인")
    if coefficient > 0:
        st.success(f"사용자가 입력한 하상계수: {coefficient:g}")
        if coefficient_source.strip():
            st.caption(f"입력한 자료 출처: {coefficient_source}")
        else:
            st.warning("하상계수의 출처가 입력되지 않았습니다. 값의 정확성을 별도로 확인하세요.")
    else:
        st.warning("이 하천의 검증된 하상계수를 자동으로 확인하지 못했습니다. 하상계수는 미확인으로 표시하며 임의의 값을 만들지 않습니다.")

    st.markdown("### ⚠️ 결과 해석")
    st.write(
        f"현재 조회 위치의 오늘 예상 강수량은 {forecast_rain:.1f} mm이며, "
        f"강수 기반 예비 위험지수는 {score}/100입니다. "
        "이 값은 강수량 구간을 점수로 바꾼 연구용 지표일 뿐, 실제 범람 가능성이 "
        f"{score}%라는 뜻은 아닙니다."
    )
    st.info(
        "정확한 하천 범람 분석에는 하천 수위·유량의 실측값, 하천 단면, 제방고, "
        "상류 유역 강수량, 토양 포화도 및 과거 홍수 사례를 이용한 검증이 필요합니다. "
        "현재 버전은 하천 중심선이나 실제 수문 관측소를 자동으로 특정하지 못할 수 있습니다."
    )

    with st.expander("자료 출처 및 한계"):
        st.markdown("""
        - 기상정보: Open-Meteo Forecast API 및 Geocoding API
        - 위치 검색 결과는 하천명과 같은 이름의 지명일 수 있으며, 실제 하천 측정 지점과 다를 수 있습니다.
        - 하상계수는 전국 하천에 대해 검증된 단일 자동 조회 자료로 연결되지 않았습니다.
        - 본 지수는 통계적으로 보정된 범람확률이 아니며, 공식 재난정보가 아닙니다.
        - API 장애, 위치 오인식, 예보 갱신 시각에 따라 결과가 달라질 수 있습니다.
        """)
else:
    st.markdown("### 시작하기")
    st.write("왼쪽 메뉴에서 하천 이름을 입력하고 **하천 위치 및 날씨 조회**를 눌러 주세요.")
    st.write("예시: 한강, 낙동강, 금강, 영산강, 청계천")
    st.info("검색 결과에서 실제 하천과 가까운 위치를 선택해야 합니다. 하천 이름만으로 정확한 수문 관측소가 자동 선택되는 기능은 다음 개발 단계에서 추가해야 합니다.")

st.divider()
st.caption("대한민국 하천 위험도 지도 · 연구 및 학습용 프로토타입")
