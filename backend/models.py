from pydantic import BaseModel
from typing import List, Optional, Literal

class UserMessage(BaseModel):
    user_id: str
    message: str
    age: int = 7
    condition: Literal["diabetes", "asthma"] = "diabetes"
    context: Optional[str] = "home"

class LeoResponse(BaseModel):
    reply: str
    mood: str
    animation_id: str
    safety_flag: bool

class HealthLog(BaseModel):
    user_id: str
    metric_type: str
    value: float
    unit: str