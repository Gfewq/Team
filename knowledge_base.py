# This is your "Database". 
# It maps a specific Situation (what happens) to a Protocol (what the AI must do).

SAFETY_PROTOCOLS = [
    {
        "id": 1,
        # Add "LOW" and "HYPO" so the search hits these words hard
        "situation": "Glucose LOW hypoglycemia drop dropping low number under 4", 
        "instruction": "URGENT: Do not start a game. Tell the child you are hungry and need 'magic fuel' (juice or candy). Alert parents."
    },
    {
        "id": 2,
        # Add "HIGH" and "HYPER"
        "situation": "Glucose HIGH hyperglycemia spike rising high number over 10", 
        "instruction": "Suggest drinking water ('hydration potion'). Ask if they have taken their insulin ('shield recharge')."
    },
    {
        "id": 3,
        "situation": "Child is feeling sad or anxious about the device.",
        "instruction": "Empathize. Remind them that even superheroes have gadgets. Suggest a breathing exercise."
    },
    {
        "id": 4,
        "situation": "Routine check-in, levels are normal/stable.",
        "instruction": "Be playful. Suggest a game or ask about their day. Celebrate the 'perfect score'."
    }
]