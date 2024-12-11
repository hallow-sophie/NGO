import os
import streamlit as st
import time
from openai import OpenAI
from PIL import Image
import io
import requests

# 로그인 상태 확인
if "ID" not in st.session_state or st.session_state['ID'] == None:
    st.warning("로그인이 필요합니다. 로그인 페이지로 이동합니다.")
    time.sleep(2)
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

# api_key = ""
client = OpenAI(api_key=api_key) # api_key를 통해 생성


# 여러 시스템 역할 정의
system_roles = [
    {"persona":"아리스토텔레스", "role": "system", "content": "당신은 질문을 논리력을 바탕으로 정확한 답변을 제공하는 조수입니다."},
    {"persona":"바보온달","role": "system", "content": "당신은 질문을 받으면 이상하고 엉터리 답변만을 제공하는 바보입니다."},
    {"persona":"네로","role": "system", "content": "당신은 주어진 질문에 대한 답에는 관심이 없고, 오직 부자들의 입장만 대변해주는 아주 아주 나쁜사람입니다."},
    {"persona":"소크라테스","role": "system", "content": "당신은 철학적인 관점에서 답변을 제공하는 사색가입니다."},
]

user_query = st.text_input("Enter your query:", value="빈부격차는 어떻게 분배해야 할까?")
responses = []

if st.button("인물들에게 물어보기."):
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
            responses.append({"role": system_role["persona"], "response": completion.choices[0].message.content})

    # 가로 레이아웃에 응답 표시
    cols = st.columns(len(responses))  # 역할 개수만큼 열 생성
    for col, response in zip(cols, responses):
        with col:
            st.subheader(f"인물")
            st.markdown(f"**{response['role']}**")
            st.write(response["response"])


uploaded_file = st.file_uploader("Upload a text file for image generation", type=["txt"])

if uploaded_file:
    # 파일 저장
    file_path = os.path.join(user_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    file_content = uploaded_file.getvalue().decode("utf-8").strip()

    st.write("Generating an image based on the uploaded file...")
    with st.spinner("Generating image..."):
        response = client.images.generate(
            model="dall-e-3",
            prompt=file_content,  # 파일 내용을 프롬프트로 사용
            n=1,
            size="1024x1024"
        )

    image_url = response.data[0].url

    # 이미지를 표시
    st.image(image_url, caption="AI가 추천해주는 LOGO", use_container_width=True)

    # 이미지 파일 다운로드 및 저장
    st.write("LOGO Image 저장중...")
    image_response = requests.get(image_url)  # 이미지 URL에서 이미지 다운로드
    image = Image.open(io.BytesIO(image_response.content))
    image_save_path = os.path.join(user_folder, "AI_LOGO.png")
    image.save(image_save_path)

    st.success(f"Image saved at: {image_save_path}")
