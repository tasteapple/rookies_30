from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

st.title('ChatGPT Chatbot')

# 대화 내용 저장
# openai => GPT 모델 변수로 저장
if 'openai_model' not in st.session_state:
    st.session_state.openai_model = 'gpt-5.2' # openai_model이라는 변수를 만들고 해당 변수에 gpt-5.2 문자열을 저장

# 대화 내용 저장
# messages => []
# message 초기 세팅
if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg['role']): # chat_message : 역할에 따라 메시지 구분
        st.markdown(msg['content'])


# prompt => 사용자 입력창
# := 할당 표현식 -- 변수에 값을 할당하면서 동시에 그 값을 평가
if prompt := st.chat_input('메시지를 입력하세요'):
    # messages 내용 추가
    # "role", "content"
    st.session_state.messages.append(
        {
            "role" : "user",
            "content" : prompt
        }
    )

    with st.chat_message('user'):
        st.markdown(prompt)
    
    # with st.chat_message('assistant'):
    #     stream = client.responses.create(
    #         model = st.session_state.openai_model,
    #         input=[
    #             {
    #                 "role" : m['role'],
    #                 "content" : m['content']
    #             }for m in st.session_state.messages
    #         ],
    #         stream = True
    #     )
    #     response = st.write_stream(stream)
    
    with st.chat_message('assistant'):
        stream = client.chat.completions.create(
            model=st.session_state.openai_model,
            messages=[
                {"role": m['role'], "content": m['content']}
                for m in st.session_state.messages
            ],
            stream=True
        )
        response = st.write_stream(stream)

        st.session_state.messages.append(
            {
                "role" : "assistant",
                "content" : response
            }
        )