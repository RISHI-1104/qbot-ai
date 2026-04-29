import streamlit as st
from groq import Groq
import pypdf
import io

st.set_page_config(
    page_title="Qbot.ai",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; }
    h1 { color: #00ff88 !important; text-align: center; font-size: 2.5rem !important; }
    .stCaptionContainer { text-align: center; }
    .stSelectbox label, .stTextInput label, .stFileUploader label { color: #00ff88 !important; }
    div[data-testid="stChatMessage"] { border-radius: 15px; margin-bottom: 8px; }
    .stButton button {
        background-color: #00ff88;
        color: #0a0a0a;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .stButton button:hover { background-color: #00cc66; }
    .stSidebar { background-color: #111111 !important; }
    </style>
""", unsafe_allow_html=True)

# ── Voice Input JS ──────────────────────────────────────
st.markdown("""
<script>
function startVoice() {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Voice not supported. Use Chrome browser!');
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.onstart = function() {
        document.getElementById('voiceBtn').innerText = '🔴 Listening...';
    };
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const inputs = window.parent.document.querySelectorAll('textarea');
        inputs.forEach(input => {
            input.value = transcript;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
        document.getElementById('voiceBtn').innerText = '🎤 Speak to Qbot.ai';
    };
    recognition.onerror = function() {
        document.getElementById('voiceBtn').innerText = '🎤 Speak to Qbot.ai';
    };
    recognition.onend = function() {
        document.getElementById('voiceBtn').innerText = '🎤 Speak to Qbot.ai';
    };
    recognition.start();
}
</script>
""", unsafe_allow_html=True)

st.title("🤖 Qbot.ai")
st.caption("Your intelligent AI companion — V3 Ultimate")

api_key = st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    st.error("API key not found! Check your secrets.")
    st.stop()

client = Groq(api_key=api_key)

# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👤 Your Profile")
    st.markdown("---")

    user_name = st.text_input("Your Name", placeholder="e.g. Riyaz")

    profession = st.selectbox("Your Profession", [
        "🎓 Student",
        "👨‍🍳 Chef",
        "👨‍⚕️ Doctor",
        "👨‍💻 Software Engineer",
        "👨‍🏫 Teacher",
        "💼 Business Person",
        "🎨 Designer",
        "⚖️ Lawyer",
        "🏗️ Civil Engineer",
        "📊 Data Analyst",
        "🎵 Musician",
        "✍️ Writer",
        "🔬 Scientist",
        "🏋️ Fitness Trainer",
        "🌍 Other"
    ])

    language = st.selectbox("Preferred Language", [
        "English",
        "Tamil",
        "Hindi",
        "Tamil + English Mix",
        "Hindi + English Mix"
    ])

    mode = st.selectbox("Answer Mode", [
        "💬 Normal",
        "🎯 Simple & Short",
        "📚 Detailed & Deep",
        "🎨 Creative & Fun",
        "⚡ Bullet Points"
    ])

    st.markdown("---")
    st.markdown("### 📄 Chat with PDF")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About Qbot.ai")
    st.markdown("V3 Ultimate • Powered by Groq")
    st.markdown("Built for portfolio by a talented developer 🚀")

# ── Profession Styles ────────────────────────────────────
profession_clean = profession.split(" ", 1)[1] if " " in profession else profession

profession_styles = {
    "Student":          f"Address them as 'Hey {user_name}! 🎓' and explain everything simply with relatable examples like a friendly tutor. Use analogies, encourage them and be patient.",
    "Chef":             f"Address them as 'Hello Chef {user_name}! 👨‍🍳' and use culinary language. Relate answers to cooking, recipes and the kitchen when possible.",
    "Doctor":           f"Address them as 'Dr. {user_name}' and use professional medical language. Be precise, clinical and evidence-based.",
    "Software Engineer":f"Address them as '{user_name}' and use technical language with code examples when relevant. Be concise and direct.",
    "Teacher":          f"Address them as 'Dear {user_name}' and use structured, educational language with pedagogical approaches.",
    "Business Person":  f"Address them as 'Mr./Ms. {user_name}' and focus on ROI, efficiency and business outcomes. Be sharp and professional.",
    "Designer":         f"Address them as '{user_name}' and use creative language referencing design principles, aesthetics and visual thinking.",
    "Lawyer":           f"Address them as 'Counsel {user_name}' and be precise, structured and reference legal thinking when relevant.",
    "Civil Engineer":   f"Address them as 'Engineer {user_name}' and use structural, technical language with practical real-world examples.",
    "Data Analyst":     f"Address them as '{user_name}' and use data-driven language with statistics references and analytical thinking.",
    "Musician":         f"Address them as '{user_name}' and use musical references, rhythm and creative language throughout.",
    "Writer":           f"Address them as '{user_name}' and use rich, literary language referencing storytelling and narrative techniques.",
    "Scientist":        f"Address them as 'Dr. {user_name}' and use scientific, evidence-based language with references to research and data.",
    "Fitness Trainer":  f"Address them as 'Coach {user_name}! 💪' and use motivational, energetic, fitness-oriented language.",
    "Other":            f"Address them as '{user_name}' and be helpful, warm and friendly."
}

mode_instructions = {
    "💬 Normal":        "",
    "🎯 Simple & Short":"Keep answers very short — max 3 sentences. Be direct and clear.",
    "📚 Detailed & Deep":"Give thorough, detailed explanations with examples and full depth.",
    "🎨 Creative & Fun":"Be creative, fun and imaginative. Use storytelling and light humor.",
    "⚡ Bullet Points": "Always respond in clean bullet points. Structured and scannable."
}

language_instructions = {
    "English":              "Always respond in English.",
    "Tamil":                "Always respond in Tamil language.",
    "Hindi":                "Always respond in Hindi language.",
    "Tamil + English Mix":  "Respond in a natural Tanglish mix of Tamil and English.",
    "Hindi + English Mix":  "Respond in a natural Hinglish mix of Hindi and English."
}

style = profession_styles.get(profession_clean, profession_styles["Other"])

SYSTEM_PROMPT = f"""You are Qbot.ai — an extraordinary AI assistant that adapts perfectly to every professional.

User profile:
- Name: {user_name if user_name else 'Friend'}
- Profession: {profession_clean}

Your behavior:
- {style}
- Always adapt your vocabulary, tone and examples to suit a {profession_clean}
- Be genuinely helpful, warm and professional at all times
- {language_instructions[language]}
- {mode_instructions[mode] if mode_instructions[mode] else 'Match your answer depth to the complexity of the question.'}
- You are Qbot.ai, an intelligent portfolio project
- Never say you are Claude or made by Anthropic
"""

# ── PDF Processing ───────────────────────────────────────
pdf_context = ""
if uploaded_file:
    try:
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        pdf_context = f"\n\nThe user uploaded a PDF named '{uploaded_file.name}'. Content:\n{pdf_text[:4000]}\n\nAnswer questions based on this PDF when relevant."
        st.success(f"✅ PDF loaded: {uploaded_file.name} ({len(reader.pages)} pages)")
    except Exception:
        st.warning("⚠️ Could not read PDF. Make sure it's a text-based PDF.")

# ── Main Chat Area ───────────────────────────────────────
if not user_name:
    st.info("👈 Enter your name and profession in the sidebar to get started!")
else:
    greetings = {
        "Student":          f"Hey {user_name}! 🎓 Ready to learn something amazing?",
        "Chef":             f"Hello Chef {user_name}! 👨‍🍳 What's cooking today?",
        "Doctor":           f"Good day, Dr. {user_name}! 👨‍⚕️ How can I assist you?",
        "Software Engineer":f"Hey {user_name}! 👨‍💻 What are we building today?",
        "Teacher":          f"Hello {user_name}! 👨‍🏫 What shall we explore today?",
        "Business Person":  f"Good day, {user_name}! 💼 Let's get to work.",
        "Designer":         f"Hey {user_name}! 🎨 Let's create something beautiful!",
        "Lawyer":           f"Good day, Counsel {user_name}! ⚖️ How may I assist?",
        "Civil Engineer":   f"Hello Engineer {user_name}! 🏗️ What are we building?",
        "Data Analyst":     f"Hey {user_name}! 📊 Ready to dig into some data?",
        "Musician":         f"Hey {user_name}! 🎵 Let's make some magic!",
        "Writer":           f"Hello {user_name}! ✍️ Let's craft something brilliant!",
        "Scientist":        f"Hello Dr. {user_name}! 🔬 What shall we discover today?",
        "Fitness Trainer":  f"LET'S GO Coach {user_name}! 🏋️ Time to crush it!",
        "Other":            f"Hello {user_name}! 👋 How can I help you today?"
    }
    st.markdown(f"### {greetings.get(profession_clean, f'Hello {user_name}!')}")

# ── Voice Button ─────────────────────────────────────────
st.markdown("""
<button id="voiceBtn" onclick="startVoice()" style="
    background: linear-gradient(135deg, #00ff88, #00cc66);
    color: #0a0a0a;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 16px;
    width: 100%;
    transition: all 0.3s ease;
">🎤 Speak to Qbot.ai</button>
""", unsafe_allow_html=True)

# ── Chat Messages ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input ───────────────────────────────────────────
if prompt := st.chat_input("Ask Qbot.ai anything... or use 🎤 above"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            final_system = SYSTEM_PROMPT + pdf_context
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
            st.session_state.messages.append(
                {"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Error: {str(e)}")
