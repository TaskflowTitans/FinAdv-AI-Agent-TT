import pytesseract
from PIL import Image
import pandas as pd
import re
import json
import os

# 🔹 If using Windows, uncomment and set path:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import pytesseract
from PIL import Image
import os

# 🔹 If using Windows, set correct path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# ==============================
# 1️⃣ Extract Data From Image
# ==============================

def extract_receipt_data(image_path):
    try:
        print(f"\nProcessing: {image_path}")

        # Open Image
        image = Image.open(image_path)

        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(image)

        # Print extracted text
        print("\n===== EXTRACTED TEXT =====\n")
        print(extracted_text)

        return extracted_text

    except Exception as e:
        print("Error:", e)
        return None


# ==============================
# 2️⃣ Process Images in Folder
# ==============================

image_folder = "receipts"

for file in os.listdir(image_folder):
    if file.endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(image_folder, file)
        extract_receipt_data(image_path)



     
    #==========================
    # 2️⃣ Auto Categorization
    # ===========================
def categorize_expense(text):
    data = {}
    if data["Paid_To"] and "electric" in data["Paid_To"].lower():
        data["Category"] = "Electricity Bill"
    elif data["Paid_To"] and "mobile" in data["Paid_To"].lower():
        data["Category"] = "Mobile Recharge"
    elif data["Paid_To"]:
        data["Category"] = "UPI Transfer"
    else:
        data["Category"] = "Other"

    return data


# ==============================
# 3️⃣ Convert to JSON
# ==============================

def save_as_json(data):
    with open("expense_data.json", "a") as f:
        json.dump(data, f)
        f.write("\n")


# ==============================
# 4️⃣ Save to CSV (Expense Tracker DB)
# ==============================

def save_to_csv(data):

    file_exists = os.path.isfile("expenses.csv")

    df = pd.DataFrame([data])

    if file_exists:
        df.to_csv("expenses.csv", mode='a', header=False, index=False)
    else:
        df.to_csv("expenses.csv", mode='w', header=True, index=False)


# ==============================
# 5️⃣ Run For Multiple Receipts
# ==============================

import os

# Run For Multiple Receipts
import os

# Run For Multiple Receipts
if __name__ == "__main__":
    folder_path = "receipts"  # Put all receipt images inside this folder
    
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' not found. Creating it now...")
        os.makedirs(folder_path)

    # Get list of files
    files = os.listdir(folder_path)

    if not files:
        print(f"No receipts found in '{folder_path}'. Please add receipt images to process.")
    else:
        for file in files:
            print(f"Processing: {file}")
            # Further code likely processes each file
 