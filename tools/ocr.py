from dotenv import load_dotenv
import os
import pytesseract
from PIL import Image, ImageEnhance
from PIL import Image, ImageEnhance, ImageFilter
import re
import base64
import json 
from datetime import datetime
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

def calculate_confidence(data):
    score = 0

    if data.get("amount") and data["amount"] > 0:
        score += 0.4

    if data.get("date"):
        score += 0.2

    if data.get("description") and data["description"] != "Unknown":
        score += 0.2

    if data.get("sender") and data["sender"] != "Unknown":
        score += 0.2

    return round(score, 2)

AMOUNT_PATTERNS = [
    r'Paid\s*₹\s?([\d,]+\.?\d*)',
    r'₹\s?([\d,]+\.?\d*)',
    r'Amount Paid\s*₹?\s?([\d,]+\.?\d*)',
    r'Money Deposited.*?₹?\s?([\d,]+\.?\d*)',
    r'₹\s?([\d,]+\.?\d*)',
    r'Rs\.?\s?([\d,]+\.?\d*)',
    r'INR\s?([\d,]+\.?\d*)',

    r'Total\s*[:\-]?\s*([\d,]+\.?\d*)',
    r'Grand Total\s*[:\-]?\s*([\d,]+\.?\d*)',
    r'Amount\s*[:\-]?\s*([\d,]+\.?\d*)',
    r'Paid\s*[:\-]?\s*([\d,]+\.?\d*)',
    r'Sub Total\s*[:\-]?\s*([\d,]+\.?\d*)'
]

DATE_PATTERNS = [
    r'\d{1,2}\s[A-Za-z]{3,9}\s\d{4}\s*\d{1,2}:\d{2}',
    r'\d{1,2}/\d{1,2}/\d{2,4}',
    r'\d{1,2}-\d{1,2}-\d{2,4}',
    r'\d{1,2}\s[A-Za-z]{3,9}\s\d{2,4}'
]

MERCHANT_KEYWORDS = [
    "paid to",
    "sent to",
    "to",
    "merchant",
    "receiver"
]


def extract_amount(text):

    invoice_total = extract_invoice_total(text)

    if invoice_total:
        return invoice_total

    amounts = []

    for pattern in AMOUNT_PATTERNS:

        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:

            try:
                value = float(match.replace(",", ""))

                if 1 <= value <= 100000:
                    amounts.append(value)

            except:
                pass

    if amounts:
        return max(amounts)

    return 0

def extract_invoice_total(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):

        lower = line.lower().strip()

        if lower in ["total", "grand total", "amount payable"]:

            if i + 1 < len(lines):

                next_line = lines[i + 1]

                match = re.search(
                    r'([\d,]+\.?\d*)',
                    next_line
                )

                if match:

                    try:
                        return float(
                            match.group(1).replace(",", "")
                        )

                    except:
                        pass

    return None

def extract_date(text):

    for pattern in DATE_PATTERNS:

        matches = re.findall(pattern, text)

        if matches:

            raw_date = matches[0]

            formats = [
                "%d/%m/%Y",
                "%d/%m/%y",
                "%d-%m-%Y",
                "%d-%m-%y",
                "%d %b %Y",
                "%d %B %Y",
                "%d %b %Y %H:%M",
                "%d %B %Y %H:%M"
            ]

            for fmt in formats:

                try:
                    parsed = datetime.strptime(raw_date, fmt)
                    return parsed.strftime("%Y-%m-%d")

                except:
                    pass

    return None


def extract_merchant(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):

        lower = line.lower().strip()

        if lower.startswith("paid to"):

            if i + 1 < len(lines):
                return lines[i + 1].strip()

        if lower.startswith("sent to"):

            if i + 1 < len(lines):
                return lines[i + 1].strip()

    return "Unknown"


def detect_upi(text):

    match = re.search(
        r'[\w\.-]+@[\w]+',
        text
    )

    if match:
        return match.group()

    return None

def extract_sender(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):

        lower = line.lower().strip()

        if lower in ["from", "sender"]:

            if i + 1 < len(lines):
                return lines[i + 1].strip()

        if lower.startswith("from:"):
            return line.split(":",1)[1].strip()

    return "Unknown"

def extract_transaction_id(text):

    match = re.search(
        r'(?:UPI Transaction ID|Transaction ID)\s*[:\-]?\s*(\d{8,20})',
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return None

def smart_receipt_parser(text):

    amount = extract_amount(text)

    date = extract_date(text)

    merchant = extract_merchant(text)

    upi_id = detect_upi(text)

    parsed = {
        "amount": amount,
        "date": date,
        "description": merchant,
        "sender": extract_sender(text),
        "upi_id": upi_id,
        "currency": "INR",
        "fallback": False,
        "transaction_id": extract_transaction_id(text)
    }

    parsed["confidence_score"] = calculate_confidence(parsed)

    print("\n===== RAW OCR TEXT =====")
    print(text)

    print("\n===== PARSED RESULT =====")
    print(parsed)

    return parsed

def clean_text_to_json(text):

    try:
        llm = get_llm()

        prompt = f"""
        Extract structured data from this receipt.

        STRICT RULES:
        - Return ONLY valid JSON
        - No markdown
        - No explanation
        - Keys: amount (number), date (YYYY-MM-DD), description, sender, currency

        Text:
        {text}
        """

        response = llm.invoke(prompt)

        content = response.content

        parsed = extract_json_from_response(content)

        if parsed:
            parsed["fallback"] = False
            return parsed

        return fallback_parser(text)

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

    for attempt in range(3):

        response = requests.post(
            url,
            headers=headers,
            data=data,
            timeout=30
        )

        if response.status_code == 202:
            break

        time.sleep(2)

    if response.status_code != 202:
        return {"error": response.text}

    operation_url = response.headers["Operation-Location"]

    while True:
        result = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": key}).json()

        if result["status"] == "succeeded":
            break
        elif result["status"] == "failed":
            return {"error": "OCR failed"}

        time.sleep(1)

    lines = []
    for page in result["analyzeResult"]["readResults"]:
        for line in page["lines"]:
            lines.append(line["text"])

    full_text = "\n".join(lines)

    return {"raw_text": full_text}

def preprocess_for_azure(image_path):

    img = Image.open(image_path)

    img = img.convert("L")

    img = ImageEnhance.Contrast(img).enhance(1.5)

    img = img.filter(ImageFilter.SHARPEN)

    temp = image_path + "_clean.png"

    img.save(temp)

    return temp

def detect_receipt_type(text):

    raw = text.lower()

    if "upi transaction id" in raw:
        return "upi"

    elif "google pay" in raw:
        return "upi"

    elif "phonepe" in raw:
        return "upi"

    elif "paytm" in raw:
        return "upi"

    elif "invoice" in raw:
        return "invoice"

    elif "gst" in raw:
        return "gst_invoice"

    elif "account number" in raw:
        return "bank"

    else:
        return "generic"

def parse_upi_receipt(text):

    return {
        "amount": extract_amount(text),
        "date": extract_date(text),
        "description": extract_merchant(text),
        "sender": extract_sender(text),
        "upi_id": detect_upi(text),
        "transaction_id": extract_transaction_id(text),
        "currency": "INR",
        "fallback": False
    }

def extract_with_azure_pipeline(image_path):

    clean_path = preprocess_for_azure(image_path)
    ocr_result = extract_with_azure_vision(clean_path)

    if "error" in ocr_result:
        return ocr_result

    receipt_type = detect_receipt_type(
        ocr_result["raw_text"]
    )

    if receipt_type == "upi":

        cleaned = parse_upi_receipt(
            ocr_result["raw_text"]
        )
    else:

        cleaned = smart_receipt_parser(
            ocr_result["raw_text"]
        )

    cleaned["receipt_type"] = receipt_type

    if cleaned["amount"] <= 0:

        return {
            "error": "Amount extraction failed",
            "raw_text": ocr_result["raw_text"]
        }
    cleaned["raw_text"] = ocr_result["raw_text"]

    if "confidence_score" not in cleaned:
        cleaned["confidence_score"] = calculate_confidence(cleaned)

    return cleaned