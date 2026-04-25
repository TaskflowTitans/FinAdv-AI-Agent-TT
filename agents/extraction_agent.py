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
    def extract(self, image_bytes):

        last_error = None

        for attempt in range(2):  # retry once

            try:
                img_data = base64.b64decode(image_bytes.split(",")[-1])

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(img_data)
                    temp_path = tmp.name

                result = extract_with_azure_pipeline(temp_path)

                if "error" not in result:
                    confidence = result.get("confidence_score", 0)

                    if confidence < 0.5:
                        result["warning"] = "Low confidence extraction"

                    return result

            except Exception as e:
                last_error = str(e)

        return {"error": last_error or "Extraction failed"}
