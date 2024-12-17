import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

myid = st.session_state['ID']

# 페이지 제목
st.title("📋 문항 평가 ")
conn = st.connection("gsheets", type=GSheetsConnection)

# 설명 텍스트
st.subheader("각 탭에서 동일한 문항에 대해 1~5점 사이의 점수를 선택하고 각 탭에서 제출하세요.")

# 문항 리스트
questions = [
    "문항 1: NGO의 목표와 활동 계획이 공정성과 인류애를 잘 반영했나요?",
    "문항 2: 활동 내용이 실현 가능하고 현실적인 해결 방안을 제시했나요?",
    "문항 3: 포스터, 뉴스 대본, 영상 등 홍보물이 창의적으로 제작되었나요?",
    "문항 4: 홍보물에 NGO의 가치와 메시지가 명확히 전달되었나요?",
    "문항 5: 뉴스 발표가 흥미롭고 설득력 있게 전달되었나요?",
    "문항 6: 발표 내용이 시청자의 관심을 끌고 몰입하게 만들었나요?",
    "문항 7: 갈등 해결 방안이 논리적이고 체계적으로 제시되었나요?",
    "문항 8: 데이터나 시뮬레이션 결과를 적절히 활용했나요?",
    "문항 9: 발표와 홍보물 제작에서 팀원들의 협력이 잘 드러났나요?",
    "문항 10: 팀의 메시지가 일관되게 표현되었나요?",
    "문항 11: 전체적으로 NGO의 활동과 발표가 강렬하고 설득력 있었나요?",
    "문항 12: 지구촌 문제 해결에 대한 진정성과 열정이 느껴졌나요?"
]

# 탭 이름과 Google Sheets 이름 매핑
tab_names = ["팀 A 평가", "팀 B 평가", "팀 C 평가", "팀 D 평가"]
sheet_names = ["TeamA", "TeamB", "TeamC", "TeamD"]
tab_mapping = dict(zip(tab_names, sheet_names))

# 세션 상태 초기화
if "scores_by_tab" not in st.session_state:
    st.session_state["scores_by_tab"] = {
        tab_name: [3] * len(questions) for tab_name in tab_names  # 초기 점수 설정
    }

# 탭 생성
tabs = st.tabs(tab_names)

# 각 탭에서 동일한 질문 출력
for tab, tab_name in zip(tabs, tab_names):
    with tab:
        st.subheader(f"{tab_name}에 대한 평가")
        scores = []

        # 각 질문에 대한 점수 입력
        for i, question in enumerate(questions):
            st.write(f"**{question}**")
            score = st.radio(
                f"점수를 선택하세요 (문항 {i+1})",  # 문항 제목
                options=[1, 2, 3, 4, 5],         # 선택 가능한 점수
                index=st.session_state["scores_by_tab"][tab_name][i] - 1,  # 초기값
                key=f"{tab_name}_Q{i}",          # 고유 키
                horizontal=True                  # 가로로 표시
            )
            scores.append(score)
        
        # 점수를 세션 상태에 저장
        st.session_state["scores_by_tab"][tab_name] = scores

        # 탭별 제출 버튼
        if st.button(f"{tab_name} 점수 제출", key=f"submit_{tab_name}"):
            st.success(f"{tab_name}의 점수를 제출합니다!")

            # Google Sheets에 저장
            worksheet_name = f"Mission5-{tab_mapping[tab_name]}"
            
            # 기존 데이터 읽기
            existing_data = conn.read(worksheet=worksheet_name, ttl="10s")
            existing_df = pd.DataFrame(existing_data)

            # 새로운 점수 데이터 준비
            new_data = pd.DataFrame(
                [[myid] + st.session_state["scores_by_tab"][tab_name]],  # ID와 점수 병합
                columns=["ID"] + [f"Q{i+1}" for i in range(len(questions))]
            )

            # ID가 이미 존재하면 업데이트, 없으면 추가
            if "ID" in existing_df.columns:
                if myid in existing_df["ID"].values:
                    # 기존 ID의 데이터 업데이트
                    existing_df.update(new_data.set_index("ID"))
                else:
                    # 새로운 ID의 데이터 추가
                    existing_df = pd.concat([existing_df, new_data], ignore_index=True)
            else:
                # 기존 데이터에 ID 컬럼이 없으면 새로운 데이터로 초기화
                existing_df = new_data

            # Google Sheets에 데이터 업데이트
            conn.update(
                worksheet=worksheet_name,  # 저장할 시트 이름
                data=existing_df,          # 업데이트할 전체 데이터
            )
            
            st.success(f"{tab_name}의 점수가 Google Sheets '{worksheet_name}' 시트에 저장되었습니다!")
            st.balloons()  # 풍선 애니메이션 추가
            st.toast("제출이 완료되었습니다!")  # 토스트 메시지 (최신 Streamlit 버전 필요)

# Google Sheets 데이터 표시
# st.header("📊 Google Sheets 데이터")
# for tab_name in tab_names:
#     worksheet_name = f"Mission5-{tab_mapping[tab_name]}"
#     st.subheader(f"**{tab_name} 시트 데이터**")
#     df = conn.read(worksheet=worksheet_name, ttl="2s")
#     st.dataframe(df)
