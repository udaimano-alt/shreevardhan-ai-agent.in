import streamlit as st
from google import genai

st.title("Shreevardhan's AI")

client = genai.Client(api_key=st.secrets[""])

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model="gemini-3.6-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    response = st.session_state.chat.send_message(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
