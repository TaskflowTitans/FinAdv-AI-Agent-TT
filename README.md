# Welcome to TitansLedger - Financial AI Agent

## Project Introduction

TitansLedger – Financial AI Agent is an AI-powered system designed to automatically analyze digital payment receipts and transaction screenshots from platforms such as Google Pay, PhonePe, and Paytm. The system extracts relevant financial information from these images and converts it into structured data that can be used for expense tracking, financial analysis, and automated record keeping.

## Installation

### QUICK SETUP

<br>

Create a New Folder in your Local<br>
1. Open that New Folder in VS Code and clone the Repo

<br>

```bash
git clone https://github.com/TaskflowTitans/FinAdv-AI-Agent-TT.git
```

<br>

2. Change directory

<br>

```bash
cd .\FinAdv-AI-Agent-TT\
```

<br>

3. Install the Virtual Environment <br>
```bash
python -m venv venv
```

<br>

4. Activate the Virtual Env (For Windows) <br>
```bash
venv\scripts\activate
```

<br>

5. Install the requirements from requirements.txt <br>
```bash
pip install -r requirements.txt
```

<br>

<br>

Doing All this Steps will install you the Virtual Environment of our Project in your local. 

<br>

#### Integrate API Keys in your Local

Create a .env file in \FINADV-AI-Agent-TT\ folder which stores the Gemini and OpenAI API Keys as:
<br>
GEMINI_API_KEY = key_here <br>
OPENAI_API_KEY = key_here

<br>

## 🔍 OCR Strategy & Design Decision

### Initial Approach: Tesseract OCR

As per the project requirement, the initial implementation used:

<br>

‣ Tesseract OCR <br>
‣ OpenCV preprocessing (grayscale, thresholding, denoising)

<br>

The pipeline was :

```bash
Image → Tesseract OCR → Regex Parsing → Structured Data
```

### Challenges Observed

During testing with real Indian UPI payment screenshots (Google Pay, PhonePe, Paytm), several issues were observed:

<br>

‣ Inconsistent text alignment in screenshots <br>

‣ Mixed fonts and UI overlays <br>

‣ Broken line structures <br>

‣ Poor extraction of ₹ symbol and transaction IDs <br>

‣ Regular Expression errors

<br>

This resulted in :

<br>

‣ Low extraction accuracy (≈ 50–65%) <br>

‣ Manual correction requirements <br>

## 🚀Improved Approach: Gemini Vision

To improve reliability and accuracy, the OCR-based extraction was replaced with:

<br>

Google Gemini Vision model <br>

Updated pipeline:

```bash
Image → Gemini Vision → Structured JSON Extraction
```

Instead of relying on raw OCR + regex rules, Gemini Vision performs: <br>

‣ Context-aware text recognition <br>

‣ Semantic understanding of financial screenshots <br>

‣ Direct structured JSON output generation. <br>

## Running the Streamlit App

NOTE: App is still in development, it will output only dictionaries of uploaded payment recipts. <br>

After Cloning the Github Repository and installing the requirements, run the following commands to run the app (make sure you are in FinAdv-AI-Agent-TT folder) : <br>

```bash
streamlit run .\app\main.py
```

<br>

## Live Demo (Preffered)

You can also try the deployed version of the app here: <br>

```bash
https://titansledger.streamlit.app/
```

## Username and Password

Username and Password are temporarily Stored in json file. <br>
Username : Admin <br>
Password : 1234

## 🔑 API Configuration & Quota Notice

This project is powered by **Gemini 2.0 Flash**. To ensure the AI agents perform analysis and extraction without interruption, please review the following technical requirements.

### ⚠️ Note for Evaluators & Judges
The application is optimized for high-performance receipt processing. However, due to the strict rate limits of the **Google AI Studio Free Tier**, you may encounter `429 RESOURCE_EXHAUSTED` errors if multiple receipts are uploaded rapidly.

#### Recommended Setup:
* **Pay-As-You-Go Billing:** For the most stable experience, it is highly recommended to use an API Key with **billing enabled**. This increases the Requests Per Minute (RPM) and Daily Quota, allowing for seamless testing of the agentic loops.
* **Free Tier Usage:** If evaluating via the Free Tier, please allow **10–15 seconds** between receipt uploads to stay within the 'Tokens Per Minute' safety window.

#### Installation:
1. Obtain your API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a `.env` file in the root directory.
3. Add your key:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```

## Tech Stack

‣ Python <br>
‣ LangChain <br>
‣ Google Gemini Vision <br>
‣ Pandas <br>

## Team Members

‣ Aditi <br>
‣ Diya <br>
‣ Heer <br>
‣ Sanjay <br>