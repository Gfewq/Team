# This is your "Database". 
# It maps a specific Situation (what happens) to a Protocol (what the AI must do).

# Mapped to Team Member 2's "EventType" Enum
SAFETY_PROTOCOLS = [
    # --- GLUCOSE ---
    {
        "id": 1,
        "situation": "glucose_drop low hypoglycemia DANGER",
        "instruction": "URGENT: Leo is hungry! We need Magic Fuel (Juice) immediately."
    },
    {
        "id": 2,
        "situation": "glucose_spike high hyperglycemia DANGER",
        "instruction": "URGENT: Too many sparkles! We need a Shield Recharge (Insulin)."
    },
    
    # --- HEART RATE ---
    {
        "id": 3,
        "situation": "heart_rate_elevated high pulse stress MONITOR",
        "instruction": "Leo's heart is racing like a bunny! Let's take 3 deep breaths together."
    },
    {
        "id": 4, 
        "situation": "heart_rate_low slow pulse tired MONITOR",
        "instruction": "Leo feels very sleepy and slow. Let's tell a grown-up."
    },

    # --- OXYGEN / ASTHMA ---
    {
        "id": 5,
        "situation": "asthma_risk high pollen poor air DANGER",
        "instruction": "The air is dusty! Leo needs his Air Potion (Inhaler) to breathe easy."
    },
    {
        "id": 6,
        "situation": "oxygen_saturation low spo2 breathing difficulty DANGER",
        "instruction": "Leo is having trouble roaring. We need to sit down and breathe deeply."
    },

    # --- MOOD / MEDICATION ---
    {
        "id": 7,
        "situation": "mood_indicator sad low mood tired MONITOR",
        "instruction": "Leo feels a bit droopy. Do you want a hug or a story?"
    },
    {
        "id": 8,
        "situation": "medication_due reminder insulin HIGH",
        "instruction": "Time for a power-up! Let's get our Shield ready."
    },

    # --- GENERAL ---
    {
        "id": 9,
        "situation": "glucose_normal safe stable happy activity_level",
        "instruction": "Leo feels brave and strong! Let's play a game!"
    }
]