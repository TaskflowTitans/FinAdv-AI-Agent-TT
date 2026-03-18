CATEGORIES = {

    "food": [
        "zomato", "swiggy", "restaurant", "food", "cafe",
        "kirana", "dmart", "grocery"
    ],

    "transport": [
        "ola", "uber", "rapido", "auto", "bus", "train",
        "irctc", "metro"
    ],

    "entertainment": [
        "netflix", "amazon prime", "bgmi", "spotify",
        "youtube", "hotstar"
    ],

    "medical": [
        "hospital", "medical", "pharmacy", "clinic",
        "doctor", "lab", "medicine"
    ],

    "transfer": [
        "payment to", "upi", "transfer", "sent to"
    ],

    "Finance & Bills": [
        "bill","recharge","electricity", "water", "gas", "phone", "internet",
        "insurance", "loan", "credit card", "debit card","broadband","jio","airtel","vodafone","bsnl","dish tv","tatasky","postpaid","prepaid"
    ],

    "Shopping & E-commerce": [
        "amazon", "flipkart", "myntra", "ajio", "snap","nykaa","meesho","delivery","courier","bluedart"
        ],

    "Government": [
        "income tax","challan","digilocker","passport","aadhar"
    ],

    "Investment": [
        "zerodha","groww","upstox","mutual fund","stock","crypto"
    ],

    "Travel & Stay": [
        "makemytrip","goibibo","hotel","airbnb","indigo","flight","where is my train","paytm","bookmyshow","booking","visa","homestay"
    ],

    "Housing & Utilities": [
        "rent","maintenance","maid","cook","urban company","plumber","capenter","urban clap","society"
    ],

    "uncategorized": []
}


def categorize(description=None, bank_name=None, upi_id=None):

    text = " ".join([
        str(description or ""),
        str(bank_name or ""),
        str(upi_id or "")
    ]).lower()

    for category, keywords in CATEGORIES.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "uncategorized"
