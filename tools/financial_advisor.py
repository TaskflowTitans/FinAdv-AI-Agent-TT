from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tenacity import retry, stop_after_attempt, wait_exponential

import os
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0.3
)

fallback_llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=8))
def call_primary_llm(prompt):
    return llm.invoke(prompt)

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

    # response = llm.invoke(prompt)
    # return response.content
    try:
        response = call_primary_llm(prompt)
        return response.content

    except Exception as e:
        print("⚠ Primary LLM failed, using fallback...", e)

        try:
            response = fallback_llm.invoke(prompt)
            return response.content
        except:
            return "⚠ Unable to generate advice right now. Try again later."