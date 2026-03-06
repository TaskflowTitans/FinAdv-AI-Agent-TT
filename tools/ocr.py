from urllib import response
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import cv2
import pytesseract
from PIL import Image, ImageEnhance
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import base64
import json

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# GEMINI API Key is Working!

# This is for Sanjay's Local Tesseract Installation (needed for testing)
# Install Tesseract OCR and set path if necessary (Set this path for your System)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\HELLO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# To Show Image

# def show_image(img_path):
#     image = cv2.imread(img_path)
#     if image is None:
#         print("Error: Could not read image. Check the file path.")
#         return
#     cv2.imshow("Image Window", image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# show_image("payment1.jpg")

# With OCR

image_path = "data/samples/payment6.png"
image = cv2.imread(image_path)

image = cv2.resize(image, None, fx=1.5, fy=1.5)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

gray = cv2.bilateralFilter(gray, 9, 75, 75)

_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

custom_config = r'--oem 3 --psm 6'

text = pytesseract.image_to_string(thresh, config=custom_config)

# print("\n===== RAW OCR TEXT =====\n")
# print(text)

# OCR is not working well for all samples, especially those with complex backgrounds and layouts.

# With GEMINI Vision Method

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_api_key)

from langchain_core.messages import HumanMessage

def extract_json_from_response(text):
    """
    Extracts valid JSON object from messy LLM response.
    Handles markdown blocks and extra text.
    """

    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠ JSON decode failed after extraction")
            print(json_str)
            return None

    print("⚠ No JSON object found")
    print(text)
    return None

def extract_with_gemini_vision(img_path):
    with open(img_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """
You are a financial data extraction API.

You MUST respond with ONLY a valid JSON object.
No markdown.
No explanations.
No text before or after JSON.

JSON schema:
{
  "amount": number | null,
  "currency": string | null,
  "date": string | null,
  "time": string | null,
  "bank_name": string | null,
  "upi_id": string | null,
  "transaction_id": string | null,
  "payment_status": string | null,
  "description": string | null
}

If a field is missing, use null.
"""
            },
            {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{image_data}"
            },
        ]
    )

    response = llm.invoke([message])

    clean_data = extract_json_from_response(response.content)

    return clean_data
    
# if __name__ == "__main__":
#     test_path = "data/samples/payment2.jpg"

#     if os.path.exists(test_path):
#         result = extract_with_gemini_vision(test_path)
#         print("\n===== STRUCTURED OUTPUT =====\n")
#         print(json.dumps(result, indent=4))
#     else:
#         print("❌ File not found")