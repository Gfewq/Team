# The static knowledge base, ready for RAG injection
# Mapped to the "Metaphor System" from the report

DIABETES_METAPHORS = {
    "glucose": "Fuel",
    "insulin": "Shield Charge",
    "hypoglycemia": "Empty Tank",
    "hyperglycemia": "Traffic Jam",
    "glucometer": "Magic Scanner"
}

SAFETY_PROTOCOLS = [
    {
        "id": 1,
        "keywords": ["dizzy", "shaky", "hungry", "sweaty"],
        "condition": "diabetes",
        "protocol": "HYPOGLYCEMIA_ALERT",
        "instruction": "URGENT: Child needs fast-acting glucose (Juice/Candy). Stop activity."
    },
    {
        "id": 2,
        "keywords": ["wheeze", "tight", "cough", "chest"],
        "condition": "asthma",
        "protocol": "ASTHMA_ATTACK",
        "instruction": "URGENT: Use rescue inhaler (Blue Puffer). Sit upright."
    }
]