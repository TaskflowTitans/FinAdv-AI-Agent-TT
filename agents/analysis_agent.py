import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI


class AnalysisAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def analyze(self, transactions: list):
        """
        Analyze spending patterns from transaction list
        """

        prompt = f"""
You are a financial analysis expert.

Analyze the following transactions:

{json.dumps(transactions)}

Return ONLY JSON in this format:
{{
  "top_category": "",
  "total_spent": 0,
  "average_spend": 0,
  "high_spending_days": [],
  "insights": []
}}

Rules:
- top_category = category with highest total spend
- total_spent = sum of all amounts
- average_spend = average per transaction
- high_spending_days = days where spending > 2x average
- insights = 3-5 useful financial observations

NO explanation. ONLY JSON.
"""

        response = self.llm.invoke(prompt)

        try:
            return json.loads(response.content)
        except Exception:
            return {
                "error": "Analysis failed",
                "raw_output": response.content
            }