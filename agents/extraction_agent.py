import os
import json
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.api_core import exceptions
# from tools.ocr import extract_with_tesseract
import tempfile
import base64
from tools.ocr import extract_with_azure_pipeline
# from tools.ocr import extract_with_google_pipeline

class ExtractionAgent:
    def __init__(self):
        pass

    def extract(self, image_bytes):

        try:
            # convert base64 → image
            img_data = base64.b64decode(image_bytes.split(",")[-1])

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_data)
                temp_path = tmp.name

            result = extract_with_azure_pipeline(temp_path)

            if (
                "error" in result
                or not result.get("amount")
                or result.get("amount") == 0
                or result.get("description") in ["Unknown", "", None]
            ):
                return {"error": "Low confidence extraction"}

            return result

        except Exception as e:
            return {"error": str(e)}
