class AdvisorAgent:

    def advise(self, analysis, guru):

        if "error" in analysis:
            return "No advice available."

        total = analysis.get("total_spent", 0)
        avg = analysis.get("average_spend", 0)
        top_cat = analysis.get("top_category", "")

        advice = []

        # 🔹 Observations
        if avg > 500:
            advice.append(("high_spend", "Your daily spending is high."))

        if top_cat:
            advice.append(("top_category", f"You spend most on {top_cat}."))

        if total > 10000:
            advice.append(("total_high", "Your total spending is significantly high."))

        if not advice:
            advice.append(("balanced", "Your spending is balanced."))

        # 🧠 CHANAKYA (STRATEGIC)

        if guru == "Chanakya":

            styled = []

            for tag, text in advice:

                if tag == "high_spend":
                    styled.append(
                        "Excess daily spending weakens financial power. Control it immediately."
                    )

                elif tag == "top_category" and top_cat != "Others":
                    styled.append(
                        f"Your focus on {top_cat} reveals a vulnerability. Discipline this habit before it dominates you."
                    )

                elif tag == "total_high":
                    styled.append(
                        "Wealth without control is temporary. Reduce expenses and build reserves."
                    )

                else:
                    styled.append(
                        "Maintain strict discipline. Small financial leaks destroy long-term strength."
                    )

            return "\n".join(styled)

        # 🌿 VIDURA (BALANCED)
        
        elif guru == "Vidura":

            styled = []

            for tag, text in advice:

                if tag == "high_spend":
                    styled.append(
                        "Excess spending disturbs balance. Practice moderation in daily life."
                    )

                elif tag == "top_category" and top_cat != "Others":
                    styled.append(
                        f"Your inclination towards {top_cat} should be guided with awareness, not impulse."
                    )

                elif tag == "total_high":
                    styled.append(
                        "True prosperity comes from balance between earning and spending."
                    )

                else:
                    styled.append(
                        "A balanced financial path leads to stability and peace."
                    )

            return "\n".join(styled)

        # fallback
        return "No advice available."