import pandas as pd

def analyze(self, transactions: list):
    if not transactions:
        return {"error": "No transactions"}

    df = pd.DataFrame(transactions)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    total_spent = df["amount"].sum()
    avg_spend = df["amount"].mean()

    category_spend = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    top_category = category_spend.idxmax()

    # 🔥 NEW METRICS
    max_txn = df["amount"].max()
    min_txn = df["amount"].min()

    # spending concentration
    top_category_pct = (category_spend.iloc[0] / total_spent) * 100 if total_spent > 0 else 0

    # daily pattern
    daily_spend = df.groupby("date")["amount"].sum()
    high_spending_days = daily_spend[daily_spend > (1.5 * avg_spend)].index.tolist()

    # category diversity
    category_count = df["category"].nunique()

    insights = []

    # 🔥 INTELLIGENT INSIGHTS

    if top_category_pct > 50:
        insights.append(f"You are heavily spending on {top_category} ({top_category_pct:.1f}%). Consider balancing your expenses.")

    if max_txn > 3 * avg_spend:
        insights.append("You have some unusually large transactions. Review them carefully.")

    if len(high_spending_days) > 0:
        insights.append(f"You tend to overspend on certain days ({len(high_spending_days)} days detected).")

    if category_count <= 2:
        insights.append("Your spending is concentrated in very few categories.")

    if avg_spend > 1000:
        insights.append("Your average spending is quite high relative to typical users.")

    # 🔥 BEHAVIOR TAGS (VERY POWERFUL)
    behavior = []

    if top_category.lower() in ["food", "shopping"]:
        behavior.append("impulsive_spender")

    if "Bills" in df["category"].values:
        behavior.append("essential_spender")

    if category_count > 5:
        behavior.append("diversified_spender")

    return {
        "top_category": top_category,
        "total_spent": round(total_spent, 2),
        "average_spend": round(avg_spend, 2),
        "max_transaction": max_txn,
        "top_category_percentage": round(top_category_pct, 2),
        "high_spending_days": high_spending_days,
        "category_count": category_count,
        "behavior": behavior,
        "insights": insights
    }