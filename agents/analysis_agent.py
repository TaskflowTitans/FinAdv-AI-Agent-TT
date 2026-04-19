import pandas as pd

class AnalysisAgent:
    def analyze(self, transactions: list):
        if not transactions:
            return {"error": "No transactions"}

        df = pd.DataFrame(transactions)

        # Convert safely
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        total_spent = df["amount"].sum()
        avg_spend = df["amount"].mean()

        category_spend = df.groupby("category")["amount"].sum()
        top_category = category_spend.idxmax()

        high_spending_days = (
            df.groupby("date")["amount"].sum()
            .loc[lambda x: x > 2 * avg_spend]
            .index.tolist()
        )

        insights = []

        if avg_spend > 500:
            insights.append("Your average spending is quite high.")

        if len(high_spending_days) > 0:
            insights.append(f"High spending detected on {len(high_spending_days)} days.")

        if top_category:
            insights.append(f"Most money spent on {top_category}.")

        return {
            "top_category": top_category,
            "total_spent": round(total_spent, 2),
            "average_spend": round(avg_spend, 2),
            "high_spending_days": high_spending_days,
            "insights": insights
        }