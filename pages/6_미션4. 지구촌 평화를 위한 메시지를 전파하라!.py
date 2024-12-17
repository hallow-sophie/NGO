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

# api_key = st.secrets.openAI["api_key"]
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 탭 구성
tab1, tab2, tab3 = st.tabs(["AI 인물들과의 인터뷰", "NGO 로고 생성","뉴스기사 첨삭"])

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
    st.header("💬 인터뷰를 해봐요.")

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
        },
        "우크라이나 전쟁으로 고통받는 안나": {
        "role": "system",
        "content": "당신은 인공지능이 아니라, 전쟁속에서 고통받고 있습니다. 우크라이나인입니다.  인터뷰어가 당신을 인터뷰를 진행할 예정 입니다.",
        "image": "images/anna.jpg"
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
        logo_maker = "다음 이어지는 내용을 기반으로 NGO 단체의 로고를 글자없이 독창적으로 그려줘. 그림에는 글자가 들어가면 절대 안돼."
        if uploaded_file is not None:
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        # 페이지에서 테이블 추출
                        imsi = page.extract_text()
                        logo_maker = logo_maker + imsi
            except Exception as e:
                st.error(f"PDF 파일을 읽는 중 오류가 발생했습니다: {e}")

            st.session_state["pdf_file_content"] = logo_maker  # 파일 내용을 세션에 저장

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
