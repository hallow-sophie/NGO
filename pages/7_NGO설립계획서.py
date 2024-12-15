import os
import streamlit as st
import time
from openai import OpenAI
from PIL import Image
import io
import requests

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] is None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(1)
    st.session_state["redirect"] = True
    st.switch_page("pages/2_login.py")

# 사용자별 파일 저장 경로
UPLOAD_FOLDER = "user_uploads"

# 유저 세션 ID를 기반으로 사용자별 디렉토리 설정
user_id = st.session_state["ID"]  # 로그인 시 저장된 사용자 ID
user_folder = os.path.join(UPLOAD_FOLDER, user_id)

# 사용자별 디렉토리 생성
os.makedirs(user_folder, exist_ok=True)

# Streamlit 앱 설정
st.title("NGO 설립계획서")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 탭 구성
tab1, tab2 = st.tabs(["AI 인물들에게 물어보기", "NGO 로고 생성"])

# 상태 초기화
if "responses" not in st.session_state:
    st.session_state["responses"] = []

if "uploaded_file_content" not in st.session_state:
    st.session_state["uploaded_file_content"] = None

if "image_url" not in st.session_state:
    st.session_state["image_url"] = None

if "user_query" not in st.session_state:
    st.session_state["user_query"] = "빈부격차는 어떻게 분배해야 할까?"

# Tab 1: AI 인물들에게 물어보기
with tab1:
    st.header("AI 인물들에게 물어보기")

    # 여러 시스템 역할 정의
    system_roles = [
        {"persona": "아인슈타인", "role": "system", "content": "당신은 질문을 논리력을 바탕으로 정확한 답변을 제공하는 조수입니다."},
        {"persona": "바보온달", "role": "system", "content": "당신은 질문을 받으면 이상하고 엉터리 답변만을 제공하는 바보입니다."},
        {"persona": "이완용", "role": "system", "content": "당신은 주어진 질문에 대한 답에는 관심이 없고, 오직 부자들의 입장만 대변해주는 아주 나쁜사람입니다."},
        {"persona": "세종대왕", "role": "system", "content": "당신은 철학적인 관점에서 답변을 제공하는 사색가입니다."},
    ]

    # 입력값 상태 관리
    user_query = st.text_input(
        "Enter your query:", 
        value=st.session_state["user_query"], 
        key="query_input_tab1"
    )

    if st.button("인물들에게 물어보기.", key="ask_ai_button"):
        st.session_state["responses"] = []  # 이전 응답 초기화
        st.session_state["user_query"] = user_query  # 입력값 동기화
        with st.spinner("인물들이 고심중입니다..."):
            for system_role in system_roles:
                # OpenAI API 호출
                completion = client.chat.completions.create(
                    model="gpt-4o",  # 모델 설정
                    messages=[
                        system_role,  # 현재 시스템 역할
                        {
                            "role": "user",
                            "content": user_query + "초등학생도 이해할 정도로 쉽게 이야기해줘. 그리고 한 두 문장으로 짧게 이야기해줘.",  # 사용자의 질문
                        }
                    ]
                )
                # 응답 저장
                st.session_state["responses"].append({"role": system_role["persona"], "response": completion.choices[0].message.content})

    # 이전 응답 표시
    if st.session_state["responses"]:
        cols = st.columns(len(st.session_state["responses"]))  # 역할 개수만큼 열 생성
        for col, response in zip(cols, st.session_state["responses"]):
            with col:
                st.subheader(f"인물")
                st.markdown(f"**{response['role']}**")
                st.write(response["response"])

# Tab 2: NGO 로고 생성
with tab2:
    st.header("NGO 로고 생성")

    uploaded_file = st.file_uploader(
        "text file을 업로드하면 LOGO를 생성해줘요.", 
        type=["txt"], 
        key="file_uploader_tab2"
    )

    if uploaded_file:
        # 파일 저장
        file_path = os.path.join(user_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

        logo_maker = "다음 이어지는 내용을 기반으로 NGO 단체의 로고를 독창적으로 작성해줘."
        file_content = logo_maker + uploaded_file.getvalue().decode("utf-8").strip()
        st.session_state["uploaded_file_content"] = file_content  # 파일 내용을 세션에 저장

    # 이미지를 생성하는 함수
    def generate_logo(content):
        with st.spinner("AI가 LOGO 를 그리고 있는 중이에요..."):
            response = client.images.generate(
                model="dall-e-3",
                prompt=content,
                n=1,
                size="1024x1024"
            )
        return response.data[0].url

    # 로고 생성 버튼
    if st.session_state["uploaded_file_content"] is not None:
        if st.button("로고 생성하기", key="generate_logo_button"):
            st.session_state["image_url"] = generate_logo(st.session_state["uploaded_file_content"])

        # 이전에 생성된 이미지 표시
        if st.session_state["image_url"]:
            st.image(st.session_state["image_url"], caption="AI가 추천해주는 LOGO", use_container_width=True)
            st.write("LOGO Image 저장중...")
            image_response = requests.get(st.session_state["image_url"])  # 이미지 URL에서 이미지 다운로드
            image = Image.open(io.BytesIO(image_response.content))
            image_save_path = os.path.join(user_folder, "AI_LOGO.png")
            image.save(image_save_path)

            st.success(f"Image saved at: {image_save_path}")
