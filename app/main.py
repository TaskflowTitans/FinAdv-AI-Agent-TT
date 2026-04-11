import sys
import os

# allow importing from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tempfile
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from database.db import init_db, insert_transaction, get_all_transactions
import plotly.express as px
from auth import login, signup, logout

from data.categories import categorize

from agents.extraction_agent import ExtractionAgent
from utils.image_utils import convert_to_base64

extraction_agent = ExtractionAgent()

from agents.cleaning_agent import CleaningAgent
cleaning_agent = CleaningAgent()

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

# Session init
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        login()

    with tab2:
        signup()

    st.stop()

# Sidebar after login
col1, col2 = st.columns([6, 2])

with col1:
    st.markdown(f"👤 Logged in as: **{st.session_state['username']}**")

with col2:
    st.button("🚪 Logout", on_click=logout, use_container_width=True)

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

    # ----------------- IMAGE PREVIEW & EXTRACTION -----------------

if uploaded_files:
        # Small side preview for the image (col1) and data actions (col2)
        col1, col2 = st.columns([1, 3])

        with col1:
            st.markdown("##### 🖼️ Preview")

            for file in uploaded_files:
                st.image(file, use_container_width=True)

        with col2:
            st.markdown("##### ⚙️ Actions")
            
            # Action 1: Extract Data
            if st.button("🔍 Extract Transactions", key="multi_extract"):
                all_results = []

                progress = st.progress(0) 

                with st.spinner("Processing all receipts with AI..."):
                    for i, file in enumerate(uploaded_files):
                        # Convert image to base64
                        image_base64 = convert_to_base64(file)

                        # Call Extraction Agent
                        result = extraction_agent.extract(image_base64)
                        # 🔥 CLEAN THE DATA

                        if "error" in result:
                            st.error(f"Extraction failed for: {file.name}")
                            continue

                        cleaned_result = cleaning_agent.clean(result)

                        if "error" in cleaned_result:
                            st.error(f"Cleaning failed for: {file.name}")
                            continue

                        # Better categorization
                        merchant = cleaned_result.get("merchant", "")
                        items_text = " ".join([item.get("name", "") for item in cleaned_result.get("items", [])])
                        combined_text = merchant + " " + items_text

                        cleaned_result["category"] = categorize(combined_text)

                         # Safe date parsing
                        from datetime import datetime
                        date = cleaned_result.get("date", "")

                        try:
                            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
                        except:
                            parsed_date = datetime.today().date()

                        total = cleaned_result.get("total", 0)

                        # Clean amount
                        try:
                            total = float(str(total).replace("₹", "").replace(",", "").strip())
                        except:
                            total = 0

                        formatted_data = {
                            "amount": total,
                            "category": cleaned_result.get("category", "Other"),
                            "date": str(parsed_date),
                            "description": cleaned_result.get("merchant", "")
                        }

                        insert_transaction(formatted_data)
                        all_results.append(formatted_data)

                        progress.progress((i + 1) / len(uploaded_files))

                progress.empty()

                if all_results:
                    st.success(f"✅ {len(all_results)} transactions added successfully!")
                else:
                    st.error("❌ No valid transactions extracted.")

                # Show all results
                with st.expander("View Extracted Data", expanded=True):
                    st.json(all_results)
                    
            # Action 2: Clear Data (Now only appears when a file is uploaded)
            st.markdown("---") 
            if st.button("🗑️ Clear All Data",type="primary", help="This will wipe the entire database"):
                from database.db import delete_all
                delete_all()
                st.success("All data deleted!")
                st.rerun() # Refresh the app to clear the dashboard charts

    # ----------------- DASHBOARD WITH DB -----------------
df = get_all_transactions()

if not df.empty:
        # --- THIS SECTION SHOWS AS SOON AS THERE IS 1+ TRANSACTION ---
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        st.header("📊 Expense Dashboard")

        total_spent = df["amount"].sum()
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Spending", f"₹ {total_spent:,.2f}")

        with col2:
            st.metric("Transactions", len(df))

        col1, col2, col3, col4 = st.columns(4)

        avg_spend = df["amount"].mean()
        top_category = df.groupby("category")["amount"].sum().idxmax()
        highest_txn = df["amount"].max()

        with col1:
            st.metric("💰 Total", f"₹ {total_spent:,.2f}")

        with col2:
            st.metric("📅 Avg Spend", f"₹ {avg_spend:,.2f}")

        with col3:
            st.metric("🏆 Top Category", top_category)

        with col4:
            st.metric("⚠️ Highest", f"₹ {highest_txn:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True)

        # TABLE - Always show the history if data exists
        st.subheader("📋 Transaction History")
        # st.dataframe(df, use_container_width=True)
        st.dataframe(
        df.sort_values(by="amount", ascending=False),
        use_container_width=True
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
            st.plotly_chart(fig_bar, use_container_width=True)

        # ✅ Show pie chart ONLY if more than 1 category
        if len(category_chart) > 1:
            with col_b:
                fig_pie = px.pie(
                    category_chart,
                    names="category",
                    values="amount",
                    title="📊 Expense Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
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

        st.plotly_chart(fig_line, use_container_width=True)

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

col1, col2 = st.columns(2)

with col1:
    st.button(
        "🔄 Refresh Dashboard",
        on_click=st.rerun,
        use_container_width=True
    )

with col2:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download CSV",
        data=csv,
        file_name="expenses.csv",
        use_container_width=True
    )

    # ----------------- AI ADVICE SECTION -----------------

if df.empty:
    st.info("👋 Upload receipts to start tracking your expenses.")
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.header("💡 AI Financial Insights")

try:
        with st.spinner("Analyzing your spending with AI..."):

            transactions = df.tail(50).to_dict(orient="records")
            if not transactions:
                st.info("No data available for analysis yet.")  
            else:
                analysis = analysis_agent.analyze(transactions)
                advice = advisor_agent.advise(analysis)

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

except Exception as e:
        st.error("Error generating AI insights")
        st.exception(e)

st.markdown("### 💡 Smart Financial Advice")

for line in advice.split("\n"):
    if line.strip():
        st.success(line)

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



