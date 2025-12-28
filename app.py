import streamlit as st
import pandas as pd
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Study Planner", layout="centered")

st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FILES ----------------
USER_FILE = "users.csv"
PLAN_FILE = "study_plans.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USER_FILE, index=False)

if not os.path.exists(PLAN_FILE):
    pd.DataFrame(columns=["username", "subject", "hours"]).to_csv(PLAN_FILE, index=False)

# ---------------- AUTH FUNCTIONS ----------------
def register_user(username, password):
    df = pd.read_csv(USER_FILE)
    if username in df["username"].values:
        return False
    df.loc[len(df)] = [username, password]
    df.to_csv(USER_FILE, index=False)
    return True

def login_user(username, password):
    df = pd.read_csv(USER_FILE)
    return not df[(df["username"] == username) & (df["password"] == password)].empty

# ---------------- UI ----------------
st.title("📘 Smart Study Planner")

tabs = st.tabs(["🔐 Login", "📝 Sign Up", "👤 Profile"])

# -------- SIGN UP --------
with tabs[1]:
    st.subheader("Create Account")
    r_user = st.text_input("Username", key="ruser")
    r_pass = st.text_input("Password", type="password", key="rpass")

    if st.button("Sign Up"):
        if register_user(r_user, r_pass):
            st.success("Account created! Now login.")
        else:
            st.error("Username already exists!")

# -------- LOGIN --------
with tabs[0]:
    st.subheader("Login")
    l_user = st.text_input("Username", key="luser")
    l_pass = st.text_input("Password", type="password", key="lpass")

    if st.button("Login"):
        if login_user(l_user, l_pass):
            st.session_state["user"] = l_user
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

# -------- PROFILE --------
with tabs[2]:
    if "user" not in st.session_state:
        st.warning("Please login first.")
    else:
        user = st.session_state["user"]
        st.subheader(f"👤 Welcome, {user}")

        plans = pd.read_csv(PLAN_FILE)
        user_plans = plans[plans["username"] == user]

        total_hours = user_plans["hours"].sum() if not user_plans.empty else 0
        subjects_count = user_plans["subject"].nunique()

        col1, col2 = st.columns(2)
        col1.metric("Total Study Hours", f"{total_hours:.1f}")
        col2.metric("Subjects Studied", subjects_count)

        st.subheader("📘 Your Study History")
        if user_plans.empty:
            st.info("No study plans yet.")
        else:
            st.dataframe(user_plans)

        if st.button("Logout"):
            st.session_state.clear()
            st.experimental_rerun()

# ---------------- STUDY PLANNER ----------------
if "user" in st.session_state:
    st.divider()
    st.header("📚 Study Planner")

    n = st.number_input("Number of Subjects", 1, 10, 3)

    subjects = []
    for i in range(n):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input(f"Subject {i+1}")
        with c2:
            diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key=f"d{i}")
        with c3:
            urg = st.slider("Urgency", 1, 5, 3, key=f"u{i}")

        weight = {"Easy": 1, "Medium": 2, "Hard": 3}[diff]
        subjects.append([name, weight * urg])

    hours = st.slider("Total Study Hours", 1, 12, 6)

    if st.button("Generate Plan"):
        df = pd.DataFrame(subjects, columns=["Subject", "Score"])
        df["Study Hours"] = (df["Score"] / df["Score"].sum()).round(2) * hours

        st.success("Study Plan Generated 🎯")
        st.dataframe(df)

        for _, row in df.iterrows():
            pd.DataFrame([{
                "username": st.session_state["user"],
                "subject": row["Subject"],
                "hours": row["Study Hours"]
            }]).to_csv(PLAN_FILE, mode="a", header=False, index=False)
