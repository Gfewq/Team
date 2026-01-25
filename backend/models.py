from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime


class UserMessage(BaseModel):
    user_id: str
    message: str
    age: int = 7
    condition: Literal["diabetes", "asthma", "both", "none"] = "diabetes"
    current_mood: Optional[str] = None
    is_kid_mode: bool = True  # True for kid-friendly, False for parent professional mode
    child_id: Optional[str] = None  # ID of the child being discussed
    child_name: Optional[str] = None  # Name of the child


class ChildProfile(BaseModel):
    """Profile for a child being monitored"""
    id: str
    name: str
    age: int
    condition: Literal["diabetes", "asthma", "both", "none"]
    parent_name: str
    avatar: Optional[str] = "lion"
    # Baseline health values (age/condition appropriate)
    baseline_glucose: float = 5.5  # mmol/L
    baseline_heart_rate: int = 90  # bpm
    baseline_spo2: float = 98.0  # %
    # Gamification stats
    xp: int = 0
    level: int = 1
    streak: int = 0
    created_at: Optional[str] = None
    
    class Config:
        extra = "ignore"


class ChildProfileCreate(BaseModel):
    """Request model for creating a child profile"""
    name: str
    age: int
    condition: Literal["diabetes", "asthma", "both", "none"] = "none"
    parent_name: str
    avatar: Optional[str] = "lion"
    baseline_glucose: Optional[float] = None
    baseline_heart_rate: Optional[int] = None


class ChildProfileUpdate(BaseModel):
    """Request model for updating a child profile"""
    name: Optional[str] = None
    age: Optional[int] = None
    condition: Optional[Literal["diabetes", "asthma", "both", "none"]] = None
    parent_name: Optional[str] = None
    avatar: Optional[str] = None
    baseline_glucose: Optional[float] = None
    baseline_heart_rate: Optional[int] = None


class ScenarioRequest(BaseModel):
    """Request to run a specific simulation scenario"""
    scenario: str  # e.g., "hypoglycemia_episode", "healthy_school_day"
    duration_minutes: int = 5
    event_interval_seconds: int = 10  # Time between events


class ScenarioInfo(BaseModel):
    """Information about an available scenario"""
    id: str
    name: str
    description: str
    category: Literal["episode", "full_day"]
    duration_minutes: int
    conditions: List[str]  # Which conditions this applies to

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
    # Optional enrichments (sent by sensor stream / simulator)
    child_id: Optional[str] = None
    llm_reasoning: Optional[str] = None
    trend: Optional[str] = None
    anomaly_score: Optional[float] = None
    correlation_tags: Optional[List[str]] = None
    statistics: Optional[Dict[str, Any]] = None
    # We add a catch-all for extra fields so it doesn't crash
    class Config:
        extra = "ignore"