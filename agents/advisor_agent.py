import os
from langchain_google_genai import ChatGoogleGenerativeAI


class AdvisorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,  # slight creativity
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def advise(self, analysis: dict):
        """
        Generate personalized financial advice based on analysis
        """

        prompt = f"""
You are a smart financial advisor.

Based on this financial analysis:

{analysis}

Give personalized, practical advice.

Rules:
- Be specific (mention amounts, categories)
- Give 3–5 actionable tips
- Be concise and helpful
- Focus on saving money and better habits

Format:
- Use bullet points
- No JSON, only plain text
"""

        response = self.llm.invoke(prompt)

        return response.content