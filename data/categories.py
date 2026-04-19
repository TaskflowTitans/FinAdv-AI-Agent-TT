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


def categorize(merchant: str) -> str:

    if not merchant:
        return "Others"

    merchant = merchant.lower()

    if any(x in merchant for x in ["swiggy", "zomato", "restaurant", "cafe", "food", "dominos", "pizza", "burger"]):
        return "Food"

    elif any(x in merchant for x in ["uber", "ola", "rapido", "transport", "taxi", "metro", "bus"]):
        return "Transport"

    elif any(x in merchant for x in ["mart", "store", "supermarket", "grocery", "bigbasket", "dmart", "reliance"]):
        return "Groceries"

    elif any(x in merchant for x in ["amazon", "flipkart", "myntra", "shopping", "store", "mall"]):
        return "Shopping"

    elif any(x in merchant for x in ["electricity", "bill", "recharge", "mobile", "internet", "wifi", "jio", "airtel", "vi"]):
        return "Bills"

    elif any(x in merchant for x in ["netflix", "prime", "hotstar", "spotify", "movie", "cinema"]):
        return "Entertainment"

    elif any(x in merchant for x in ["petrol", "fuel", "diesel", "hp", "indian oil", "bharat petroleum"]):
        return "Fuel"

    elif any(x in merchant for x in ["hospital", "pharmacy", "medical", "clinic"]):
        return "Health"

    return "Others"
