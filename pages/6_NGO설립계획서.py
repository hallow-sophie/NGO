import os
import streamlit as st
import time
from openai import OpenAI
from PIL import Image
import io
import requests
from PyPDF2 import PdfReader
import pdfplumber

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

api_key = st.secrets.openAI["api_key"]
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 탭 구성
tab1, tab2, tab3 = st.tabs(["AI 인물들에게 물어보기", "NGO 로고 생성","뉴스기사 첨삭"])

# 상태 초기화
if "responses" not in st.session_state:
    st.session_state["responses"] = []

if "uploaded_file_content" not in st.session_state:
    st.session_state["uploaded_file_content"] = None

if "pdf_file_content" not in st.session_state:
    st.session_state["pdf_file_content"] = None

if "image_url" not in st.session_state:
    st.session_state["image_url"] = None

if "user_query" not in st.session_state:
    st.session_state["user_query"] = "빈부격차는 어떻게 분배해야 할까?"

def generate_logo(content):
    with st.spinner("AI가 LOGO 를 그리고 있는 중이에요..."):
        response = client.images.generate(
            model="dall-e-3",
            prompt=content,
            n=1,
            size="1024x1024"
        )
    return response.data[0].url

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

with tab2:
    # Streamlit 앱 제목
    st.header("NGO 로고 생성")

    # 파일 업로드
    uploaded_file = st.file_uploader("PDF 파일을 업로드하면 LOGO를 생성해줘요.", type="pdf")

    def clean_text(text):
        # \n을 공백으로 대체
        text = text.replace("\n", " ")
        # 불필요한 중복 공백 제거
        text = " ".join(text.split())
        return text

    # PDF 파일 읽기
    if uploaded_file is not None:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                tables0 = pdf.pages[0].extract_tables()
                tables1 = pdf.pages[1].extract_tables()
            
            pdf_text = ""
            pdf_text = pdf_text + clean_text("우리 NGO Project의 " + tables0[0][0][0] + "는 " + tables0[0][0][1] + "이야")
            pdf_text = pdf_text + clean_text("그리고 우리 NGO Project의 " + tables1[0][0][0] + "는 " + tables1[0][0][1] + "이야")

            logo_maker = "다음 이어지는 내용을 기반으로 NGO 단체의 로고를 독창적으로 작성해줘."
            file_content = logo_maker + pdf_text
            st.session_state["pdf_file_content"] = file_content  # 파일 내용을 세션에 저장

        except Exception as e:
            st.error(f"PDF 파일을 읽는 중 오류가 발생했습니다: {e}")

    if st.session_state["pdf_file_content"] is not None:
        if st.button("로고 생성하기", key="generate_logo_button"):
            st.session_state["image_url"] = generate_logo(st.session_state["pdf_file_content"])

        # 이전에 생성된 이미지 표시
        if st.session_state["image_url"]:
            st.image(st.session_state["image_url"], caption="AI가 추천해주는 LOGO", use_container_width=True)
            st.write("LOGO Image 저장중...")
            image_response = requests.get(st.session_state["image_url"])  # 이미지 URL에서 이미지 다운로드
            image = Image.open(io.BytesIO(image_response.content))
            image_save_path = os.path.join(user_folder, "PDF_LOGO.png")
            image.save(image_save_path)

            st.success(f"Image saved at: {image_save_path}")

# Tab 3: 뉴스기사 첨삭
with tab3:
    st.header("뉴스기사 첨삭하기")
    system_roles = [
        {
            "role": "system",
            "content": "너는 기사를 아주 잘 쓰는 기자야. 주어진 기사를 잘 첨삭해서 고칠 부분을 알려줘. 너무 어려운 단어는 지양부탁해.",
        }
    ]
    current_chat = system_roles
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
        
    # 파일 업로드
    uploaded_file = st.file_uploader("PDF 파일을 업로드하면 기사를 첨삭해줘요.", type="pdf")

    def clean_text(text):
        # \n을 공백으로 대체
        text = text.replace("\n", " ")
        # 불필요한 중복 공백 제거
        text = " ".join(text.split())
        return text

    # PDF 파일 읽기
    query = "아래에 주어진 내용들 중에 고칠 부분들을 종류별로 알려줘. 맞춤법/문맥/자연스러움 정도로 나눠서 알려줘."
    if uploaded_file is not None:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    # 페이지에서 테이블 추출
                    imsi = page.extract_text()
                    query = query + imsi
        except Exception as e:
            st.error(f"PDF 파일을 읽는 중 오류가 발생했습니다: {e}")

    current_chat.append({"role": "user", "content": query})

    with st.spinner(f"첨삭이 진행 중 입니다..."):
        response = generate_response(current_chat)
    current_chat.append({"role": "assistant", "content": response})
    st.write(response)
