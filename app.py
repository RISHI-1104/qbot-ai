import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Qbot.ai",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Qbot.ai")
st.caption("Your AI assistant — powered by Groq")

api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("API key not found! Check your secrets.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Qbot.ai anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
