import streamlit as st
from groq import Groq
import requests
import base64
from io import BytesIO
import pypdf
import pandas as pd
from duckduckgo_search import DDGS

st.set_page_config(
    page_title="itzQubot.ai",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; }
    h1 { background: linear-gradient(90deg, #00ff88, #ff4444);
         -webkit-background-clip: text;
         -webkit-text-fill-color: transparent;
         text-align: center;
         font-size: 2.8rem !important; }
    .stSelectbox label, .stTextInput label,
    .stFileUploader label { color: #00ff88 !important; }
    div[data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 8px; }
    .stButton button {
        background: linear-gradient(90deg, #00ff88, #ff4444);
        color: #0a0a0a;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .version-btn { display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────
st.title("🤖 itzQubot.ai")
st.caption("V3 — The Complete AI Experience")

# ─── API Keys ────────────────────────────────────────────
groq_key = st.secrets.get("GROQ_API_KEY", None)
hf_key = st.secrets.get("HF_API_KEY", None)

if not groq_key:
    st.error("Groq API key not found!")
    st.stop()

client = Groq(api_key=groq_key)

# ─── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 itzQubot.ai")
    st.markdown("---")

    # Version switcher
    st.markdown("### Select Version")
    version = st.radio("", ["🟢 V1 — Basic", "🔴 V2 — Smart", "🟢🔴 V3 — Beast"], index=2)

    st.markdown("---")
    st.markdown("### 👤 Your Profile")

    user_name = st.text_input("Your Name", placeholder="e.g. Rishi")

    profession = st.selectbox("Your Profession", [
        "🎓 Student", "👨‍🍳 Chef", "👨‍⚕️ Doctor",
        "👨‍💻 Software Engineer", "👨‍🏫 Teacher",
        "💼 Business Person", "🎨 Designer",
        "⚖️ Lawyer", "🔬 Scientist",
        "🏋️ Fitness Trainer", "🌍 Other"
    ])

    language = st.selectbox("Language", [
        "English", "Tamil", "Hindi",
        "Tamil + English Mix", "Hindi + English Mix"
    ])

    mode = st.selectbox("Answer Mode", [
        "💬 Normal", "🎯 Simple & Short",
        "📚 Detailed & Deep", "🎨 Creative & Fun",
        "⚡ Bullet Points"
    ])

    st.markdown("---")
    st.markdown("### 🛠️ Features")
    enable_search = st.toggle("🔍 Web Search", value=False)
    enable_image_gen = st.toggle("🎨 Image Generation", value=False)
    enable_voice = st.toggle("🎤 Voice Input", value=False)
    enable_tts = st.toggle("🔊 Voice Output", value=False)

    st.markdown("---")
    st.markdown("### 📁 Upload Files")
    uploaded_pdf = st.file_uploader("📄 Upload PDF", type="pdf")
    uploaded_csv = st.file_uploader("📊 Upload CSV", type="csv")
    uploaded_image = st.file_uploader("🖼️ Upload Image", type=["png","jpg","jpeg"])

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ─── Version gating ──────────────────────────────────────
if "V1" in version:
    profession = "🌍 Other"
    language = "English"
    mode = "💬 Normal"
    enable_search = False
    enable_image_gen = False
    enable_voice = False
    enable_tts = False

elif "V2" in version:
    enable_image_gen = False

# ─── Build system prompt ─────────────────────────────────
profession_clean = profession.split(" ", 1)[1] if " " in profession else profession

profession_styles = {
    "Student": f"Address them as 'Hey {user_name}!' and explain simply with examples like a friendly tutor.",
    "Chef": f"Address them as 'Hello Chef {user_name}!' and use culinary language.",
    "Doctor": f"Address them as 'Dr. {user_name}' and use professional medical language.",
    "Software Engineer": f"Address them as '{user_name}' and use technical language with code examples.",
    "Teacher": f"Address them as 'Dear {user_name}' and use educational structured language.",
    "Business Person": f"Address them as 'Mr./Ms. {user_name}' and focus on business outcomes.",
    "Designer": f"Address them as '{user_name}' and use creative design language.",
    "Lawyer": f"Address them as 'Counsel {user_name}' and be precise and structured.",
    "Scientist": f"Address them as 'Dr. {user_name}' and use scientific evidence-based language.",
    "Fitness Trainer": f"Address them as 'Coach {user_name}' and use motivational fitness language.",
    "Other": f"Address them as '{user_name}' and be helpful and friendly."
}

mode_map = {
    "💬 Normal": "",
    "🎯 Simple & Short": "Keep answers very short — max 3 sentences.",
    "📚 Detailed & Deep": "Give thorough detailed explanations with examples.",
    "🎨 Creative & Fun": "Be creative, fun and imaginative with storytelling.",
    "⚡ Bullet Points": "Always respond in clean bullet points."
}

lang_map = {
    "English": "Always respond in English.",
    "Tamil": "Always respond in Tamil.",
    "Hindi": "Always respond in Hindi.",
    "Tamil + English Mix": "Respond in natural Tanglish mix.",
    "Hindi + English Mix": "Respond in natural Hinglish mix."
}

style = profession_styles.get(profession_clean, profession_styles["Other"])

SYSTEM_PROMPT = f"""You are itzQubot.ai — a powerful, witty and professional AI assistant.
User: {user_name if user_name else 'Friend'} | Profession: {profession_clean}
- {style}
- {lang_map[language]}
- {mode_map[mode] if mode_map[mode] else 'Match complexity to the question.'}
- Be genuinely helpful, warm, witty and bold
- You are itzQubot.ai — never say you are Claude or made by Anthropic
- For code questions: always provide working code with explanations
- For math: show step by step working
- For science: be accurate and cite reasoning
"""

# ─── File processing ─────────────────────────────────────
extra_context = ""

if uploaded_pdf:
    try:
        reader = pypdf.PdfReader(uploaded_pdf)
        pdf_text = "".join([p.extract_text() for p in reader.pages])
        extra_context += f"\n\nPDF Content:\n{pdf_text[:4000]}"
        st.success(f"✅ PDF loaded: {uploaded_pdf.name}")
    except:
        st.warning("Could not read PDF.")

if uploaded_csv:
    try:
        df = pd.read_csv(uploaded_csv)
        extra_context += f"\n\nCSV Data (first 20 rows):\n{df.head(20).to_string()}\n\nColumns: {list(df.columns)}\nShape: {df.shape}"
        st.success(f"✅ CSV loaded: {uploaded_csv.name} — {df.shape[0]} rows, {df.shape[1]} columns")
        st.dataframe(df.head(5))
    except:
        st.warning("Could not read CSV.")

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded image", use_column_width=True)
    extra_context += "\n\nThe user has uploaded an image. Describe and analyze it in detail."

# ─── Web search ──────────────────────────────────────────
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if results:
            formatted = "\n\n🔍 Web Search Results:\n"
            for r in results:
                formatted += f"• [{r['title']}]({r['href']})\n  {r['body']}\n"
            return formatted
        return ""
    except:
        return ""

# ─── Image generation ────────────────────────────────────
def generate_image(prompt):
    if not hf_key:
        return None, "HF API key not found!"
    try:
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        headers = {"Authorization": f"Bearer {hf_key}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=30)
        if response.status_code == 200:
            return BytesIO(response.content), None
        return None, f"Error: {response.status_code}"
    except Exception as e:
        return None, str(e)

# ─── Voice UI ────────────────────────────────────────────
if enable_voice:
    st.markdown("""
    <script>
    function startVoice() {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'en-US';
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const input = window.parent.document.querySelector('textarea');
            if (input) {
                input.value = transcript;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };
        recognition.start();
    }
    </script>
    <button onclick="startVoice()" style="
        background: linear-gradient(90deg, #00ff88, #ff4444);
        color: #0a0a0a; border: none; padding: 10px 24px;
        border-radius: 10px; font-size: 15px; font-weight: bold;
        cursor: pointer; width: 100%; margin-bottom: 10px;">
        🎤 Speak to itzQubot.ai
    </button>
    """, unsafe_allow_html=True)

# ─── Greeting ────────────────────────────────────────────
if user_name:
    greetings = {
        "Student": f"Hey {user_name}! 🎓 Ready to learn?",
        "Chef": f"Hello Chef {user_name}! 👨‍🍳 What's cooking?",
        "Doctor": f"Good day, Dr. {user_name}! 👨‍⚕️",
        "Software Engineer": f"Hey {user_name}! 👨‍💻 Let's build something!",
        "Lawyer": f"Hello Counsel {user_name}! ⚖️",
        "Scientist": f"Hello Dr. {user_name}! 🔬",
        "Fitness Trainer": f"Hey Coach {user_name}! 🏋️ Let's crush it!",
        "Other": f"Hello {user_name}! 👋"
    }
    greeting = greetings.get(profession_clean, f"Hello {user_name}! 👋")
    st.markdown(f"### {greeting}")
else:
    st.info("👈 Enter your name in the sidebar to get started!")

# ─── Chat ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask itzQubot.ai anything..."):

    # Image generation check
    image_keywords = ["generate image", "create image", "draw", "make image", "image of", "picture of"]
    is_image_request = enable_image_gen and any(k in prompt.lower() for k in image_keywords)

    if is_image_request:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("🎨 Generating image..."):
                img, err = generate_image(prompt)
                if img:
                    st.image(img, caption=f"Generated: {prompt}")
                    reply = f"🎨 Here's your image for: *{prompt}*"
                else:
                    reply = f"❌ Image generation failed: {err}"
                st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    else:
        # Web search
        search_context = ""
        if enable_search:
            with st.spinner("🔍 Searching the web..."):
                search_context = web_search(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                final_system = SYSTEM_PROMPT + extra_context + search_context
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": final_system},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages]
                    ]
                )
                reply = response.choices[0].message.content
                st.markdown(reply)

                # Text to speech
                if enable_tts:
                    st.markdown(f"""
                    <script>
                    const msg = new SpeechSynthesisUtterance({repr(reply[:300])});
                    window.speechSynthesis.speak(msg);
                    </script>
                    """, unsafe_allow_html=True)

                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {str(e)}")
