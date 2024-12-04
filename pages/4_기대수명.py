import os
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import streamlit as st
import time

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] == None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(2)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

# 현재 파일 경로를 기준으로 데이터 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
shapefile_path = os.path.join(current_dir, "data", "ne_110m_admin_0_countries.shp")
csv_path = os.path.join(current_dir, "data", "life-expectancy.csv")

# Shapefile 로드
world = gpd.read_file(shapefile_path)

# CSV 데이터 로드
data = pd.read_csv(csv_path)

# Streamlit 앱 설정
st.title("연도별 기대수명 시각화")

# 연도 범위 가져오기
years = sorted(data["Year"].unique())

# 슬라이더를 사용하여 연도 선택
selected_year = st.slider("연도를 선택하세요", min_value=min(years), max_value=max(years), step=1)

# 선택한 연도의 데이터 필터링
filtered_data = data[data["Year"] == selected_year]

# 해당 연도의 min/max 값 계산
if not filtered_data.empty:
    min_value = filtered_data["life"].min()
    max_value = filtered_data["life"].max()
else:
    min_value, max_value = None, None

# GeoDataFrame 병합
merged_data = world.merge(filtered_data, left_on="ADMIN", right_on="Entity", how="left")

# 지도 레이어 생성
polygons = []
for _, row in merged_data.iterrows():
    geometry = row["geometry"]
    if pd.isna(row["life"]) or min_value is None or max_value is None:  # 데이터가 없는 경우
        color = [255, 255, 255, 150]  # 흰색
    else:  # 데이터가 있는 경우
        # 정규화된 값을 사용하여 색상 설정
        normalized_value = (row["life"] - min_value) / (max_value - min_value)
        normalized_value = max(0, min(1, normalized_value))  # 범위를 0~1로 제한
        color = [
            int((1 - normalized_value) * 255),  # Red decreases as value increases
            int(normalized_value * 255),       # Green increases as value increases
            0,  # Blue remains constant
            150,  # Transparency
        ]
    if geometry.geom_type == "Polygon":
        polygons.append({"polygon": list(geometry.exterior.coords), "color": color, "life": row["life"]})
    elif geometry.geom_type == "MultiPolygon":
        for poly in geometry.geoms:
            polygons.append({"polygon": list(poly.exterior.coords), "color": color, "life": row["life"]})

# Pydeck 레이어 추가
map_layers = [
    pdk.Layer(
        "PolygonLayer",
        data=polygons,
        get_polygon="polygon",
        get_fill_color="color",
        get_line_color="[200, 200, 200, 255]" if pd.isna(row["life"]) else "[255, 255, 255, 255]",
        line_width_min_pixels=1,
        pickable=True,
    )
]

# Pydeck 지도 초기 상태
view_state = pdk.ViewState(
    latitude=0,
    longitude=0,
    zoom=1.5,
    min_zoom=0.5,
    max_zoom=10,
)

# Pydeck 차트 생성
deck = pdk.Deck(
    layers=map_layers,
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v9",
)

st.pydeck_chart(deck)

# 선택된 연도 및 정보 표시
st.caption(f"선택된 연도: {selected_year}")
if min_value is not None and max_value is not None:
    st.caption(f"최소 기대수명: {min_value:.2f}세, 최대 기대수명: {max_value:.2f}세")
else:
    st.caption("선택한 연도의 데이터가 없습니다.")

# 색상 범례 추가
st.markdown("### 색상 범례")
st.text(f"🟢 높은 기대수명 (최대값) {max_value:.2f}세")
st.text(f"🟡 중간 기대수명")
st.text(f"🔴 낮은 기대수명 (최소값) {min_value:.2f}세")
