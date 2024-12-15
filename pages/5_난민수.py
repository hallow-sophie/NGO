import os
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import streamlit as st
import time

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

# 현재 파일 경로를 기준으로 데이터 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
shapefile_path = os.path.join(current_dir, "data", "ne_110m_admin_0_countries.shp")
csv_path = os.path.join(current_dir, "data", "refugee.csv")

# CSV 데이터 로드
data = pd.read_csv(csv_path)

# 1950년 이후 데이터만 필터링
data = data[data["Year"] >= 1990]

# 5년 단위로 그룹화할 새로운 열 추가
data["YearGroup"] = (data["Year"] // 5) * 5

# 5년 단위 평균 계산
grouped_data = data.groupby(["YearGroup", "Entity"], as_index=False).agg({"refugee": "mean"})

# 그룹별 데이터 수 계산
group_counts = data.groupby("YearGroup").size()

# 데이터가 충분한 그룹만 선택 (예: 최소 10개 이상의 데이터가 있는 경우)
min_data_threshold = 10
valid_groups = group_counts[group_counts >= min_data_threshold].index
filtered_grouped_data = grouped_data[grouped_data["YearGroup"].isin(valid_groups)]

# Streamlit 앱 설정
st.title("1990년 이후 5년 단위 난민 수")

# 유효한 연도 그룹 가져오기
year_groups = sorted(filtered_grouped_data["YearGroup"].unique())

if year_groups:
    # 슬라이더를 사용하여 5년 단위 그룹 선택
    selected_year_group = st.select_slider(
        "5년 단위 연도 그룹을 선택하세요",
        options=year_groups,
        format_func=lambda x: f"{x}~{x+4}"
    )

    # 선택한 5년 단위 그룹의 데이터 필터링
    filtered_data = filtered_grouped_data[filtered_grouped_data["YearGroup"] == selected_year_group]

    # GeoDataFrame 병합
    world = gpd.read_file(shapefile_path)
    merged_data = world.merge(filtered_data, left_on="ADMIN", right_on="Entity", how="left")

    # 절대값 기준 설정 (0~1,000,000)
    min_value, max_value = 0, 1_000_000

    # 지도 레이어 생성
    polygons = []
    for _, row in merged_data.iterrows():
        geometry = row["geometry"]
        refugee_count = row["refugee"]

        if pd.isna(refugee_count):  # 데이터가 없는 경우
            color = [255, 255, 255, 150]  # 흰색
        else:  # 데이터가 있는 경우
            # 절대값 기준 정규화 (0~1,000,000)
            normalized_value = (refugee_count - min_value) / (max_value - min_value)
            normalized_value = max(0, min(1, normalized_value))  # 범위를 0~1로 제한
            color = [
                int(normalized_value * 255),        # Red increases as value increases
                int((1 - normalized_value) * 255),  # Green decreases as value increases
                0,  # Blue remains constant
                150,  # Transparency
            ]

        if geometry.geom_type == "Polygon":
            polygons.append({"polygon": list(geometry.exterior.coords), "color": color, "refugee": refugee_count})
        elif geometry.geom_type == "MultiPolygon":
            for poly in geometry.geoms:
                polygons.append({"polygon": list(poly.exterior.coords), "color": color, "refugee": refugee_count})

    # Pydeck 레이어 추가
    map_layers = [
        pdk.Layer(
            "PolygonLayer",
            data=polygons,
            get_polygon="polygon",
            get_fill_color="color",
            get_line_color="[200, 200, 200, 255]" if pd.isna(row["refugee"]) else "[255, 255, 255, 255]",
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
    st.caption(f"선택된 5년 단위 연도 그룹: {selected_year_group}~{selected_year_group+4}")
    st.caption("난민 수 범위: 0~1,000,000 기준으로 색상 표시")

    # 색상 범례 추가
    st.markdown("### 색상 범례")
    st.text("🟢 초록색: 낮은 난민 수 (0)")
    st.text("🟡 노란색: 중간 난민 수 (~500,000)")
    st.text("🔴 빨간색: 높은 난민 수 (1,000,000+)")
else:
    st.warning("유효한 데이터가 있는 연도 그룹이 없습니다.")
