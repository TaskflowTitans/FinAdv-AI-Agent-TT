import os
import json
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.api_core import exceptions 


class ExtractionAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def extract(self, image_bytes):
        """
        Takes base64 image string and returns structured receipt data
        """
        prompt = """
        You are an expert receipt parser and data cleaner. 
        Extract: merchant name, date, list of items (name + price), total, and currency. 
        
        Rules:
        1. Date must be in YYYY-MM-DD format.
        2. Total must be a pure NUMBER (remove ₹, commas, or text).
        3. Ensure total is the sum of items.
        4. Default currency to INR if not found.
        
        Return ONLY valid JSON.
        """

        clean_base64 = image_bytes.split(",")[-1] if "," in image_bytes else image_bytes

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{clean_base64}"}
                },
            ]
        )

        # RETRY LOGIC for 429 Errors
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = self.llm.invoke([message])
                raw_content = response.content.replace("```json", "").replace("```", "").strip()
                return json.loads(raw_content)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries:
                    # Wait 30 seconds if we hit the limit
                    time.sleep(30)
                    continue
                return {"error": "Extraction failed", "details": str(e)}
