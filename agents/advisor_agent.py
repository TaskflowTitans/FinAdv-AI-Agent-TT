class AdvisorAgent:

    def advise(self, analysis: dict, guru: str):

        if "error" in analysis:
            return "No advice available."

        total = analysis.get("total_spent", 0)
        avg = analysis.get("average_spend", 0)
        top_cat = analysis.get("top_category", "")

        advice = []

        # 🔹 Base observations
        if avg > 500:
            advice.append("Your daily spending is high.")

        if top_cat:
            advice.append(f"You are spending most on {top_cat}.")

        if total > 10000:
            advice.append("Your total spending is significantly high.")

        if not advice:
            advice.append("Your spending is currently balanced.")

        # 🔥 CHANAKYA STYLE (strict, strategic)
        if guru == "Chanakya":
            styled_advice = []

            for a in advice:
                if "high" in a.lower():
                    styled_advice.append(
                        "Control your expenses immediately. Wealth once lost is difficult to regain."
                    )
                elif "most on" in a:
                    styled_advice.append(
                        f"Excess focus on {top_cat} is a weakness. Discipline your spending or it will control you."
                    )
                else:
                    styled_advice.append(
                        "Maintain strict discipline. Even small leakages destroy great wealth."
                    )

        # 🌿 VIDURA STYLE (wise, balanced)
        elif guru == "Vidura":
            styled_advice = []

            for a in advice:
                if "high" in a.lower():
                    styled_advice.append(
                        "Excess spending disturbs balance in life. Practice moderation and mindful choices."
                    )
                elif "most on" in a and top_cat != "uncategorized":
                    styled_advice.append(
                        f"Your inclination towards {top_cat} should be guided with awareness, not impulse."
                    )
                elif top_cat == "uncategorized":
                    styled_advice.append(
                        "Your spending is unclear. Track categories properly to gain control over your finances."
                    )
                else:
                    styled_advice.append(
                        "Balance between needs and desires leads to lasting prosperity."
                    )

        # ✅ fallback safety
        else:
            styled_advice = advice

        return "\n".join(styled_advice)