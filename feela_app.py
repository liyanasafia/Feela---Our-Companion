import streamlit as st
import random
from openai import OpenAI

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="FEELA - Your Mood Companion",
    page_icon="💛",
    layout="centered"
)

# -------------------------------
# CUSTOM CSS STYLING
# -------------------------------
st.markdown("""
<style>
/* Page background */
[data-testid="stAppViewContainer"] {
    background-image: url('https://images.unsplash.com/photo-1760556415132-533affdd9ccf?ixlib=rb-4.1.0&auto=format&fit=crop&w=1974&q=80');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Hide default Streamlit header & toolbar */
[data-testid="stHeader"], [data-testid="stToolbar"] {
    background: transparent;
    display: none;
}

/* Main title */
h1 {
    color: #1e90ff;  /* dark blue */
    font-family: sans-serif;
    text-align: center;
    font-size: 3em;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
    margin-top: 20px;
}

/* Subtitle and labels */
p, label {
    color: #87ceeb;  /* sky blue */
    font-family: sans-serif;
    text-align: center;
    font-size: 1.05em;
}

/* Chat container */
.chat-box {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 4px 25px rgba(0,0,0,0.15);
    backdrop-filter: blur(15px);
    max-width: 700px;
    margin: 0 auto;
}

/* User bubble */
.chat-bubble-user {
    background: rgba(211, 211, 211, 0.9);  /* grey */
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    text-align: right;
    font-weight: 500;
    color: #4a2c0a;
    font-family: sans-serif;
}

/* Bot bubble */
.chat-bubble-bot {
    background: rgba(255, 255, 255, 0.9);
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    border: 1px solid #f7cfa1;
    color: #4a2c0a;
    font-family: sans-serif;
}

/* Input box */
input[type="text"], input[type="password"] {
    border-radius: 10px !important;
    padding: 10px !important;
    border: 1px solid #87ceeb !important;  /* sky blue border */
    background-color: rgba(255, 255, 255, 0.95) !important;
    font-family: sans-serif;
    color: #4a2c0a !important;
}

/* Send/Login/Signup button */
.stButton>button {
    background-color: #1e90ff;
    color: white;
    font-family: sans-serif;
    font-weight: 600;
    border-radius: 10px;
    padding: 8px 20px;
    margin-left: 10px;
    border: none;
    cursor: pointer;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #00008B;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# OPENAI CLIENT
# -------------------------------
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

# -------------------------------
# USER DATABASE (In-memory dictionary)
# -------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}  # Stores username: password
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "signup_phase" not in st.session_state:
    st.session_state.signup_phase = False

# -------------------------------
# SIGN UP & LOGIN PHASES
# -------------------------------
def signup():
    st.title("Sign Up to Use Feela 💬")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    if st.button("Sign Up"):
        if new_user in st.session_state.users:
            st.error("Username already exists! Try logging in or choose another.")
        elif new_user == "" or new_pass == "":
            st.warning("Please fill in both fields.")
        else:
            st.session_state.users[new_user] = new_pass
            st.success(f"Account created for {new_user}! You can now log in.")
            st.session_state.signup_phase = False

def login():
    st.title("Login to Access Feela 💬")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success(f"Welcome {username}! You can now chat with Feela 💛")
        else:
            st.error("Invalid username or password")

if not st.session_state.logged_in:
    st.write("New user? [Sign Up](#)") if not st.session_state.signup_phase else None
    if st.session_state.signup_phase:
        signup()
    else:
        login()
    if st.button("Switch to Sign Up"):
        st.session_state.signup_phase = True
    if st.button("Switch to Login"):
        st.session_state.signup_phase = False

# -------------------------------
# MOOD DETECTION FUNCTION
# -------------------------------
def detect_mood(user_text):
    mood_keywords = {
        "happy": ["happy", "great", "awesome", "good", "fantastic", "excited", "joyful"],
        "sad": ["sad", "down", "tired", "bad", "upset", "depressed", "unhappy"],
        "angry": ["angry", "mad", "furious", "annoyed", "irritated"],
        "neutral": ["okay", "fine", "alright", "so-so"]
    }
    user_text_lower = user_text.lower()
    for mood, words in mood_keywords.items():
        if any(word in user_text_lower for word in words):
            return mood
    return "neutral"

# -------------------------------
# FEELA RESPONSE FUNCTION
# -------------------------------
def generate_feela_response(user_input):
    lower_text = user_input.lower()
    greetings_keywords = ["hi", "hello", "hey", "yo", "hiya"]
    thanks_keywords = ["thank you", "thanks", "thx", "thankyou"]

    if any(word in lower_text.split() for word in greetings_keywords):
        return random.choice([
            "Hello! How are you today? 😊",
            "Hey there! How’s it going?",
            "Hi! I’m glad to see you! How’s your day so far?"
        ])

    if any(word in lower_text for word in thanks_keywords):
        return random.choice([
            "You’re welcome! I’m always here for you 💛",
            "No problem! I’m glad I could help 🌟",
            "Anytime! I’m always around if you need me 😊"
        ])

    current_mood = detect_mood(user_input)
    exercises = [
        "try stretching your arms and taking three deep breaths 🌬️",
        "take a short 5-minute walk and look at the sky 🌤️",
        "do 10 jumping jacks to lift your mood 💪",
        "stand up, roll your shoulders, and smile — it really helps 😄"
    ]
    snacks = [
        "grab a banana 🍌 — full of happy nutrients!",
        "have some dark chocolate 🍫 — instant serotonin boost!",
        "try a handful of nuts 🥜 — they boost energy and mood!",
        "drink a glass of water 💧 — hydration helps your brain think clearer!"
    ]

    if current_mood == "sad":
        return f"""
Hey there 💛  
I can sense you might be feeling a bit low.  
How about you {random.choice(exercises)}?  
Or maybe {random.choice(snacks)} could cheer you up!  
You’ve got this — I’m here for you 💪✨
"""
    elif current_mood == "happy":
        return random.choice([
            "Yay! That makes me so happy to hear 😄 Keep that positive energy flowing!",
            "That’s awesome! 🌈 The world feels brighter when you’re smiling.",
            "Love that for you! 💖 Keep spreading those good vibes!"
        ])
    elif current_mood == "angry":
        return f"""
It’s okay to feel angry sometimes 🔥  
Maybe take a deep breath or {random.choice(exercises)} to release some tension.  
Want to tell me what’s making you feel that way?
"""
    else:
        if not client.api_key:
            return "I’m here to chat with you! How are you feeling today? 💛"
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Feela, a kind, casual, and friendly mood companion chatbot."},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
        except Exception:
            return "SORRY!! Feela is unable to process your text. Please try again."

# -------------------------------
# CHAT INTERFACE
# -------------------------------
if st.session_state.logged_in:
    st.title(f"Feela - Your Mood Companion 💬")
    st.markdown(f"Hey {st.session_state.current_user}! I’m **Feela**, your friendly chatbot. Tell me how you’re feeling today!")

    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Input box and send button
    user_input = st.text_input("Type something to Feela...", key="user_input_box")
    if st.button("SEND") and user_input:
        response = generate_feela_response(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Feela", response))

    # Display chat history
    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-bot'><b>Feela:</b> {msg}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

