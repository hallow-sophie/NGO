import streamlit as st
from openai import OpenAI
import os
import time

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

# OpenAI API 초기화
client = OpenAI(api_key=api_key)

st.title("💬 인터뷰를 해봐요.")

# 시스템 역할 설정
system_roles = {
    "소말리아 난민": {
        "role": "system",
        "content": "당신은 인공지능이 아니라, 전쟁과 극심한 빈곤상태에서 살아온 소말리아인입니다.  인터뷰어가 당신을 인터뷰를 진행할 예정 입니다.",
        "image": "images/refugee.jpg"
    },
    "가난속에서 굶주린 국민": {
        "role": "system",
        "content": "당신은 인공지능이 아니라, 극심한 가난 상태에서 살아왔습니다. 인터뷰어가 당신을 인터뷰를 진행할 예정 입니다.",
        "image": "images/ganan.jpg"
    },
    "전쟁을 겪고 있는 국민": {
        "role": "system",
        "content": "당신은 인공지능이 아니라, 전쟁속에서 고통받고 있습니다. 우크라이나인입니다.  인터뷰어가 당신을 인터뷰를 진행할 예정 입니다.",
        "image": "images/war.jpg"
    }
}

# 캐릭터별 대화 기록 초기화
if "chat_histories" not in st.session_state:
    st.session_state["chat_histories"] = {
        role: [details] for role, details in system_roles.items()
    }

# 선택된 캐릭터 상태 초기화
if "selected_role" not in st.session_state:
    st.session_state["selected_role"] = "소말리아 난민"

# 캐릭터 선택 UI
st.write("대화할 캐릭터를 선택하세요:")
columns = st.columns(len(system_roles))  # 선택지에 따라 컬럼 생성

for i, (name, role) in enumerate(system_roles.items()):
    with columns[i]:
        image_path = os.path.join(os.path.dirname(__file__), role["image"])
        st.image(image_path)  # 캐릭터 이미지 표시
        if st.button(name):  # 이름으로 버튼 생성
            st.session_state["selected_role"] = name  # 선택된 캐릭터 변경
            if len(st.session_state["chat_histories"][name]) == 1:
                # 초기 메시지 유지
                st.session_state["chat_histories"][name].append({"role": "system", "content": role["content"]})

# 선택된 대화 상대
selected_role = st.session_state["selected_role"]
st.write(f"**{selected_role}**와 인터뷰를 진행 중입니다.")

# 현재 캐릭터의 대화 기록 가져오기
current_chat = st.session_state["chat_histories"][selected_role]

# 챗봇 응답 생성 함수
def generate_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # GPT 모델
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}")
        return "오류가 발생했습니다. 다시 시도해주세요."

# 사용자 입력 필드
user_input = st.chat_input("대화를 입력하세요!")
if user_input:
    # 사용자 메시지 추가
    current_chat.append({"role": "user", "content": user_input})

    # OpenAI 응답 생성
    with st.spinner(f"{selected_role}이(가) 응답 중입니다..."):
        response = generate_response(current_chat)

    # 챗봇 응답 저장
    current_chat.append({"role": "assistant", "content": response})

# 대화 기록 표시
for message in current_chat:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant").markdown(message["content"])

# 캐릭터별 대화 기록 업데이트
st.session_state["chat_histories"][selected_role] = current_chat
