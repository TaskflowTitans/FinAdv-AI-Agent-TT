from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import os
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0.3
)

def generate_financial_advice(df):
    if df.empty:
        return "No data available."

    # Convert dataframe to JSON (clean format)
    data = df.to_dict(orient="records")

    prompt = f"""
    Act like a strict financial coach.

    User expense data:
    {data}

    Rules:
    - Be honest and critical
    - Give practical saving advice
    - Highlight unnecessary spending

    Output in bullet points.
    """

    response = llm.invoke(prompt)
    return response.content