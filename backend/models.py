from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any

class UserMessage(BaseModel):
    user_id: str
    message: str
    age: int = 7
    condition: Literal["diabetes", "asthma"] = "diabetes"

class HealthLog(BaseModel):
    # This now matches your data_simulator.py output structure
    timestamp: str
    event_type: str
    value: float
    unit: str
    urgency: str
    metadata: Dict[str, Any]
    safety_status: Optional[str] = None
    health_score: Optional[float] = None
    # We add a catch-all for extra fields so it doesn't crash
    class Config:
        extra = "ignore"