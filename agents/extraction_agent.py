import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


class ExtractionAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

#     def extract(self, image_bytes):
#         """
#         Takes image bytes and returns structured receipt data
#         """

#         prompt = """
# You are an expert receipt parser.

# Extract the following from the receipt image:
# - merchant name
# - date
# - list of items (name + price)
# - total amount
# - currency

# Return ONLY valid JSON in this format:
# {
#   "merchant": "",
#   "date": "",
#   "items": [{"name": "", "price": 0}],
#   "total": 0,
#   "currency": ""
# }

# Do not include any explanation.
# """

#         message = HumanMessage(
#             content=[
#                 {"type": "text", "text": prompt},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{image_bytes}"
#                     },
#                 },
#             ]
#         )

#         response = self.llm.invoke([message])

#         try:
#             return json.loads(response.content)
#         except Exception:
#             return {
#                 "error": "Failed to parse response",
#                 "raw_output": response.content
#             }

    def extract(self, image_bytes):
        """
        Takes base64 image string and returns structured receipt data
        """
        prompt = """
        You are an expert receipt parser. Extract: merchant name, date, 
        list of items (name + price), total, and currency. 
        Return ONLY JSON.
        """

        # Ensure there is no 'data:image/jpeg;base64,' prefix 
        # if it was already added in main.py to avoid double-prefixing
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

        try:
            # 1. Call the LLM
            response = self.llm.invoke([message])
            
            # 2. Clean markdown backticks
            raw_content = response.content.replace("```json", "").replace("```", "").strip()
            
            # 3. Parse JSON
            return json.loads(raw_content)

        except Exception as e:
            # We use 'str(e)' here instead of 'response' because 
            # if the API failed, 'response' was never created.
            print(f"DEBUG Error: {str(e)}") 
            return {
                "error": "Extraction failed",
                "details": str(e)
            }