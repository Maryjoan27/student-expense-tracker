import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
from supabase import create_client, Client

import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

img = get_base64_image("assets/background.png")

page_bg = f"""
<style>

.stApp {{
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
    background-position: center;
    background-color: rgba(0, 0, 0, 0.75);
    background-repeat: no-repeat;
    filter: brightness (0.4);
}}

.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
}}

</style>
"""

st.markdown("""
<h1 style='text-align: center; color: #1f4e79;'>
💰 Smart Student Expense Tracker
</h1>

<p style='text-align: center; font-size:18px;'>
Track your spending, save smarter, and let AI guide your finances 🤖
</p>
""", unsafe_allow_html=True)

st.image ("assets/logo.png", width=300 )

st.markdown("""
<style>
.glass {
    background: rgba(255, 255, 255, 0.2);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(page_bg, unsafe_allow_html=True)

# ---------------- SETUP ---------------- #

# ---------------- SETUP ---------------- #

st.set_page_config(page_title="Student Expense Tracker", layout="wide")

# Connect to Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_data():
    response = supabase.table("expenses").select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        cols = ["date", "type", "amount", "category", "description", "payment_method"]
        df = df[cols]
        return df
    else:
        return pd.DataFrame(columns=["date","type","amount","category","description","payment_method"])

def save_data(row):
    supabase.table("expenses").insert(row).execute()

def calculate_balance(df):
    if df.empty:
        return 0, 0, 0
    income = df[df["type"] == "income"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()
    balance = income - expenses
    return balance, income, expenses

df = load_data()
# ---------------- SIDEBAR ---------------- #

menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Add Income",
    "Add Expense",
    "View Expenses",
    "Analysis",
    "AI Prediction"
])

# ---------------- DASHBOARD ---------------- #

if menu == "Dashboard":
    st.title("📊 Dashboard")

    if df.empty:
        st.warning("No expenses added yet")
    else:
        balance, total_income, total_expenses = calculate_balance(df)

        # Warning banner
        if total_income > 0:
            percentage_left = (balance / total_income) * 100
            if balance <= 0:
                st.error("⚠️ You are out of money!")
            elif percentage_left <= 40:
                st.warning(f"⚠️ Low balance! You have {percentage_left:.1f}% of your income left")

        st.divider()

        # Clean metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Balance", f"₦{balance:.2f}")
        col2.metric("📥 Total Income", f"₦{total_income:.2f}")
        col3.metric("📤 Total Spent", f"₦{total_expenses:.2f}")

        st.divider()

        # Top spending category (expenses only)
        expenses_only = df[df["type"] == "expense"]
        if not expenses_only.empty:
            top_category = expenses_only.groupby("category")["amount"].sum().idxmax()
            st.metric("🏆 Top Spending Category", top_category)
# ---------------- ADD INCOME ---------------- #

elif menu == "Add Income":
    st.title("💵 Add Income")

    balance, total_income, total_expenses = calculate_balance(df)
    st.success(f"✅ Current Balance: ₦{balance:.2f}")
    
    st.divider()

    col1, col2 = st.columns(2)
    date = col1.date_input("Date", datetime.today())
    amount = col2.number_input("Amount (₦)", min_value=0.0)

    description = st.text_input("Description (e.g. Monthly allowance from mum)")
    payment = st.selectbox(
        "Payment Method",
        ["Cash","Transfer","Card"]
    )

    if st.button("Save Income"):
        new_data = {
            "date": str(date),
            "type": "income",
            "amount": amount,
            "category": "Income",
            "description": description,
            "payment_method": payment
        }
        save_data( new_data)
        st.success(f"₦{amount:.2f} added successfully!")
        st.rerun()
# ---------------- ADD EXPENSE ---------------- #

elif menu == "Add Expense":
    st.title("➕ Add Expense")

    # Show current balance at the top
    balance, total_income, total_expenses = calculate_balance(df)
    
    if total_income > 0:
        percentage_left = (balance / total_income) * 100
        if balance <= 0:
            st.error(f"⚠️ You are out of money! Balance: ₦{balance:.2f}")
        elif percentage_left <= 40:
            st.warning(f"⚠️ Low balance warning! You have ₦{balance:.2f} left ({percentage_left:.1f}% of your income)")
        else:
            st.success(f"✅ Current Balance: ₦{balance:.2f}")
    else:
        st.info("💡 Add your income first before adding expenses")

    st.divider()

    col1, col2 = st.columns(2)
    date = col1.date_input("Date", datetime.today())
    amount = col2.number_input("Amount (₦)", min_value=0.0)

    category = st.selectbox(
        "Category",
        ["Food","Transport","Data/Airtime","School","Clothes","Entertainment","Other"]
    )
    description = st.text_input("Description")
    payment = st.selectbox(
        "Payment Method",
        ["Cash","Transfer","Card"]
    )

    if st.button("Save Expense"):
        new_data = {
            "date": str(date),
            "type": "expense",
            "amount": amount,
            "category": category,
            "description": description,
            "payment_method": payment
        }
        save_data(new_data)
        st.success("Expense saved successfully!")
        st.rerun()

# ---------------- VIEW ---------------- #

elif menu == "View Expenses":
    st.title("📄 All Expenses")

    expenses_only = df[df["type"] == "expense"]

    if expenses_only.empty:
        st.warning("No expenses added yet")
    else:
        # Drop the type column since it's always "expense" here
        display_df = expenses_only.drop(columns=["type"]).reset_index(drop=True)
        st.dataframe(display_df, width='stretch')

# ---------------- ANALYSIS ---------------- #

elif menu == "Analysis":

    st.title("📊 Spending Analysis")

    if df.empty:
        st.warning("No data available")

    else:

        balance, total_income, total_expenses = calculate_balance(df)
        st.metric("Total Spending", f"₦{total_expenses:.2f}")

        st.subheader("Category Distribution")

        category_sum = df[df["type"] == "expense"].groupby("category")["amount"].sum()

        st.bar_chart(category_sum)

        st.subheader("Spending Trend")

        df["date"] = pd.to_datetime(df["date"])

        daily = df.groupby("date")["amount"].sum()

        st.line_chart(daily)

    st.subheader("Spending Distribution (Pie Chart)")

    category_sum = df[df["type"] == "expense"].groupby("category")["amount"].sum()

    if not category_sum.empty:
        st.pyplot(category_sum.plot.pie(autopct="%1.1f%%").figure)
    else:
        st.info("No expense data yet to display pie chart")   

# ---------------- AI PREDICTION ---------------- #

elif menu == "AI Prediction":

    st.title("🤖 AI Prediction")

    if len(df) < 5:

        st.warning("Add at least 5 expenses for prediction")

    else:

        df["date"] = pd.to_datetime(df["date"])

        df["day"] = df["date"].dt.day

        X = df[["day"]]
        y = df["amount"]

        model = LinearRegression()

        model.fit(X,y)

        future_days = np.array(range(df["day"].max()+1,31)).reshape(-1,1)

        predicted = model.predict(future_days)

        predicted_total = predicted.sum()

        spent_so_far = df["amount"].sum()

        income = st.number_input("Monthly Income (₦)", min_value=0.0)

        if income > 0:

            balance = income - (spent_so_far + predicted_total)

            col1, col2 = st.columns(2)

            col1.metric("Spent so far", f"₦{spent_so_far:.2f}")
            col2.metric("Predicted spending", f"₦{predicted_total:.2f}")

            if balance < 0:

                st.error(f"You may overspend by ₦{abs(balance):.2f}")

            else:

                st.success(f"Estimated balance: ₦{balance:.2f}")