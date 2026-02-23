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

load_dotenv()  # Loads .env automatically

gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# GEMINI API Key is Working!

# This is for Sanjay's Local Tesseract Installation (needed for testing)
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



# Initialize Gemini 1.5 Flash (faster and cheaper for OCR tasks)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_api_key)

def extract_with_vision(img_path):
    with open(img_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text", 
                "text": "Extract these details from this UPI screenshot: Amount, Date, Bank Name, and Description. Respond ONLY in JSON."
            },
            {
                "type": "image_url", 
                "image_url": f"data:image/jpeg;base64,{image_data}"
            },
        ]
    )
    
    response = llm.invoke([message])
    return response.content

# Run the test
if __name__ == "__main__":
    test_path = "data/samples/payment1.jpg"
    if os.path.exists(test_path):
        result = extract_with_vision(test_path)
        print("\n--- Extraction Result ---")
        print(result)
    else:
        print(f"❌ File not found at: {test_path}")