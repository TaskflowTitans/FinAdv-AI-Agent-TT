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
    st.title("🔐 Login")

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
    st.title("📝 Sign Up")

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
    st.session_state["logged_in"] = False
    st.session_state["username"] = None