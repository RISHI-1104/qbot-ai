import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Qbot.ai",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; }
    .stChatMessage { border-radius: 15px; }
    h1 { color: #00ff88 !important; text-align: center; }
    .stCaptionContainer { text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Qbot.ai")
st.caption("Your intelligent AI companion — V2")

api_key = st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    st.error("API key not found!")
    st.stop()

client = Groq(api_key=api_key)

# Qbot personality
SYSTEM_PROMPT = """You are Qbot.ai — a smart, friendly and witty AI assistant.
Your personality:
- You are helpful, funny and engaging
- You use simple language everyone understands
- You can respond in English, Tamil, or Hindi based on what language the user writes in
- You give short answers for simple questions, detailed answers for complex ones
- You are encouraging and positive
- Your name is Qbot.ai, created by a talented developer for their portfolio
- You never say you are Claude or made by Anthropic
"""

# Answer mode selector
mode = st.selectbox(
    "Answer mode",
    ["💬 Normal", "🎯 Simple & Short", "📚 Detailed", "🎨 Creative"],
    index=0
)

mode_instructions = {
    "💬 Normal": "",
    "🎯 Simple & Short": "Keep your answer very short and simple — maximum 3 sentences.",
    "📚 Detailed": "Give a very detailed, thorough explanation with examples.",
    "🎨 Creative": "Answer in a creative, fun and imaginative way with storytelling style."
}

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
        try:
            system = SYSTEM_PROMPT
            if mode_instructions[mode]:
                system += f"\n\nCurrent answer mode: {mode_instructions[mode]}"

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system},
                    *[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages]
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Clear chat button
if st.button("🗑️ Clear chat"):
    st.session_state.messages = []
    st.rerun()
