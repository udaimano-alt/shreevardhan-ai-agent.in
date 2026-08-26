import streamlit as st
from google import genai

st.set_page_config(page_title="Shreevardhan's AI", page_icon="🤖")
st.title("Shreevardhan's AI")

def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "chat" not in st.session_state:
    st.session_state.client = get_client()
    st.session_state.chat = st.session_state.client.chats.create(model="gemini-3.6-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    try:
        response = st.session_state.chat.send_message(user_input)
    except RuntimeError:
        # Client closed unexpectedly — recreate and retry
        st.session_state.client = get_client()
        st.session_state.chat = st.session_state.client.chats.create(model="gemini-3.6-flash")
        response = st.session_state.chat.send_message(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
