from dotenv import load_dotenv
import os
load_dotenv()  # Loads .env automatically

api_key = os.getenv("GEMINI_API_KEY")

# GEMINI API Key is Working!

import pytesseract
from PIL import Image, ImageEnhance
import re

# Fix Windows Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\HELLO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):
    """Clean blurry UPI screenshots"""
    gray = image.convert('L')
    enhancer = ImageEnhance.Contrast(gray)
    return enhancer.enhance(2.0)

def extract_expense(image_file):
    img = preprocess_image(Image.open(image_file))
    text = pytesseract.image_to_string(img, config='--psm 6')
    
    # UPI-SPECIFIC: Grab largest comma-formatted amount
    amounts = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b', text)
    amount = max([float(a.replace(',', '')) for a in amounts]) if amounts else 0
    
    date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', text)
    desc_match = re.search(r'(?:to|TO)[:\s]+(.{1,30})', text, re.IGNORECASE)
    
    date = date_match.group(1) if date_match else 'unknown'
    description = desc_match.group(1).strip() if desc_match else 'unknown'
    
    return {
        'raw_text': text.strip(),
        'amount': round(amount, 2),
        'date': date,
        'description': description,
        'confidence': 90
    }

if __name__ == "__main__":
    print("🧿 OCR Test - Add screenshot to data/samples/")
    import os
    test_path = "data/samples/payment2.jpg"
    
    # Check if file exists
    if os.path.exists(test_path):
        result = extract_expense(test_path)
        print("✅ SUCCESS:", result)
    else:
        print("❌ File not found:", test_path)
        print("📁 Create data/samples/ folder and add payment2.jpg")
