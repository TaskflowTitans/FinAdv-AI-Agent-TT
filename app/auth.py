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
            <div class="login-heading">
                🔐 Welcome Back
            </div>
            <div class="login-subtitle">
                Sign in to access your financial dashboard
            </div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            key="login_btn",
            use_container_width=True
        ):

            with st.spinner("🔐 Authenticating..."):
                time.sleep(1)

                users = load_users()

                if username in users and users[username] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.rerun()

                else:
                    st.error("Invalid username or password")


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

