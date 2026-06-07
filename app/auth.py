import streamlit as st
import json
import os
import time

# Path to users.json
USER_FILE = os.path.join(os.path.dirname(__file__), "users.json")


# Load users
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)


# Save users
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


# LOGIN FUNCTION
def login():
    st.markdown("""
        <div class="login-card">
            <h2 style="
                color:#FFD700;
                font-size:2rem;
                font-weight:800;
                ">🔐 Welcome Back</h2>
            <p style='color:#94A3B8;'>
                Sign in to access your financial dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        with st.spinner("🔐 Authenticating..."):
            time.sleep(1)  # small delay for UX

            users = load_users()

            if username in users and users[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid username or password ❌")


# SIGNUP FUNCTION (IMPORTANT ADD)
def signup():
    st.markdown("""
        <div class="login-card">
            <h2 style="
                color:#FFD700;
                font-size:2rem;
                font-weight:800;
                ">📝 Create Account</h2>
            <p style='color:#94A3B8;'>
                Start tracking your expenses with AI
            </p>
        </div>
        """, unsafe_allow_html=True)

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Sign Up"):
        users = load_users()

        if new_user in users:
            st.warning("User already exists ⚠️")
        else:
            users[new_user] = new_pass
            save_users(users)
            st.success("Account created successfully 🎉")


# LOGOUT
def logout():

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()

st.markdown("""
<style>
    .login-card{
        background: linear-gradient(
            145deg,
            rgba(30,30,30,0.95),
            rgba(15,15,15,0.95)
        );

        backdrop-filter: blur(20px);

        border: 1px solid rgba(255,215,0,0.25);

        border-radius: 24px;

        padding: 30px;

        text-align: center;

        margin-bottom: 20px;

        box-shadow:
            0 0 30px rgba(255,215,0,0.08),
            0 8px 30px rgba(0,0,0,0.4);
    }
            
    .stTextInput input {
        background-color: #111111 !important;
        border: 1px solid rgba(255,215,0,0.25) !important;
        color: white !important;
        border-radius: 10px !important;
    }

    .stTextInput input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 10px rgba(255,215,0,0.4) !important;
    }
</style>
""", unsafe_allow_html=True)