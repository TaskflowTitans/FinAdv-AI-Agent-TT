from langchain.tools import tool
import json
from tools.ocr import extract_with_gemini_vision

@tool
def ocr_extraction_tool(image_path: str) -> str:
    """
    Extracts transaction details from UPI screenshot.
    Input: image file path
    Output: JSON string
    """

    data = extract_with_gemini_vision(image_path)

    if data is None:
        return "Extraction failed"

    return json.dumps(data)