from langchain.tools import tool
import json
# from tools.ocr import extract_with_gemini_vision
from tools.ocr import extract_with_tesseract

@tool
def ocr_extraction_tool(image_path: str) -> str:
    """
    Extracts transaction details from UPI screenshot.
    Input: image file path
    Output: JSON string
    """

    data = extract_with_tesseract(image_path)

    if not data:
        return json.dumps({"error": "Extraction failed"})

    # Ensure required fields exist
    data.setdefault("amount", None)
    data.setdefault("date", None)
    data.setdefault("description", "")

    return json.dumps(data)