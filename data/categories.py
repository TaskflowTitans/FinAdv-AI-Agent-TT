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