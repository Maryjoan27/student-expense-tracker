import csv
import os
import pandas as pd
import numpy as np

# ================= BUDGET LIMITS (NAIRA) ================= #

BUDGET_LIMITS = {
    "Food": 15000,
    "Transport": 8000,
    "Airtime/Data": 5000,
    "Entertainment": 4000,
    "Books/Stationery": 3000,
    "Personal Care": 3000,
    "Accommodation": 25000,
    "Other": 5000
}


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LinearRegression


# ================= FILE SETUP ================= #

DATA_FILE = "data/expenses.csv"

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Create CSV if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "date",
            "amount",
            "category",
            "description",
            "payment_method"
        ])

# ================= AUTO CATEGORIZATION ================= #

def auto_categorize(description):
    desc = description.lower()

    if any(word in desc for word in ["food", "rice", "stew", "lunch", "dinner", "breakfast"]):
        return "Food"
    elif any(word in desc for word in ["bus", "uber", "taxi", "transport", "keke"]):
        return "Transport"
    elif any(word in desc for word in ["airtime", "data", "internet"]):
        return "Airtime/Data"
    elif any(word in desc for word in ["book", "pen", "stationery"]):
        return "Books/Stationery"
    elif any(word in desc for word in ["rent", "hostel", "accommodation"]):
        return "Accommodation"
    elif any(word in desc for word in ["movie", "party", "entertainment"]):
        return "Entertainment"
    elif any(word in desc for word in ["hair", "cream", "soap"]):
        return "Personal Care"
    else:
        return "Other"
    
def ml_categorize(description):
    try:
        df = pd.read_csv("data/category_training_data.csv")

        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(df["description"])
        y = df["category"]

        model = MultinomialNB()
        model.fit(X, y)

        desc_vec = vectorizer.transform([description])
        prediction = model.predict(desc_vec)

        return prediction[0]
    except:
        return auto_categorize(description)
    

# ================= ADD EXPENSE ================= #

def add_expense():
    print("\n--- Add New Expense ---")

    date = input("Enter date (YYYY-MM-DD): ")
    amount = float(input("Enter amount spent (₦): "))
    description = input("Enter description (optional): ")

    suggested_category = ml_categorize(description)
    print(f"Suggested category: {suggested_category}")

    category = input("Press Enter to accept or type a new category: ").strip()
    if category == "":
        category = suggested_category

    category = category.title()
    payment_method = input("Payment method (Cash, Transfer, Card): ").title()

    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            date,
            amount,
            category,
            description,
            payment_method
        ])

    print("✅ Expense saved successfully!")

# ================= VIEW EXPENSES ================= #

def view_expenses():
    print("\n--- All Expenses ---")

    df = pd.read_csv(DATA_FILE)
    if df.empty:
        print("No expenses recorded yet.")
    else:
        print(df)

# ================= ANALYZE SPENDING ================= #

def analyze_spending():
    print("\n--- Spending Analysis ---")

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        print("No data available for analysis.")
        return

    total_spent = df["amount"].sum()
    print(f"\n💰 Total Spent: ₦{total_spent:.2f}")

    category_summary = df.groupby("category")["amount"].sum()
    print("\n📊 Spending by Category:")
    print(category_summary)

    top_category = category_summary.idxmax()
    print(f"\n🔥 Top Spending Category: {top_category}")  

    show_spending_pie(df)
    spending_alerts(df)



import matplotlib.pyplot as plt

def show_spending_pie(df):
    category_totals = df.groupby("category")["amount"].sum()

    plt.figure(figsize=(6, 6))
    plt.pie(
        category_totals,
        labels=category_totals.index,
        autopct="%1.1f%%",
        startangle=140
    )
    plt.title("Spending by Category")
    plt.tight_layout()
    plt.show()

def spending_alerts(df):
    print("\n🚨 Overspending Alerts & Advice")

    category_totals = df.groupby("category")["amount"].sum()

    for category, spent in category_totals.items():
        limit = BUDGET_LIMITS.get(category, None)

        if limit and spent > limit:
            excess = spent - limit
            print(
                f"⚠️ {category}: Spent ₦{spent:.2f} "
                f"(₦{excess:.2f} above recommended)"
            )
            print(
                f"💡 Advice: Try reducing {category.lower()} spending "
                f"to save about ₦{excess:.2f}\n"
            )

def predict_month_end_balance(df):
    print("\n🤖 AI Balance Prediction")

    try:
        monthly_income = float(input("Enter your monthly income/allowance (₦): "))
    except:
        print("Invalid amount.")
        return

    df["date"] = pd.to_datetime(df["date"])
    df["day"] = df["date"].dt.day

    daily_spending = df.groupby("day")["amount"].sum().reset_index()

    if len(daily_spending) < 2:
        print("Not enough data for prediction yet.")
        return

    X = daily_spending[["day"]]
    y = daily_spending["amount"]

    model = LinearRegression()
    model.fit(X, y)

    last_day = df["day"].max()
    days_in_month = 30

    future_days = np.array(range(last_day + 1, days_in_month + 1)).reshape(-1, 1)
    predicted_spending = model.predict(future_days)

    predicted_remaining_spending = predicted_spending.sum()
    total_spent_so_far = df["amount"].sum()

    predicted_end_balance = (
        monthly_income - (total_spent_so_far + predicted_remaining_spending)
    )

    print(f"\n📉 Spent so far: ₦{total_spent_so_far:.2f}")
    print(f"📈 Predicted remaining spending: ₦{predicted_remaining_spending:.2f}")

    if predicted_end_balance >= 0:
        print(
            f"✅ Estimated balance at month end: "
            f"₦{predicted_end_balance:.2f}"
        )
    else:
        print(
            f"⚠️ Warning: At this rate, you may run out of money "
            f"by ₦{abs(predicted_end_balance):.2f}"
        )


# ================= MAIN MENU ================= #

def main():
    while True:
        print("\n==== Student Expense Tracker ====")
        print("1. Add new expense")
        print("2. View all expenses")
        print("3. Analyze spending")
        print("4. Predict month-end balance")
        print("5. Exit")

        choice = input("Choose an option (1-5): ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            analyze_spending()
        elif choice == "4":
            df = pd.read_csv(DATA_FILE)
            if df.empty:
                print("No expense data available.")
            else:
                predict_month_end_balance(df)
        elif choice == "5":
            print("Goodbye 👋")
            break            
    
        else:
            print("❌ Invalid option. Try again.")

# ================= RUN APP ================= #

if __name__ == "__main__":
    main()
