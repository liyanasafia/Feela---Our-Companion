# feela_app.py
import streamlit as st
import os
import random
from openai import OpenAI

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="FEELA - Your Mood Companion", page_icon="💛", layout="centered")

# -------------------------------
# SHARED CSS (chat + global)
# -------------------------------
global_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url('https://images.unsplash.com/photo-1760556415132-533affdd9ccf?ixlib=rb-4.1.0&auto=format&fit=crop&w=1974&q=80');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
.chat-box {
    background: rgba(255,255,255,0.9);
    border-radius: 16px;
    padding: 20px;
    max-width: 780px;
    margin: 0 auto 30px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    backdrop-filter: blur(6px);
}
.chat-bubble-user {
    background: rgba(220,220,220,0.95);
    padding: 10px 14px;
    border-radius: 14px;
    margin: 10px 0;
    text-align: right;
    color: #333;
}
.chat-bubble-bot {
    background: rgba(255,255,255,0.95);
    padding: 10px 14px;
    border-radius: 14px;
    margin: 10px 0;
    border: 1px solid rgba(247,207,161,0.6);
    color: #333;
}
.title-chat {
    text-align: center;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    color: #0b63b8;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 8px;
}
.stButton>button {
    background-color: #1e90ff;
    color: white;
    border-radius: 10px;
    padding: 8px 18px;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #0e5bb5;
}
input[type="text"], input[type="password"], textarea {
    border-radius: 10px !important;
    padding: 10px !important;
    border: 1px solid #cfe8ff !important;
}
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)

# -------------------------------
# LOGIN/SIGNUP PAGE CSS (distinct)
# -------------------------------
login_css = """
<style>
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #e6f3ff 0%, #ffffff 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.login-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,255,0.98));
    padding: 36px 36px;
    border-radius: 16px;
    box-shadow: 0 12px 40px rgba(12, 60, 120, 0.12);
    max-width: 420px;
    width: 100%;
    text-align: center;
}
.login-card .logo {
    font-size: 34px;
    margin-bottom: 10px;
}
.login-card h1 {
    color: #0b63b8;
    margin-bottom: 10px;
    font-weight: 700;
}
.login-sub {
    color: #4b6b8a;
    font-size: 14px;
    margin-bottom: 18px;
}
.login-card input {
    width: 100%;
    padding: 12px;
    margin: 8px 0;
    border-radius: 10px;
    border: 1px solid #d9eefd;
    background-color: #fff;
    box-sizing: border-box;
}
.login-card .muted {
    font-size: 13px;
    color: #6b7b8f;
    margin-top: 12px;
}
.link-btn {
    background: none;
    border: none;
    color: #0b63b8;
    text-decoration: underline;
    cursor: pointer;
    font-weight: 600;
    padding: 0;
}
</style>
"""

# -------------------------------
# OPENAI CLIENT SETUP
# -------------------------------
api_key = None
try:
    api_key = st.secrets["general"]["OPENAI_API_KEY"]
except Exception:
    pass
if not api_key:
    api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    api_key = os.getenv("OPENAI_API_KEY")
if not api_key or not isinstance(api_key, str) or not api_key.startswith("sk-"):
    st.error("❌ OpenAI API key not found. Add it to Streamlit Cloud → Manage app → Edit secrets:\n\n[general]\nOPENAI_API_KEY = \"sk-your_key_here\"")
    st.stop()
client = OpenAI(api_key=api_key)

# -------------------------------
# SESSION STATE INIT
# -------------------------------
if "users" not in st.session_state: st.session_state.users = {}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "signup_phase" not in st.session_state: st.session_state.signup_phase = False
if "chats" not in st.session_state: st.session_state.chats = {}

def ensure_chat_for_user(username):
    if username not in st.session_state.chats:
        st.session_state.chats[username] = []

# -------------------------------
# SIGNUP / LOGIN FUNCTIONS
# -------------------------------
def signup():
    st.markdown(login_css, unsafe_allow_html=True)
    st.markdown("<div class='login-container'><div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='logo'>🤖 Feela</div>", unsafe_allow_html=True)
    st.markdown("<h1>Create account</h1>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Join Feela — a friendly mood companion</div>", unsafe_allow_html=True)
    new_user = st.text_input("Username", key="signup_user")
    new_pass = st.text_input("Password", type="password", key="signup_pass")
    if st.button("Create account"):
        if not new_user or not new_pass:
            st.warning("Please fill both fields.")
        elif new_user in st.session_state.users:
            st.error("That username is already taken.")
        else:
            st.session_state.users[new_user] = new_pass
            st.success(f"Account created for {new_user}. Please log in.")
            st.session_state.signup_phase = False
    if st.button("Already have an account? Log in"):
        st.session_state.signup_phase = False
    st.markdown("</div></div>", unsafe_allow_html=True)

def login():
    st.markdown(login_css, unsafe_allow_html=True)
    st.markdown("<div class='login-container'><div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='logo'>🤖 Feela</div>", unsafe_allow_html=True)
    st.markdown("<h1>Welcome back</h1>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Sign in to continue chatting with Feela</div>", unsafe_allow_html=True)
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Sign in"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            ensure_chat_for_user(username)
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password")
    if st.button("New here? Create an account"):
        st.session_state.signup_phase = True
    st.markdown("</div></div>", unsafe_allow_html=True)

# -------------------------------
# MOOD DETECTION & RESPONSE
# -------------------------------
def detect_mood(text):
    moods = {
        "happy": ["happy","great","awesome","good","fantastic","excited","joyful"],
        "sad": ["sad","down","tired","bad","upset","depressed","unhappy"],
        "angry": ["angry","mad","furious","annoyed","irritated"],
        "neutral": ["okay","fine","alright","so-so"]
    }
    t = (text or "").lower()
    for mood, keys in moods.items():
        if any(k in t for k in keys): return mood
    return "neutral"

def generate_feela_response(user_text):
    lower_text = (user_text or "").lower()
    greetings = ["hi","hello","hey","yo","hiya"]
    thanks = ["thank you","thanks","thx","thankyou"]
    if any(w in lower_text.split() for w in greetings):
        return random.choice(["Hello! How are you today? 😊","Hey there! How’s it going?","Hi! I’m glad to see you! How’s your day so far?"])
    if any(w in lower_text for w in thanks):
        return random.choice(["You’re welcome! I’m always here for you 💛","No problem! Glad I could help 🌟","Anytime! I’m here 😊"])
    mood = detect_mood(user_text)
    exercises = ["try stretching your arms and taking three deep breaths 🌬️","take a short 5-minute walk and look at the sky 🌤️","do 10 jumping jacks to lift your mood 💪","stand up, roll your shoulders, and smile — it really helps 😄"]
    snacks = ["grab a banana 🍌 — full of happy nutrients!","have some dark chocolate 🍫 — instant serotonin boost!","try a handful of nuts 🥜 — they boost energy and mood!","drink a glass of water 💧 — hydration helps your brain think clearer!"]
    if mood == "sad":
        return f"Hey 💛, I sense you’re feeling low. Maybe {random.choice(exercises)} or {random.choice(snacks)} could help. I’m here for you!"
    elif mood == "happy":
        return random.choice(["Yay! That makes me happy 😄 Keep smiling!","Awesome! 🌈 Spread those good vibes!","Love that! 💖 Keep it going!"])
    elif mood == "angry":
        return f"It’s okay to feel angry 🔥. Maybe {random.choice(exercises)} could help you relax."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":"You are Feela, a kind, casual, friendly mood companion chatbot."},
                {"role":"user","content":user_text}
            ]
        )
        return response.choices[0].message.content
    except Exception:
        return "SORRY!! Feela is unable to process your text right now. Please try again."

# -------------------------------
# MAIN APP FLOW
# -------------------------------
if not st.session_state.logged_in:
    if st.session_state.signup_phase:
        signup()
    else:
        login()
else:
    st.markdown("<div class='title-chat'><h1>Feela - Your Mood Companion</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#476b8a;'>Hello <b>{st.session_state.current_user}</b> — I’m Feela. Tell me how you feel today!</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.experimental_rerun()
    with col2:
        if st.button("Reset Chat"):
            ensure_chat_for_user(st.session_state.current_user)
            st.session_state.chats[st.session_state.current_user] = []
            st.success("Chat history cleared.")

    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    ensure_chat_for_user(st.session_state.current_user)
    cols = st.columns([8,2])
    user_text = cols[0].text_input("Type something to Feela...", key="chat_input")
    if cols[1].button("SEND") and user_text:
        st.session_state.chats[st.session_state.current_user].append(("You", user_text))
        reply = generate_feela_response(user_text)
        st.session_state.chats[st.session_state.current_user].append(("Feela", reply))
        st.experimental_rerun()
    for sender, msg in st.session_state.chats[st.session_state.current_user]:
        if sender=="You":
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-bot'><b>Feela:</b> {msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
