import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI


class CleaningAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def clean(self, extracted_data: dict):
        """
        Cleans and validates extracted receipt data
        """

        prompt = f"""
You are a financial data cleaning assistant.

Fix and normalize this receipt data:

INPUT:
{json.dumps(extracted_data)}

TASK:
- Ensure all fields exist: merchant, date, items, total, currency
- Convert total to a NUMBER (remove ₹, commas, text)
- Ensure date is in YYYY-MM-DD format
- Ensure items is a list of objects with name + price (number)
- Remove duplicate or invalid items
- Ensure total ≈ sum of items (fix if needed)
- Currency should be INR if not specified

OUTPUT:
Return ONLY valid JSON:
{{
  "merchant": "",
  "date": "",
  "items": [{{"name": "", "price": 0}}],
  "total": 0,
  "currency": ""
}}

NO explanation. ONLY JSON.
"""

        response = self.llm.invoke(prompt)

        try:
            raw_content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_content)
        except Exception as e:
            print(f"DEBUG: Raw response was: {response.content}")
            return {"error": "Failed to parse JSON", "details": str(e)}