from dotenv import load_dotenv
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.langchain_tool import ocr_extraction_tool
from tools.langchain_tool import ocr_extraction_tool
from langchain.agents import create_agent

load_dotenv()  # Loads .env automatically

api_key = os.getenv("GEMINI_API_KEY")

# GEMINI API Key is Working!

# Integrating langchain tool with Agent

# Initialize Gemini
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Create agent with tools
agent = create_agent(
    model=model,
    tools=[ocr_extraction_tool],
    system_prompt="You are a financial AI assistant that extracts transaction details from images."
)

if __name__ == "__main__":
    result = agent.invoke(
        {"messages": [
            {"role": "user", "content": "Extract transaction details from data/samples/payment4.png"}
        ]}
    )

    print("\nFinal Output:\n")
    print(result["messages"][-1].content)
