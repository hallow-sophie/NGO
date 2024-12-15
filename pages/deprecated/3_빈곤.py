import os
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import streamlit as st

# 현재 파일 경로를 기준으로 데이터 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
shapefile_path = os.path.join(current_dir, "data", "ne_110m_admin_0_countries.shp")
csv_path = os.path.join(current_dir, "data", "poverty.csv")

# Shapefile 로드
world = gpd.read_file(shapefile_path)

# CSV 데이터 로드
data = pd.read_csv(csv_path)

# 5년 단위 그룹 생성
data["YearGroup"] = (data["Year"] // 5) * 5

# Streamlit 앱 설정
st.title("국가별 빈곤도 데이터 시각화 (5년 단위 평균)")

# 유효한 5년 단위 그룹 가져오기
year_groups = sorted(data["YearGroup"].unique())

# 슬라이더를 사용하여 5년 단위 그룹 선택
selected_year_group = st.slider(
    "5년 단위 연도 그룹을 선택하세요",
    min_value=min(year_groups),
    max_value=max(year_groups),
    step=5
)

# 선택한 5년 단위 그룹의 데이터 필터링 및 평균 계산
filtered_data = data[data["YearGroup"] == selected_year_group]
grouped_data = filtered_data.groupby("Country", as_index=False).agg({"Share": "mean"})

# GeoDataFrame 병합
merged_data = world.merge(grouped_data, left_on="ADMIN", right_on="Country", how="left")

# 지도 레이어 생성
polygons = []
for _, row in merged_data.iterrows():
    geometry = row["geometry"]
    if pd.isna(row["Share"]):  # 데이터가 없는 경우
        color = [255, 255, 255, 150]  # 흰색
    else:  # 데이터가 있는 경우
        # 절대 기준(0~1)으로 색상 설정
        normalized_value = max(0, min(1, row["Share"]))  # 값이 0~1 사이로 제한
        color = [
            int((normalized_value) * 255),  # Red decreases as value increases
            int((1 - normalized_value) * 255),       # Green increases as value increases
            0,  # Blue remains constant
            150,  # Transparency
        ]
    if geometry.geom_type == "Polygon":
        polygons.append({"polygon": list(geometry.exterior.coords), "color": color, "share": row["Share"]})
    elif geometry.geom_type == "MultiPolygon":
        for poly in geometry.geoms:
            polygons.append({"polygon": list(poly.exterior.coords), "color": color, "share": row["Share"]})

# Pydeck 레이어 추가
map_layers = [
    pdk.Layer(
        "PolygonLayer",
        data=polygons,
        get_polygon="polygon",
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
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
st.caption(f"선택된 5년 단위 연도 그룹: {selected_year_group}~{selected_year_group + 4}")
st.caption(f"표시되는 빈곤도 값은 선택된 5년 단위 그룹의 평균값입니다.")

# 색상 범례 추가
st.markdown("### 색상 범례")
st.text("🔴 높은 빈곤도 (1.0)")
st.text("🟡 중간 빈곤도 (0.5)")
st.text("🟢 낮은 빈곤도 (0.0)")
