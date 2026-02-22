CATEGORIES = {
    'food': ['zomato', 'swiggy', 'kirana', 'dmart'],
    'transport': ['ola', 'uber', 'auto'],
    'entertainment': ['bgmi', 'netflix'],
    'uncategorized': []
}

def categorize(description):
    desc_lower = description.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category
    return 'uncategorized'
