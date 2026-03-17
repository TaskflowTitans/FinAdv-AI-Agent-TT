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

from tools.langchain_tool import ocr_extraction_tool
from data.categories import categorize

# Set dark theme for matplotlib to match the new UI
plt.style.use('dark_background')

# PAGE CONFIG
st.set_page_config(
    page_title="AI Expense Tracker",
    page_icon="💰",
    layout="wide"
)

init_db()

# CUSTOM CSS FOR MODERN ATTRACTIVE LOOK (Reference: Modern AI Apps)
st.markdown("""
<style>
/* Main background gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: #F8FAFC;
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
</style>
""", unsafe_allow_html=True)

st.title("💰 AI Expense Tracker")
st.caption("Upload receipts and automatically track your spending")

# SIDEBAR
st.sidebar.header("Upload Receipt")
uploaded_file = st.sidebar.file_uploader(
    "Upload Receipt Image",
    type=["png", "jpg", "jpeg"]
)

# ----------------- IMAGE PREVIEW -----------------

if uploaded_file is not None:

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Receipt Preview")
        st.image(uploaded_file, width='stretch')

    with col2:
        st.write("") # Adjust spacing
        if st.button("🔍 Extract Transaction"):

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(uploaded_file.getbuffer())
                temp_path = tmp.name

            with st.spinner("Extracting transaction details..."):

                result = ocr_extraction_tool.invoke({
                    "image_path": temp_path
                })

            if isinstance(result, str):
                result = json.loads(result)

            description = result.get("description", "")
            result["category"] = categorize(description)

            insert_transaction(result)  

            st.success("Transaction added successfully!")

            st.subheader("Extracted Data")
            st.json(result)

# ----------------- DASHBOARD WITH DB-----------------

df = get_all_transactions()

if not df.empty:

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.header("📊 Expense Dashboard")

    total_spent = df["amount"].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Spending", f"₹ {total_spent:,.2f}")

    with col2:
        st.metric("Transactions", len(df))

    st.markdown("<br>", unsafe_allow_html=True)

    # TABLE
    st.subheader("📋 Transaction History")
    st.dataframe(df, width='stretch')

    # DOWNLOAD
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇ Download Transactions as CSV",
        data=csv,
        file_name="transactions.csv",
        mime="text/csv"
    )

    # CATEGORY CHART
    category_chart = df.groupby("category")["amount"].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Expense by Category")
        st.bar_chart(category_chart)

    with col2:
        st.subheader("🥧 Expense Distribution")
        fig, ax = plt.subplots()
        category_chart.plot.pie(autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

    # ----------------- AI ADVICE SECTION -----------------
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.header("💡 AI Financial Insights")
    
    # Calculate highest expense category dynamically
    try:
        highest_category = df.groupby("category")["amount"].sum().idxmax()
        highest_amount = df.groupby("category")["amount"].sum().max()
        
        advice_html = f"""
        <div class="advice-box">
            <h4>🧠 Smart Recommendations</h4>
            <ul>
                <li>Your highest expense category is <strong>{highest_category}</strong> at <strong>₹ {highest_amount:,.2f}</strong>. Consider reviewing these expenses to see if you can cut back.</li>
                <li><strong>Rule of 50/30/20:</strong> Try to keep your Needs to 50%, Wants to 30%, and Savings to 20% of your income.</li>
                <li><strong>Pro Tip:</strong> Wait 24 hours before making non-essential purchases to avoid impulse buying.</li>
            </ul>
        </div>
        """
        st.markdown(advice_html, unsafe_allow_html=True)
        
    except Exception as e:
        # Fallback if there's an issue with the data grouping
        st.info("Add more transactions to get personalized AI financial insights!")

st.markdown("<br><br>", unsafe_allow_html=True)

if st.button("🗑 Clear All Data"):
    from database.db import delete_all
    delete_all()
    st.success("All data deleted!")
