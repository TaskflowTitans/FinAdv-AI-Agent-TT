class AdvisorAgent:
    def advise(self, analysis: dict):
        if "error" in analysis:
            return "No advice available."

        advice = []

        total = analysis.get("total_spent", 0)
        avg = analysis.get("average_spend", 0)
        top_cat = analysis.get("top_category", "")

        # Rule-based advice
        if avg > 500:
            advice.append("Try reducing daily expenses below ₹500.")

        if top_cat:
            advice.append(f"You spend most on {top_cat}. Consider cutting this down.")

        if total > 10000:
            advice.append("Your total spending is high. Consider setting a monthly budget.")

        if not advice:
            advice.append("Your spending looks balanced. Keep it up!")

        return "\n".join([f"• {a}" for a in advice])