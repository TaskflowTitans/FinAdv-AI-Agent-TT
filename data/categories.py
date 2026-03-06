import pytesseract
from PIL import Image
import pandas as pd
import re
import json
import os
from tools.langchain_tool import ocr_extraction_tool


# Install Tesseract OCR and set path if necessary (Set this path for your System)
# If using Windows, uncomment and set path:

# Heer's Local Tesseract Installation
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Sanjay's Local Tesseract Installation 
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\HELLO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def categorize_expense(text):
    data = {}
    paid_to = text.lower()
    if "electric" in paid_to:
        data["Category"] = "Electricity Bill"
    elif "mobile" in paid_to:
        data["Category"] = "Mobile Recharge"
    elif "upi" in paid_to:
        data["Category"] = "UPI Transfer"
    else:
        data["Category"] = "Other"

    return data

def save_as_json(data):
    with open("data/output/expense_data.json", "a") as f:
        json.dump(data, f)
        f.write("\n")

def save_to_csv(data):
    file_path = "data/output/expenses.csv"
    file_exists = os.path.isfile(file_path)

    df = pd.DataFrame([data])

    if file_exists:
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, mode='w', header=True, index=False)

# Run For Multiple Receipts
if __name__ == "__main__":
    folder_path = "data/samples"

    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' not found.")
    else:
        files = os.listdir(folder_path)

        for file in files:

            if file.endswith((".png", ".jpg", ".jpeg")):

                image_path = os.path.join(folder_path, file)

                print(f"Processing: {file}")

                text = ocr_extraction_tool.invoke({"image_path": image_path})

                data = categorize_expense(text)

                save_as_json(data)
                save_to_csv(data)
                print(f"Data saved for {file}: {data}\n")