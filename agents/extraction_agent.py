import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


class ExtractionAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",   # or gemini-2.0-flash if you're using
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def extract(self, image_bytes):
        """
        Takes image bytes and returns structured receipt data
        """

        prompt = """
You are an expert receipt parser.

Extract the following from the receipt image:
- merchant name
- date
- list of items (name + price)
- total amount
- currency

Return ONLY valid JSON in this format:
{
  "merchant": "",
  "date": "",
  "items": [{"name": "", "price": 0}],
  "total": 0,
  "currency": ""
}

Do not include any explanation.
"""

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_bytes}"
                    },
                },
            ]
        )

        response = self.llm.invoke([message])

        try:
            return json.loads(response.content)
        except Exception:
            return {
                "error": "Failed to parse response",
                "raw_output": response.content
            }