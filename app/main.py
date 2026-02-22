from dotenv import load_dotenv
import os
load_dotenv()  # Loads .env automatically

api_key = os.getenv("GEMINI_API_KEY")
print(api_key)  

# GEMINI API Key is Working!