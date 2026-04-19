import os
from dotenv import load_dotenv
load_dotenv()
import sys
# allow importing from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import tempfile
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from database.db import init_db, insert_transaction, get_all_transactions
import plotly.express as px
from auth import login, signup, logout
import tempfile
# from tools.ocr import extract_with_tesseract
from data.categories import categorize
from agents.extraction_agent import ExtractionAgent
from utils.image_utils import convert_to_base64
from datetime import datetime
extraction_agent = ExtractionAgent()
from agents.analysis_agent import AnalysisAgent
analysis_agent = AnalysisAgent()
from agents.advisor_agent import AdvisorAgent
advisor_agent = AdvisorAgent()

# PAGE CONFIG
st.set_page_config(
    page_title="TitansLedger - Ultimate AI Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if st.session_state.get("used_fallback"):
    st.warning("⚠ Running in fallback mode (reduced accuracy)")
else:
    st.success("✅ AI system active (high accuracy)")

# Session init
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:

    st.markdown("<h3 style='text-align:center;'>Welcome to TitansLedger</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        login()

    with tab2:
        signup()

    st.stop()

if "guru" not in st.session_state:
    st.session_state["guru"] = None

# Sidebar after login
col1, col2 = st.columns([6, 2])

with col1:
    st.markdown(f"👤 Logged in as: **{st.session_state['username']}**")

with col2:
    st.button("🚪 Logout", on_click=logout, width="stretch")

# Set dark theme for matplotlib to match the new UI
plt.style.use('dark_background')

if "menu_open" not in st.session_state:
    st.session_state["menu_open"] = False

# st.title("💰TitansLedger - AI Expense Tracker")
st.markdown("""
<div class="titans-title">
    TitansLedger
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center; color:#94A3B8;'>AI Expense Tracker</p>",
    unsafe_allow_html=True
)
st.caption("Upload receipts and automatically track your spending")

st.markdown("---")

if st.session_state["menu_open"]:
    with st.sidebar:
        st.write(f"👤 {st.session_state['username']}")

        if st.button("❌ Close"):
            st.session_state["menu_open"] = False
            st.rerun()

        if st.button("🚪 Logout"):
            logout()
            st.session_state["menu_open"] = False
            st.rerun()

init_db()

    # ----------------- MAIN UPLOAD SECTION -----------------
st.markdown("### 📥 Upload Receipt")

uploaded_files = st.file_uploader(
    "Drag and drop or click to upload a receipt (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed",
    accept_multiple_files=True
    )

# 🔥 SAMPLE RECEIPT BUTTON (ADD HERE)
if st.button("📄 Try Sample Receipt"):

    sample_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "samples",
        "payment1.jpg"
    )

    if not os.path.exists(sample_path):
        st.error("Sample receipt not found.")
    else:
        base64_img = convert_to_base64(sample_path)
        result = extraction_agent.extract(base64_img)

        st.session_state["last_results"] = [result]

        st.success("Sample receipt processed ✅")

# ----------------- IMAGE PREVIEW & EXTRACTION -----------------

def clean_result(result):
    try:
        result["total"] = float(result.get("total", 0))
    except:
        result["total"] = 0

    if not result.get("date"):
        result["date"] = None

    if not isinstance(result.get("items"), list):
        result["items"] = []

    return result

if uploaded_files:
    # Small side preview for the image (col1) and data actions (col2)
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("##### 🖼️ Preview")
        for file in uploaded_files:
            st.image(file, width="stretch")

    with col2:
        st.markdown("##### ⚙️ Actions")
        
        if st.button("🔍 Extract Transactions", key="multi_extract"):
            st.session_state["last_results"] = []
            all_results = []
            used_fallback = False
            progress = st.progress(0)

            with st.spinner("Processing With TitansLedger..."):
                for i, file in enumerate(uploaded_files):
                    if i > 0:
                        time.sleep(1)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        tmp.write(file.read())
                        tmp_path = tmp.name

                    # result = extract_with_tesseract(tmp_path)
                    base64_img = convert_to_base64(tmp_path)
                    result = extraction_agent.extract(base64_img)

                    if result.get("fallback"):
                        used_fallback = True

                    st.session_state["last_results"].append(result)

                    if "error" in result:
                        st.warning(f"⚠ {file.name}: {result.get('error')}")
                        continue

                    amount = float(result.get("amount", 0))

                    if amount <= 0:
                        st.warning(f"⚠ Skipping invalid transaction: {file.name}")
                        continue

                    merchant = result.get("description", "Unknown")
                    
                    merchant_raw = result.get("description", "Unknown")
                    sender = result.get("sender", "Unknown")

                    raw_text = merchant_raw.lower()

                    for word in ["upi", "payment", "paid", "txn", "transaction"]:
                        raw_text = raw_text.replace(word, "")

                    raw_text = raw_text.replace("-", " ").replace("_", " ")

                    if "to" in raw_text:
                        raw_text = raw_text.split("to")[-1]

                    merchant = raw_text.strip().title()

                    is_upi = False
                    if any(x in str(result).lower() for x in ["upi", "@", "pay", "txn", "bank", "transfer"]):
                        is_upi = True

                    if is_upi:
                        description = f"UPI • {sender} → {merchant}"
                    else:
                        description = f"{sender} → {merchant}"
                    
                    formatted_data = {
                        "amount": amount,
                        "category": categorize(merchant),
                        "date": result.get("date") or str(datetime.today().date()),
                        "description": description
                    }

                    all_results.append(formatted_data)

                    confidence = "high" if not result.get("fallback") else "low"
                    result["confidence"] = confidence
                    result["is_upi"] = is_upi

                    progress.progress((i + 1) / len(uploaded_files))

            progress.empty()

            if all_results:
                st.session_state["pending_transactions"] = all_results
                st.session_state["used_fallback"] = used_fallback
                st.success(f"✅ Extracted {len(all_results)} transactions! (Review below before saving)" )
            else:
                st.warning("⚠ No valid payment receipts found.")

        st.markdown("##### 📄 Extracted Data")

        for res in st.session_state.get("last_results", []):

            if res.get("fallback"):
                st.warning("⚠ Low confidence extraction (fallback used)")
            else:
                st.success("✅ High confidence extraction")

            st.json(res)
            if res.get("is_upi"):
                st.caption("💳 UPI Transaction")

        st.markdown("---")

        if st.button("🗑️ Clear All Data", type="primary"):
            from database.db import delete_all
            delete_all()
            st.session_state["last_results"] = []   # 🔥 ADD THIS
            st.success("All data deleted!")
            st.rerun()

# ----------------- MANUAL CORRECTION UI -----------------

if st.session_state.get("pending_transactions"):

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown("### ✏️ Review & Confirm Transactions")

    st.info("Please review and correct the extracted data before saving.")

    for i, txn in enumerate(st.session_state["pending_transactions"]):

        st.markdown(f"#### Transaction {i+1}")

        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                f"Amount {i}",
                value=float(txn["amount"]),
                key=f"amount_{i}"
            )

            category = st.text_input(
                f"Category {i}",
                value=txn["category"],
                key=f"category_{i}"
            )

        with col2:
            date = st.text_input(
                f"Date {i}",
                value=txn["date"],
                key=f"date_{i}"
            )

            description = st.text_input(
                f"Description {i}",
                value=txn["description"],
                key=f"description_{i}"
            )

        st.markdown("---")

    # ✅ Confirm button
    if st.button("✅ Confirm & Save All", use_container_width=True):

        for i, txn in enumerate(st.session_state["pending_transactions"]):

            final_txn = {
                "amount": float(st.session_state[f"amount_{i}"]),
                "category": st.session_state[f"category_{i}"],
                "date": st.session_state[f"date_{i}"],
                "description": st.session_state[f"description_{i}"]
            }

            insert_transaction(final_txn)

        st.success("✅ Transactions saved successfully!")

        # clear pending
        del st.session_state["pending_transactions"]

        st.rerun()

# ----------------- DASHBOARD WITH DB -----------------

df = get_all_transactions()

if df.empty:
    st.info("📭 No transactions yet. Upload a receipt to get started.")   

if not df.empty:
        # --- THIS SECTION SHOWS AS SOON AS THERE IS 1+ TRANSACTION ---
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        st.header("📊 Expense Dashboard")

        total_spent = df["amount"].sum()
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Spending", f"₹{total_spent:,.2f}")

        with col2:
            st.metric("Transactions", len(df))

        col1, col2, col3, col4 = st.columns(4)

        avg_spend = df["amount"].mean()
        top_category = df.groupby("category")["amount"].sum().idxmax()
        highest_txn = df["amount"].max()

        with col1:
            st.metric("💰 Total", f"₹{total_spent:,.2f}")

        with col2:
            st.metric("📅 Avg Spend", f"₹{avg_spend:,.2f}")

        with col3:
            st.metric("🏆 Top Category", top_category)

        with col4:
            st.metric("⚠️ Highest", f"₹{highest_txn:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)

        # TABLE - Always show the history if data exists
        st.subheader("📋 Transaction History")
        st.dataframe(
        df.sort_values(by="amount", ascending=False),
        width="stretch"
        )

        st.markdown("---")

        category_chart = df.groupby("category")["amount"].sum().reset_index()

        col_a, col_b = st.columns(2)

        # ✅ ALWAYS show bar chart
        with col_a:
            fig_bar = px.bar(
                category_chart,
                x="category",
                y="amount",
                title="💸 Spending by Category"
            )
            st.plotly_chart(fig_bar, width="stretch")

        # ✅ Show pie chart ONLY if more than 1 category
        if len(category_chart) > 1:
            with col_b:
                fig_pie = px.pie(
                    category_chart,
                    names="category",
                    values="amount",
                    title="📊 Expense Distribution"
                )
                st.plotly_chart(fig_pie, width="stretch")
        else:
            # ✅ Helpful UX message
            with col_b:
                st.info("📊 All your spending is in one category. Add more transactions to see distribution.")

        if len(category_chart) == 1:
            st.metric("Only Category", category_chart["category"].iloc[0])

        # Trend Graph

        st.markdown("### 📈 Spending Trend")

        trend = df.groupby("date")["amount"].sum().reset_index()

        fig_line = px.line(
                trend,
                x="date",
                y="amount",
                title="📅 Daily Spending Trend"
            )

        st.plotly_chart(fig_line, width="stretch")

        st.markdown("### 🚨 Spending Alerts")

        high_spend = df[df["amount"] > df["amount"].mean() * 2]

        if not high_spend.empty:
                st.warning("You have unusually high expenses!")
                st.dataframe(high_spend)
        else:
                st.success("No unusual spending detected 👍")

# Spending Alerts

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.button(
        "🔄 Refresh Dashboard",
        on_click=st.rerun,
        width="stretch"
    )

with col2:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download CSV",
        data=csv,
        file_name="expenses.csv",
        width="stretch"
    )

with col3:
    if st.button("♻ Reset App", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # ----------------- AI ADVICE SECTION -----------------

if df.empty:
    st.info("👋 Upload receipts to start tracking your expenses.")
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.header("🧘 Choose Your Financial Guru")
if st.session_state.get("guru") is None:
    st.info("👆 Select a financial guru to see personalized advice.")

# 👇 show only if data exists
if not df.empty:

    col1, col2 = st.columns(2)

    st.markdown("<br>", unsafe_allow_html=True)

    with col1:
        if st.button("🧠 Chanakya", use_container_width=True):
            st.session_state["guru"] = "Chanakya"

    with col2:
        if st.button("🌿 Vidura", use_container_width=True):
            st.session_state["guru"] = "Vidura"

    if st.button("⚖ Compare Gurus", use_container_width=True):

        transactions = df.tail(50).to_dict(orient="records")
        analysis = analysis_agent.analyze(transactions)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧠 Chanakya")
            advice_c = advisor_agent.advise(analysis, "Chanakya")
            st.info(advice_c)

        with col2:
            st.markdown("### 🌿 Vidura")
            advice_v = advisor_agent.advise(analysis, "Vidura")
            st.success(advice_v)

# 👇 Only show insights AFTER guru selection
if st.session_state.get("guru") is not None and not df.empty:

    st.markdown(f"### 🧘 Insights guided by {st.session_state['guru']}")

    if st.session_state["guru"] == "Chanakya":
        st.warning("“A person should not be too honest. Straight trees are cut first.”")

    elif st.session_state["guru"] == "Vidura":
        st.info("“True wisdom lies in balance, restraint, and righteous action.”")

    transactions = df.tail(50).to_dict(orient="records")
    analysis = analysis_agent.analyze(transactions)

    if "error" in analysis:
        st.error("Analysis failed")

    else:
        st.markdown("### 🧠 AI Insights")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Top Category", analysis.get("top_category"))

        with col2:
            st.metric("Total Spent", f"₹{analysis.get('total_spent')}")

        with col3:
            st.metric("Average Spend", f"₹{analysis.get('average_spend')}")

        st.markdown("### 📊 Key Insights")

        for insight in analysis.get("insights", []):
            st.info(insight)

        st.markdown("### 💡 Guru Advice")

        advice = advisor_agent.advise(analysis, st.session_state["guru"])

        for line in advice.split("\n"):
            if line.strip():
                st.markdown(f"- {line}")

        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("used_fallback"):
    st.warning("⚠ Some receipts used OCR fallback (lower accuracy)")
    
st.markdown("---")
st.markdown("### 📌 About TitansLedger")

st.caption("""
TitansLedger is an AI-powered expense tracking system designed for Indian users.
It combines OCR, fallback parsing, and philosophy-driven financial advice
to deliver a robust and intelligent personal finance assistant.
           
Created by Taskflow Titians
""")

# CUSTOM CSS FOR MODERN ATTRACTIVE LOOK (Reference: Modern AI Apps)

st.markdown("""
<style>
/* Main background gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: #F8FAFC;
}
            
/* Navbar buttons fix */
.stButton > button {
    height: 45px !important;
    white-space: nowrap !important;
    font-size: 16px !important;
}

/* Hide Streamlit top header */
[data-testid="stHeader"] {
    background-color: transparent;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* General Typography adjustments */
h1, h2, h3, h4, h5, h6, p, span, div {
    font-family: 'Inter', sans-serif;
}

/* Card-like Metrics styling */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    backdrop-filter: blur(10px);
}

/* Metric Label */
[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-weight: 500;
    font-size: 1.05rem;
}

/* Metric Value */
[data-testid="stMetricValue"] {
    color: #38BDF8 !important;
    font-size: 2.2rem;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
}

/* Primary Buttons */
.stButton > button {
    background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px -1px rgba(59, 130, 246, 0.5) !important;
}

/* Dataframes styling */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* File Upload Dropzone */
[data-testid="stFileUploadDropzone"] {
    background-color: rgba(255, 255, 255, 0.02);
    border: 2px dashed rgba(255, 255, 255, 0.15);
    border-radius: 12px;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #38BDF8;
    background-color: rgba(56, 189, 248, 0.05);
}

/* Dividers styling */
hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* Advice Box Styling */
.advice-box {
    background: rgba(56, 189, 248, 0.05); 
    border: 1px solid rgba(56, 189, 248, 0.3); 
    padding: 24px; 
    border-radius: 12px; 
    margin-top: 10px;
}
.advice-box h4 {
    color: #38BDF8; 
    margin-top: 0;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.advice-box ul {
    color: #E2E8F0; 
    margin-bottom: 0;
    line-height: 1.6;
}
.advice-box li {
    margin-bottom: 8px;
}
            
@keyframes shine {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

.titans-title {
    cursor: default;
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-weight: 900;
    font-size: 6vw;
    text-transform: uppercase;

    background: linear-gradient(to right,
        #434343 0%,
        #ffffff 50%,
        #434343 100%);
    
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    animation: shine 5s linear infinite;
    text-shadow: 0 0 30px rgba(255,255,255,0.2);
    font-size: clamp(40px, 6vw, 100px);

    filter: drop-shadow(0px 15px 30px rgba(0, 0, 0, 0.5));
    letter-spacing: -0.05em;
}

.titans-title:hover {
    letter-spacing: 0.02em;
    transition: 0.3s ease;
}
</style>

""", unsafe_allow_html=True)



