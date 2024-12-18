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
st.header("미션:five: NGO 뉴스 데스크 :woman_in_tuxedo::microphone::man_in_tuxedo:")

contents0 = '''
🎥 **지령5: 뉴스 앵커가 되어 세상을 변화시켜라!** 🎥\n
평화 요원 여러분, 드디어 최종 미션이 도착했습니다! ✉️\n
여러분의 NGO가 활동을 시작했고, 이를 세상에 알릴 시간입니다.\n
이번 임무는 각 팀이 **뉴스 앵커와 기자자**가 되어 NGO의 활동을 전 세계 사람들에게 생생하게 전달하는 것입니다. 🌍\n
각 팀은 뉴스 데스크를 꾸며 자신들의 **활동 내용과 홍보물**을 발표하고, 다른 팀의 발표를 시청하며 **서로 평가하고 피드백**하는 시간을 가질 것입니다.\n 
여러분의 발표는 **지구촌의 미래를 변화시키는 중요한 메시지**가 될 것입니다. 🌟\n
'''

contents1 = '''
📢 **지령 목표:**\n
1️⃣ 팀별로 준비한 뉴스 기사 대본을 토대로 발표 진행.\n
2️⃣ 홍보물(포스터, 광고 등)을 활용해 발표의 완성도를 높이기.\n
3️⃣ 다른 팀의 발표를 경청하며 공정하고 건설적인 피드백을 제공.\n
'''

contents2 = '''
📜 **뉴스 발표 구성:**\n
**1부:** 팀의 NGO 소개와 주요 활동 내용 발표.\n
**2부:** 홍보물 소개 (포스터, 영상 등)와 제작 의도 설명.\n
**3부:** 활동의 성과와 지구촌에 미칠 긍정적인 영향 강조.\n
'''

contents3 = '''
🌟 **특별 지령:**\n
1️⃣ **현장감 살리기:** 뉴스 앵커처럼 발표하며 몰입감을 높이세요.\n
2️⃣ **피드백 & 투표:** 발표 후, 다른 팀의 활동을 공정하게 평가하고 투표하세요. 투표 결과로 '가장 공감받은 NGO'가 선정됩니다!\n
'''

contents4 = '''
💬 **피드백 기준:**\n
활동 내용의 **공정성과 실현 가능성.**\n
홍보물의 **창의성**과 메시지 전달력.\n
발표의 **설득력**과 몰입감.\n
'''

contents5 = '''
**지구촌 평화의 메시지를 전 세계에 알리는 여러분의 멋진 뉴스 데스크를 기대합니다!**\n
최선을 다한 발표와 피드백을 통해 서로 배우고 성장하세요. 여러분의 열정이 지구촌에 희망을 가져다줄 것입니다. ✨🎙️\n
'''

st.write(contents0)
st.write("")
st.write("")

st.write(contents1)
st.write("")
st.write("")

st.write(contents2)
st.write("")
st.write("")

st.write(contents3)
st.write("")
st.write("")

st.write(contents4)
st.write("")
st.write("")

st.write(contents5)
st.write("")
st.write("")
st.markdown("---")



conn = st.connection("gsheets", type=GSheetsConnection)
# 설명 텍스트
st.subheader("각 탭에서 동일한 문항에 대해 1~5점 사이의 점수를 선택하고 각 탭에서 제출하세요.")

# 문항 리스트
questions = [
    "NGO의 목표와 활동 계획이 공정성과 인류애를 잘 반영했나요?",
    "활동 내용이 실현 가능하고 현실적인 해결 방안을 제시했나요?",
    "포스터, 뉴스 대본, 영상 등 홍보물이 창의적으로 제작되었나요?",
    "홍보물에 NGO의 가치와 메시지가 명확히 전달되었나요?",
    "뉴스 발표가 흥미롭고 설득력 있게 전달되었나요?",
    "발표 내용이 시청자의 관심을 끌고 몰입하게 만들었나요?",
    "갈등 해결 방안이 논리적이고 체계적으로 제시되었나요?",
    "데이터나 시뮬레이션 결과를 적절히 활용했나요?",
    "발표와 홍보물 제작에서 팀원들의 협력이 잘 드러났나요?",
    "팀의 메시지가 일관되게 표현되었나요?",
    "전체적으로 NGO의 활동과 발표가 강렬하고 설득력 있었나요?",
    "지구촌 문제 해결에 대한 진정성과 열정이 느껴졌나요?",
    "가장 인상 깊었던 점은 무엇인가요?",
    "개선하거나 더 발전시킬 점이 있다면 무엇인가요?"
]

# 질문 그룹화
question_groups = {
    "**1. 활동 내용의 공정성과 실현 가능성 (5점 만점)**": questions[:2],  # 질문 1~2
    "**2. 홍보물의 창의성과 메시지 전달력 (5점 만점)**": questions[2:4],  # 질문 3~4
    "**3. 발표의 설득력과 몰입감 (5점 만점)**": questions[4:6],  # 질문 5~6
    "**4. 문제 해결 접근 방식의 논리성 (5점 만점)**": questions[6:8],  # 질문 7~8
    "**5. 팀워크와 협업의 표현 (5점 만점)**": questions[8:10],  # 질문 9~10
    "**6. 전반적인 인상 (5점 만점)**": questions[10:12],  # 질문 11~12
    "**추가 의견 (선택사항)**": questions[12:14]  # 질문 13~14
}

# 탭 이름과 Google Sheets 이름 매핑
tab_names = ["팀 RNC(Refugee Never Cry)", "팀 BLUE ROSE", "팀 HAPPY Kids", "팀 C.F.W(Children Free From Work)"]
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
        st.subheader(f"📍 {tab_name}의 발표가 어땠나요?")
        st.write("")
        st.write("")
        # st.subheader("동료평가 기준 문항")
        scores = []

        # 각 질문에 대한 점수 입력
        for group_name, group_questions in question_groups.items():
            st.markdown(f"{group_name}")
            # st.write("이 그룹에서는 관련된 문항을 종합적으로 평가해 주세요.")
            for i, question in enumerate(group_questions):
                question_index = questions.index(question)  # 전체 질문에서 인덱스 확인
                
                score = st.radio(
                    f"**{question}**",  # 질문 제목
                    options=[1, 2, 3, 4, 5],  # 점수
                    index=st.session_state["scores_by_tab"][tab_name][question_index] - 1,
                    key=f"{tab_name}_Q{question_index}",  # 고유 키
                    horizontal=True
                )
                scores.append(score)
            st.write("")
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
