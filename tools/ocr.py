from dotenv import load_dotenv
import os
# import cv2
import pytesseract
from PIL import Image, ImageEnhance
import re
import base64
import json 
# from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime
# from langchain_openai import ChatOpenAI
from google.cloud import vision
from langchain_google_genai import ChatGoogleGenerativeAI
import io
import requests
import time

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "tesseract"
    
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

# image_path = "data/samples/payment6.png"
# image = cv2.imread(image_path)

# image = cv2.resize(image, None, fx=1.5, fy=1.5)

# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# gray = cv2.bilateralFilter(gray, 9, 75, 75)

# _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# custom_config = r'--oem 3 --psm 6'

# text = pytesseract.image_to_string(thresh, config=custom_config)

# print("\n===== RAW OCR TEXT =====\n")
# print(text)

# OCR is not working well for all samples, especially those with complex backgrounds and layouts.

# pytesseract path for local

# Do not remove this line, as it is necessary for pytesseract to work on Windows. Update the path if tesseract is installed elsewhere on your system. just comment it if you have a different path.

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Update this path if tesseract is installed elsewhere

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

# def extract_with_tesseract(img_path):

#     image = Image.open(img_path)
#     image = ImageEnhance.Contrast(image).enhance(2)
#     image = image.convert("L")
#     image = image.point(lambda x: 0 if x < 140 else 255, '1')
#     custom_config = r'--oem 3 --psm 6'

#     text = pytesseract.image_to_string(image, config=custom_config)
#     print("\n===== OCR TEXT =====\n", text)

#     lines = text.split("\n")
#     amount = 0

#     for line in lines:
#         match = re.search(r"\d{1,3}(,\d{3})+", line)
#         if match:
#             amount = float(match.group().replace(",", ""))
#             break
        
#     is_autopay = "autopay" in text.lower() or "upi lite" in text.lower()

#     for line in lines:
#         if "up to" in line.lower() or "₹" in line or "€" in line:
#             match = re.search(r"\b\d{2,6}\b", line)
#             if match:
#                 amount = float(match.group())
#                 break

#     # 🔥 RULE 1: "₹500" or "₹ 500"
#     for line in lines:
#         match = re.search(r"[₹]\s?(\d+[,\d]*)", line)
#         if match:
#             amount = float(match.group(1).replace(",", ""))
#             break

#     # 🔥 RULE 2: BIG NUMBER (center text like 26,200)
#     if amount == 0:
#         for line in lines:
#             match = re.search(r"\d{1,3}(,\d{3})+", line)
#             if match:
#                 amount = float(match.group().replace(",", ""))
#                 break

#     # 🔥 RULE 3: Payment screen fallback (ONLY if contains "paid" or "completed")
#     if amount == 0:
#         for line in lines:
#             if "paid" in line.lower() or "completed" in line.lower():
#                 match = re.search(r"\d{3,6}", line)
#                 if match:
#                     val = int(match.group())
#                     if val > 100:   # ignore 91, 30 etc
#                         amount = val
#                         break
        

#     # -------- DATE (ALWAYS DEFINE) --------
#     date = None

#     date_match = re.search(r"\d{1,2}\s\w+\s\d{4}", text)

#     if date_match:
#         try:
#             date = datetime.strptime(date_match.group(), "%d %b %Y").strftime("%Y-%m-%d")
#         except:
#             pass

#         # -------- MERCHANT (ALWAYS DEFINE) --------
#     merchant = "Unknown"

#     for line in lines:
#         if line.lower().startswith("to"):
#             merchant = re.sub(r"to[:\s]*", "", line, flags=re.IGNORECASE).strip()

#             # remove noise words
#             merchant = re.sub(r"paytm|bank|payments", "", merchant, flags=re.IGNORECASE).strip()
#             break

#     # -------- SENDER (PAYER) --------
#     sender = "Unknown"

#     for line in lines:
#         if line.lower().startswith("from"):
#             sender = re.sub(r"from[:\s]*", "", line, flags=re.IGNORECASE)
#             sender = sender.replace("@", "").strip()
#             break

#     if amount == 0:
#         print("⚠ No reliable amount found")
#         return {
#             "amount": 0,
#             "date": None,
#             "description": "Unknown",
#             "sender": "Unknown",
#             "currency": "INR"
#         }
    
#     return {
#         "amount": amount,
#         "date": date,
#         "description": merchant,
#         "sender": sender,
#         "currency": "INR",
#         "note": "autopay_detected" if is_autopay else "payment"
#     }


def extract_with_google_vision(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)

    if response.error.message:
        return {"error": response.error.message}

    texts = response.text_annotations

    if not texts:
        return {"error": "No text found"}

    extracted_text = texts[0].description

    return {
        "raw_text": extracted_text
    }

def fallback_parser(text):

    amount = 0

    # ₹ patterns
    match = re.search(r"₹\s?(\d+[,\d]*)", text)
    if match:
        amount = float(match.group(1).replace(",", ""))

    # fallback number detection
    if amount == 0:
        match = re.search(r"\b\d{2,6}\b", text)
        if match:
            val = int(match.group())
            if val > 50:
                amount = val

    # date
    date = None
    date_match = re.search(r"\d{1,2}\s\w+\s\d{4}", text)
    if date_match:
        try:
            date = datetime.strptime(date_match.group(), "%d %b %Y").strftime("%Y-%m-%d")
        except:
            pass

    # merchant
    merchant = "Unknown"
    lines = text.split("\n")
    for line in lines:
        if "to" in line.lower():
            merchant = line.replace("to", "").strip()
            break

    return {
        "amount": amount,
        "date": date,
        "description": merchant,
        "sender": "Unknown",
        "currency": "INR",
        "fallback": True
    }

def clean_text_to_json(text):

    try:
        llm = get_llm()

        prompt = f"""
        You are a strict receipt parser.

        Extract:
        - amount (number only)
        - date (YYYY-MM-DD)
        - description (merchant)
        - sender
        - currency (INR)

        Text:
        {text}

        Return ONLY valid JSON.
        """

        response = llm.invoke(prompt)

        import re, json

        content = response.content
        content = content.replace("```json", "").replace("```", "")

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if match:
            return json.loads(match.group(0))

        return {"error": "Invalid JSON"}

    except Exception as e:
        print("⚠ Gemini failed:", e)
        return fallback_parser(text)

def extract_with_google_pipeline(image_path):
    
    ocr_result = extract_with_google_vision(image_path)

    if "error" in ocr_result:
        return ocr_result

    cleaned = clean_text_to_json(ocr_result["raw_text"])

    return cleaned

def extract_with_azure_vision(image_path):
    endpoint = os.getenv("AZURE_VISION_ENDPOINT")
    key = os.getenv("AZURE_VISION_KEY")

    url = endpoint + "vision/v3.2/read/analyze"

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream"
    }

    with open(image_path, "rb") as f:
        data = f.read()

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 202:
        return {"error": response.text}

    # 🔥 Get operation URL
    operation_url = response.headers["Operation-Location"]

    # 🔁 Poll result
    while True:
        result = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": key}).json()

        if result["status"] == "succeeded":
            break
        elif result["status"] == "failed":
            return {"error": "OCR failed"}

        time.sleep(1)

    # 🔥 Extract text
    lines = []
    for page in result["analyzeResult"]["readResults"]:
        for line in page["lines"]:
            lines.append(line["text"])

    full_text = "\n".join(lines)

    return {"raw_text": full_text}

def extract_with_azure_pipeline(image_path):

    ocr_result = extract_with_azure_vision(image_path)

    if "error" in ocr_result:
        return ocr_result

    cleaned = clean_text_to_json(ocr_result["raw_text"])

    return cleaned