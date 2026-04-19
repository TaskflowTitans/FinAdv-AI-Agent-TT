import os
import json
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.api_core import exceptions
from tools.ocr import extract_with_tesseract
import tempfile
import base64


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
                import re

                text = response.content

                # remove markdown
                text = text.replace("```json", "").replace("```", "").strip()

                # extract JSON safely
                match = re.search(r"\{.*\}", text, re.DOTALL)

                if match:
                    try:
                        return json.loads(match.group(0))
                    except Exception as e:
                        return {"error": "JSON parsing failed", "details": str(e)}

                return {"error": "Invalid JSON", "details": text}
            
            except Exception as e:
                # If rate limit → fallback to OCR
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    try:
                        # Convert base64 to temp image file
                        img_data = base64.b64decode(clean_base64)

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            tmp.write(img_data)
                            temp_path = tmp.name

                        ocr_result = extract_with_tesseract(temp_path)

                        if ocr_result and "error" in ocr_result:
                            return ocr_result   # 🔥 propagate error directly

                        if ocr_result:
                            return {
                                "merchant": ocr_result.get("description", "Unknown"),
                                "sender": ocr_result.get("sender", "Unknown"),
                                "date": ocr_result.get("date"),
                                "items": [],
                                "total": ocr_result.get("amount", 0),
                                "currency": "INR",
                                "fallback": True
                            }

                    except Exception as ocr_error:
                        return {
                            "error": "OCR could not detect amount properly",
                            "details": str(ocr_error)
                        }

                return {"error": "Extraction failed", "details": str(e)}
