# Welcome to TitansLedger - Financial AI Agent
### Team :
Sanjay<br>
Heer<br>
Aditi<br>
Diya<br>

## Project Initiated✅

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

Create a .env file in \FINADV-AI-Agent-TT\ folder which stores the Gemini and Groq API Keys as:<br>
GEMINI_API_KEY = key_here

<br>

GROQ_API_KEY = key_here

<br>

## Week 1 

### DAY 1

‣ Project Initiated <br>
‣ Team Tasks Assigned ✅ <br>

### DAY 2

‣ Git Environment Created <br>

### DAY 3

‣ FlowChart Created

### DAY 4 

‣ Tasks Divided

### DAY 5

‣ Virtual Environment Created <br>
‣ Requirements.txt Added <br>
‣ OCR Added <br>
‣ API KEYS Setup ✅ <br>

### DAY 6

‣ Worked on OCR and Categorization

### DAY 7

‣ README Updated <br>
‣ FlowChart Added <br>

## Week 2

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

‣ Direct structured JSON output generation