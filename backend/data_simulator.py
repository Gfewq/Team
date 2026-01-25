"""
Play-Protect Data Simulator 🏥🤖
Team Member 2: The Data Simulator (The "Body")

Advanced pediatric medical IoT simulator with:
- Multi-device simulation (CGM, HR monitor, SpO2, accelerometer, environmental sensors)
- Time-of-day patterns (circadian rhythms, meal effects, activity cycles)
- Real-time trend analysis & anomaly detection
- LLM-powered safety analysis (DeepSeek V3.2)
- Event correlation & pattern recognition
- Real-time statistics & health scoring
- Per-child profiles with history storage
- Predefined scenario-based simulation
"""

import json
import time
import random
import asyncio
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Generator
from enum import Enum
from collections import deque
import aiohttp
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field


class EventType(Enum):
    """Types of health events that can be simulated"""
    GLUCOSE_DROP = "glucose_drop"
    GLUCOSE_SPIKE = "glucose_spike"
    GLUCOSE_NORMAL = "glucose_normal"
    HEART_RATE_ELEVATED = "heart_rate_elevated"
    HEART_RATE_LOW = "heart_rate_low"
    MOOD_INDICATOR = "mood_indicator"
    ACTIVITY_LEVEL = "activity_level"
    TEMPERATURE_ANOMALY = "temperature_anomaly"
    ASTHMA_RISK = "asthma_risk"
    MEDICATION_DUE = "medication_due"
    OXYGEN_SATURATION = "oxygen_saturation"
    RESPIRATORY_RATE = "respiratory_rate"
    BLOOD_PRESSURE = "blood_pressure"
    HYDRATION_LEVEL = "hydration_level"
    STRESS_INDICATOR = "stress_indicator"
    SLEEP_QUALITY = "sleep_quality"
    ENVIRONMENTAL_TRIGGER = "environmental_trigger"


class UrgencyLevel(Enum):
    """Urgency levels for health events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyStatus(Enum):
    """Safety classification from LLM analysis"""
    SAFE = "SAFE"
    DANGER = "DANGER"
    MONITOR = "MONITOR"


@dataclass
class HealthEvent:
    """Structure for a health event with advanced analytics"""
    timestamp: str
    event_type: str
    value: float
    unit: str
    urgency: str
    metadata: Dict[str, Any]
    safety_status: Optional[str] = None
    llm_reasoning: Optional[str] = None
    trend: Optional[str] = None  # "rising", "falling", "stable", "volatile"
    anomaly_score: Optional[float] = None  # 0-1, how anomalous this reading is
    correlation_tags: List[str] = field(default_factory=list)  # Related events
    health_score: Optional[float] = None  # Overall health score 0-100


class MedicalDataSimulator:
    """Advanced medical IoT simulator with pattern recognition & analytics"""
    
    def __init__(
        self, 
        child_id: Optional[str] = None,
        child_profile: Optional[Dict[str, Any]] = None,
        deepseek_api_key: Optional[str] = None, 
        api_base: str = "https://api.deepseek.com"
    ):
        """
        Initialize the advanced data simulator
        
        Args:
            child_id: ID of the child to simulate (loads profile from storage)
            child_profile: Direct child profile dict (alternative to child_id)
            deepseek_api_key: API key for DeepSeek V3.2 (optional, will use env var if not provided)
            api_base: Base URL for DeepSeek API
        """
        self.api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
        self.api_base = api_base
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Load child profile if provided
        self.child_id = child_id
        self.child_profile = child_profile
        
        if child_id and not child_profile:
            self.child_profile = self._load_child_profile(child_id)
        
        # Set baselines from child profile or use defaults
        if self.child_profile:
            self.child_id = self.child_profile.get("id", child_id)
            self.baseline_glucose = self.child_profile.get("baseline_glucose", 5.5)
            self.baseline_heart_rate = self.child_profile.get("baseline_heart_rate", 90)
            self.baseline_spo2 = self.child_profile.get("baseline_spo2", 98.0)
            self.child_age = self.child_profile.get("age", 7)
            self.child_condition = self.child_profile.get("condition", "diabetes")
        else:
            # Default: 7-year-old with Type 1 Diabetes
            self.baseline_glucose = 5.5  # mmol/L (normal range: 4-7)
            self.baseline_heart_rate = 90  # bpm (normal: 70-110 for age 7)
            self.baseline_spo2 = 98.0  # Oxygen saturation %
            self.child_age = 7
            self.child_condition = "diabetes"
        
        self.baseline_temperature = 36.8  # Celsius
        self.baseline_respiratory_rate = 22  # breaths/min
        self.baseline_systolic_bp = 95  # mmHg
        self.baseline_diastolic_bp = 60  # mmHg
        
        # State tracking for realistic simulations
        self.current_glucose = self.baseline_glucose
        self.current_heart_rate = self.baseline_heart_rate
        self.current_mood = 0.7  # 0-1 scale
        self.current_activity = 0.5  # 0-1 scale
        self.current_temperature = self.baseline_temperature
        self.current_spo2 = self.baseline_spo2
        self.current_respiratory_rate = self.baseline_respiratory_rate
        self.current_hydration = 0.75  # 0-1 scale
        self.current_stress = 0.3  # 0-1 scale
        self.asthma_risk_level = 0.2  # 0-1 scale
        
        # Time-based state
        self.last_medication_time = time.time() - 3600  # 1 hour ago
        self.last_meal_time = time.time() - 7200  # 2 hours ago
        self.sleep_state = "awake"  # "awake", "light_sleep", "deep_sleep"
        self.start_time = time.time()
        
        # Historical data for trend analysis (rolling windows)
        self.glucose_history = deque(maxlen=20)
        self.heart_rate_history = deque(maxlen=20)
        self.event_history = deque(maxlen=50)
        
        # Statistics
        self.stats = {
            "total_events": 0,
            "danger_events": 0,
            "monitor_events": 0,
            "safe_events": 0,
            "anomalies_detected": 0,
            "last_anomaly_time": None
        }
        
        # Environmental factors
        self.environment = {
            "air_quality": 0.8,  # 0-1 (1 = excellent)
            "pollen_count": 0.3,  # 0-1 (1 = very high)
            "humidity": 0.5,  # 0-1
            "temperature": 22.0  # Celsius
        }
        
        # Data directory for per-child history
        self.data_dir = Path(__file__).parent.parent / "data"
        self.history_dir = self.data_dir / "history"
    
    def _load_child_profile(self, child_id: str) -> Optional[Dict[str, Any]]:
        """Load a child profile from storage"""
        try:
            from backend.child_profiles import get_child
            child = get_child(child_id)
            if child:
                return child.model_dump()
        except Exception as e:
            print(f"Error loading child profile {child_id}: {e}")
        return None
    
    def _get_history_file(self) -> Path:
        """Get the path to this child's history file"""
        self.history_dir.mkdir(parents=True, exist_ok=True)
        if self.child_id:
            return self.history_dir / f"{self.child_id}.jsonl"
        return self.data_dir.parent / "events.jsonl"
    
    def _append_to_history(self, event: Dict[str, Any]):
        """Append an event to the child's history file"""
        history_file = self._get_history_file()
        
        # Add child_id to event
        if self.child_id:
            event["child_id"] = self.child_id
        
        with open(history_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def get_profile_dict(self) -> Dict[str, Any]:
        """Get the child profile as a dictionary for scenario functions"""
        return {
            "id": self.child_id,
            "age": self.child_age,
            "condition": self.child_condition,
            "baseline_glucose": self.baseline_glucose,
            "baseline_heart_rate": self.baseline_heart_rate,
            "baseline_spo2": self.baseline_spo2
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_time_of_day_factor(self) -> float:
        """Returns time-of-day factor affecting glucose (0-1)"""
        hour = datetime.now().hour
        # Meals typically at 8am, 12pm, 6pm - glucose spikes 30-60 min after
        if 8 <= hour <= 9:  # Breakfast effect
            return 1.3
        elif 12 <= hour <= 13:  # Lunch effect
            return 1.4
        elif 18 <= hour <= 19:  # Dinner effect
            return 1.3
        elif 2 <= hour <= 6:  # Dawn phenomenon
            return 1.2
        else:
            return 1.0
    
    def _calculate_trend(self, history: deque, current: float) -> str:
        """Calculate trend from historical data"""
        if len(history) < 3:
            return "stable"
        
        recent = list(history)[-5:]
        if len(recent) < 3:
            return "stable"
        
        # Calculate slope
        changes = [recent[i] - recent[i-1] for i in range(1, len(recent))]
        avg_change = sum(changes) / len(changes)
        
        if abs(avg_change) < 0.1:
            return "stable"
        elif avg_change > 0.3:
            return "rising"
        elif avg_change < -0.3:
            return "falling"
        else:
            return "volatile" if abs(avg_change) > 0.2 else "stable"
    
    def _calculate_anomaly_score(self, value: float, baseline: float, normal_range: Tuple[float, float]) -> float:
        """Calculate anomaly score (0-1) based on deviation from normal"""
        lower, upper = normal_range
        if lower <= value <= upper:
            # Within normal range, score based on distance from baseline
            distance = abs(value - baseline) / (upper - lower)
            return min(distance * 0.5, 0.5)  # Max 0.5 for normal range
        elif value < lower:
            # Below normal
            deviation = (lower - value) / (baseline - lower)
            return min(0.5 + deviation * 0.5, 1.0)
        else:
            # Above normal
            deviation = (value - upper) / (upper - baseline)
            return min(0.5 + deviation * 0.5, 1.0)
    
    def _calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0
        
        # Glucose impact (40% weight)
        if 4.0 <= self.current_glucose <= 7.0:
            glucose_score = 100
        elif 3.5 <= self.current_glucose < 4.0 or 7.0 < self.current_glucose <= 9.0:
            glucose_score = 70
        elif 3.0 <= self.current_glucose < 3.5 or 9.0 < self.current_glucose <= 11.0:
            glucose_score = 40
        else:
            glucose_score = 10
        score = score * 0.4 + glucose_score * 0.4
        
        # Heart rate impact (20% weight)
        if 70 <= self.current_heart_rate <= 110:
            hr_score = 100
        elif 60 <= self.current_heart_rate < 70 or 110 < self.current_heart_rate <= 120:
            hr_score = 80
        else:
            hr_score = 50
        score = score * 0.6 + hr_score * 0.2
        
        # Mood impact (20% weight)
        mood_score = self.current_mood * 100
        score = score * 0.8 + mood_score * 0.2
        
        # Activity impact (10% weight)
        activity_score = min(self.current_activity * 100, 100)
        score = score * 0.9 + activity_score * 0.1
        
        # Stress penalty (10% weight)
        stress_penalty = self.current_stress * 20
        score = max(0, score - stress_penalty)
        
        return round(score, 1)
    
    def generate_glucose_event(self) -> HealthEvent:
        """Generate a glucose-related event with time-of-day patterns"""
        # Time-of-day effects
        time_factor = self._get_time_of_day_factor()
        base_change = random.uniform(-1.5, 1.5)
        
        # Activity affects glucose (exercise lowers it)
        activity_effect = -self.current_activity * 0.5
        
        # Medication effect (insulin lowers glucose)
        time_since_med = (time.time() - self.last_medication_time) / 3600
        medication_effect = -0.3 if time_since_med < 2 else 0
        
        # Meal effect (glucose rises after meals)
        time_since_meal = (time.time() - self.last_meal_time) / 3600
        meal_effect = 1.5 * math.exp(-time_since_meal / 2) if time_since_meal < 4 else 0
        
        change = (base_change + activity_effect + medication_effect + meal_effect) * time_factor
        self.current_glucose += change
        
        # Clamp to realistic range
        self.current_glucose = max(2.5, min(18.0, self.current_glucose))
        
        # Update history
        self.glucose_history.append(self.current_glucose)
        trend = self._calculate_trend(self.glucose_history, self.current_glucose)
        anomaly_score = self._calculate_anomaly_score(self.current_glucose, 5.5, (4.0, 7.0))
        
        # Determine event type and urgency
        if self.current_glucose < 3.5:
            event_type = EventType.GLUCOSE_DROP
            urgency = UrgencyLevel.CRITICAL
        elif self.current_glucose < 4.0:
            event_type = EventType.GLUCOSE_DROP
            urgency = UrgencyLevel.HIGH
        elif self.current_glucose > 14.0:
            event_type = EventType.GLUCOSE_SPIKE
            urgency = UrgencyLevel.CRITICAL
        elif self.current_glucose > 11.0:
            event_type = EventType.GLUCOSE_SPIKE
            urgency = UrgencyLevel.HIGH
        elif self.current_glucose > 9.0:
            event_type = EventType.GLUCOSE_SPIKE
            urgency = UrgencyLevel.MEDIUM
        else:
            event_type = EventType.GLUCOSE_NORMAL
            urgency = UrgencyLevel.LOW
        
        # Correlation tags
        correlations = []
        if self.current_heart_rate > 110:
            correlations.append("elevated_heart_rate")
        if self.current_mood < 0.4:
            correlations.append("low_mood")
        if self.current_activity > 0.7:
            correlations.append("high_activity")
        
        health_score = self._calculate_health_score()
        
        return HealthEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type.value,
            value=round(self.current_glucose, 2),
            unit="mmol/L",
            urgency=urgency.value,
            metadata={
                "device": "continuous_glucose_monitor_v2",
                "device_id": "CGM-7YO-001",
                "trend": trend,
                "age_group": "pediatric_7_years",
                "time_of_day": datetime.now().strftime("%H:%M"),
                "meal_effect": round(meal_effect, 2),
                "activity_effect": round(activity_effect, 2),
                "medication_effect": round(medication_effect, 2)
            },
            trend=trend,
            anomaly_score=round(anomaly_score, 3),
            correlation_tags=correlations,
            health_score=health_score
        )
    
    def generate_heart_rate_event(self) -> HealthEvent:
        """Generate a heart rate event"""
        # Simulate heart rate changes
        change = random.uniform(-15, 20)
        self.current_heart_rate += change
        self.current_heart_rate = max(60, min(140, self.current_heart_rate))
        
        if self.current_heart_rate > 120:
            event_type = EventType.HEART_RATE_ELEVATED
            urgency = UrgencyLevel.MEDIUM
        elif self.current_heart_rate < 70:
            event_type = EventType.HEART_RATE_LOW
            urgency = UrgencyLevel.MEDIUM
        else:
            event_type = EventType.HEART_RATE_ELEVATED  # Still track normal
            urgency = UrgencyLevel.LOW
        
        return HealthEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type.value,
            value=round(self.current_heart_rate, 0),
            unit="bpm",
            urgency=urgency.value,
            metadata={
                "device": "wearable_heart_rate_monitor",
                "age_group": "pediatric_7_years"
            }
        )
    
    def generate_mood_event(self) -> HealthEvent:
        """Generate a mood indicator event with multi-factor analysis"""
        # Glucose strongly affects mood
        glucose_effect = 0
        if self.current_glucose < 3.5:
            glucose_effect = -0.5
        elif self.current_glucose < 4.0:
            glucose_effect = -0.3
        elif self.current_glucose > 11.0:
            glucose_effect = -0.2
        
        # Activity affects mood positively
        activity_effect = self.current_activity * 0.2
        
        # Stress affects mood negatively
        stress_effect = -self.current_stress * 0.3
        
        # Sleep affects mood
        sleep_effect = 0.2 if self.sleep_state == "deep_sleep" else -0.1 if self.sleep_state == "light_sleep" else 0
        
        mood_change = random.uniform(-0.15, 0.15) + glucose_effect + activity_effect + stress_effect + sleep_effect
        self.current_mood += mood_change
        self.current_mood = max(0.0, min(1.0, self.current_mood))
        
        urgency = UrgencyLevel.LOW
        if self.current_mood < 0.2:
            urgency = UrgencyLevel.HIGH
        elif self.current_mood < 0.3:
            urgency = UrgencyLevel.MEDIUM
        
        correlations = []
        if self.current_glucose < 4.0:
            correlations.append("hypoglycemia_symptom")
        if self.current_stress > 0.7:
            correlations.append("high_stress")
        
        return HealthEvent(
            timestamp=datetime.now().isoformat(),
            event_type=EventType.MOOD_INDICATOR.value,
            value=round(self.current_mood, 2),
            unit="normalized_score",
            urgency=urgency.value,
            metadata={
                "device": "behavioral_ai_analyzer",
                "device_id": "MOOD-7YO-001",
                "context": "play_activity" if self.current_mood > 0.6 else "fatigue_observed" if self.current_mood < 0.4 else "normal_activity",
                "facial_expression_score": round(self.current_mood, 2),
                "voice_tone_score": round(self.current_mood + random.uniform(-0.1, 0.1), 2),
                "interaction_quality": "high" if self.current_mood > 0.7 else "medium" if self.current_mood > 0.4 else "low"
            },
            trend="stable",
            anomaly_score=round(1.0 - self.current_mood, 3) if self.current_mood < 0.4 else 0.2,
            correlation_tags=correlations,
            health_score=self._calculate_health_score()
        )
    
    def generate_medication_event(self) -> HealthEvent:
        """Generate medication due reminder with glucose-based urgency"""
        time_since_medication = time.time() - self.last_medication_time
        hours_since = time_since_medication / 3600
        
        # Base urgency on time
        if hours_since > 5:
            base_urgency = UrgencyLevel.HIGH
        elif hours_since > 4:
            base_urgency = UrgencyLevel.MEDIUM
        else:
            base_urgency = UrgencyLevel.LOW
        
        # Escalate if glucose is high (needs insulin)
        if self.current_glucose > 11.0:
            urgency = UrgencyLevel.CRITICAL if base_urgency == UrgencyLevel.HIGH else UrgencyLevel.HIGH
        elif self.current_glucose > 9.0:
            urgency = UrgencyLevel.HIGH if base_urgency == UrgencyLevel.MEDIUM else base_urgency
        else:
            urgency = base_urgency
        
        correlations = []
        if self.current_glucose > 9.0:
            correlations.append("hyperglycemia_present")
        
        return HealthEvent(
            timestamp=datetime.now().isoformat(),
            event_type=EventType.MEDICATION_DUE.value,
            value=round(hours_since, 2),
            unit="hours_since_last_dose",
            urgency=urgency.value,
            metadata={
                "device": "smart_medication_tracker",
                "device_id": "MED-7YO-001",
                "medication_type": "insulin",
                "dosage": "5 units",
                "scheduled_time": True,
                "glucose_at_reminder": round(self.current_glucose, 2),
                "recommended_action": "administer_insulin" if self.current_glucose > 9.0 else "scheduled_dose"
            },
            trend="stable",
            anomaly_score=0.3 if hours_since > 5 else 0.1,
            correlation_tags=correlations,
            health_score=self._calculate_health_score()
        )
    
    def generate_asthma_risk_event(self) -> HealthEvent:
        """Generate asthma risk assessment based on environmental factors"""
        # Environmental triggers
        pollen_effect = self.environment["pollen_count"] * 0.4
        air_quality_effect = (1.0 - self.environment["air_quality"]) * 0.3
        activity_effect = self.current_activity * 0.2  # Exercise can trigger
        
        risk_change = random.uniform(-0.1, 0.1) + pollen_effect + air_quality_effect + activity_effect
        self.asthma_risk_level += risk_change
        self.asthma_risk_level = max(0.0, min(1.0, self.asthma_risk_level))
        
        # Respiratory rate correlates with asthma risk
        if self.asthma_risk_level > 0.6:
            self.current_respiratory_rate += random.uniform(2, 5)
        elif self.asthma_risk_level < 0.3:
            self.current_respiratory_rate += random.uniform(-2, 1)
        
        self.current_respiratory_rate = max(18, min(35, self.current_respiratory_rate))
        
        if self.asthma_risk_level > 0.7:
            urgency = UrgencyLevel.HIGH
        elif self.asthma_risk_level > 0.5:
            urgency = UrgencyLevel.MEDIUM
        else:
            urgency = UrgencyLevel.LOW
        
        correlations = []
        if self.environment["pollen_count"] > 0.6:
            correlations.append("high_pollen")
        if self.environment["air_quality"] < 0.5:
            correlations.append("poor_air_quality")
        if self.current_respiratory_rate > 28:
            correlations.append("elevated_respiratory_rate")
        
        return HealthEvent(
            timestamp=datetime.now().isoformat(),
            event_type=EventType.ASTHMA_RISK.value,
            value=round(self.asthma_risk_level, 2),
            unit="risk_score",
            urgency=urgency.value,
            metadata={
                "device": "environmental_sensor_array",
                "device_id": "ENV-7YO-001",
                "pollen_count": round(self.environment["pollen_count"], 2),
                "air_quality_index": round(self.environment["air_quality"] * 100, 1),
                "respiratory_rate": round(self.current_respiratory_rate, 0),
                "humidity": round(self.environment["humidity"], 2),
                "location": "indoor"
            },
            trend="rising" if risk_change > 0.1 else "falling" if risk_change < -0.1 else "stable",
            anomaly_score=round(self.asthma_risk_level, 3),
            correlation_tags=correlations,
            health_score=self._calculate_health_score()
        )
    
    def generate_oxygen_saturation_event(self) -> HealthEvent:
        """Generate SpO2 reading"""
        # SpO2 affected by respiratory rate and activity
        activity_effect = -self.current_activity * 0.5
        respiratory_effect = -(self.current_respiratory_rate - 22) * 0.1
        
        change = random.uniform(-1.0, 1.0) + activity_effect + respiratory_effect
        self.current_spo2 += change
        self.current_spo2 = max(92.0, min(100.0, self.current_spo2))
        
        if self.current_spo2 < 95:
            urgency = UrgencyLevel.HIGH
        elif self.current_spo2 < 97:
            urgency = UrgencyLevel.MEDIUM
        else:
            urgency = UrgencyLevel.LOW
        
        correlations = []
        if self.current_respiratory_rate > 28:
            correlations.append("elevated_respiratory_rate")
        if self.asthma_risk_level > 0.6:
            correlations.append("asthma_risk")
        
        return HealthEvent(
            timestamp=datetime.now().isoformat(),
            event_type=EventType.OXYGEN_SATURATION.value,
            value=round(self.current_spo2, 1),
            unit="%",
            urgency=urgency.value,
            metadata={
                "device": "pulse_oximeter",
                "device_id": "SPO2-7YO-001",
                "perfusion_index": round(random.uniform(0.5, 5.0), 2)
            },
            trend="stable",
            anomaly_score=round((97 - self.current_spo2) / 5.0, 3) if self.current_spo2 < 97 else 0.1,
            correlation_tags=correlations,
            health_score=self._calculate_health_score()
        )
    
    def generate_activity_event(self) -> HealthEvent:
        """Generate activity level event"""
        # Activity fluctuates throughout the day
        hour = datetime.now().hour
        if 7 <= hour <= 8 or 15 <= hour <= 17:  # Morning and afternoon play times
            activity_base = 0.7
        elif 12 <= hour <= 13:  # Lunch break
            activity_base = 0.4
        elif 20 <= hour <= 22:  # Evening wind-down
            activity_base = 0.3
        elif 22 <= hour or hour <= 6:  # Sleep time
            activity_base = 0.1
            self.sleep_state = "deep_sleep" if random.random() > 0.3 else "light_sleep"
        else:
            activity_base = 0.5
        
        change = random.uniform(-0.2, 0.2)
        self.current_activity = activity_base + change
        self.current_activity = max(0.0, min(1.0, self.current_activity))
        
        if self.sleep_state != "awake":
            self.current_activity = 0.1
            self.sleep_state = "awake" if random.random() > 0.7 else self.sleep_state
        
        urgency = UrgencyLevel.LOW
        
        correlations = []
        if self.current_activity > 0.8:
            correlations.append("high_activity")
            # High activity can affect glucose
            if self.current_glucose > 5.0:
                self.current_glucose -= 0.3
        
        return HealthEvent(
            timestamp=datetime.now().isoformat(),
            event_type=EventType.ACTIVITY_LEVEL.value,
            value=round(self.current_activity, 2),
            unit="normalized_score",
            urgency=urgency.value,
            metadata={
                "device": "accelerometer_gyroscope",
                "device_id": "ACT-7YO-001",
                "steps_per_minute": round(self.current_activity * 120, 0),
                "movement_type": "running" if self.current_activity > 0.7 else "walking" if self.current_activity > 0.4 else "sedentary",
                "sleep_state": self.sleep_state
            },
            trend="stable",
            anomaly_score=0.1,
            correlation_tags=correlations,
            health_score=self._calculate_health_score()
        )
    
    def generate_random_event(self) -> HealthEvent:
        """Generate a random health event with weighted probabilities"""
        event_generators = [
            self.generate_glucose_event,
            self.generate_heart_rate_event,
            self.generate_mood_event,
            self.generate_medication_event,
            self.generate_asthma_risk_event,
            self.generate_oxygen_saturation_event,
            self.generate_activity_event,
        ]
        
        # Weight events: glucose most critical, then HR, mood, etc.
        weights = [0.35, 0.20, 0.15, 0.10, 0.08, 0.07, 0.05]
        generator = random.choices(event_generators, weights=weights)[0]
        event = generator()
        
        # Update statistics
        self.stats["total_events"] += 1
        if event.safety_status == "DANGER":
            self.stats["danger_events"] += 1
        elif event.safety_status == "MONITOR":
            self.stats["monitor_events"] += 1
        else:
            self.stats["safe_events"] += 1
        
        if event.anomaly_score and event.anomaly_score > 0.7:
            self.stats["anomalies_detected"] += 1
            self.stats["last_anomaly_time"] = event.timestamp
        
        # Add to history
        self.event_history.append(event)
        
        return event
    
    def _update_environment(self):
        """Update environmental factors (pollen, air quality, etc.)"""
        # Simulate daily variations
        hour = datetime.now().hour
        # Pollen higher during day
        self.environment["pollen_count"] = max(0.0, min(1.0, 
            0.3 + 0.4 * math.sin((hour - 6) * math.pi / 12) + random.uniform(-0.1, 0.1)))
        # Air quality varies
        self.environment["air_quality"] = max(0.0, min(1.0,
            0.7 + random.uniform(-0.2, 0.2)))
    
    async def analyze_with_llm(self, event: HealthEvent) -> tuple[SafetyStatus, str]:
        """
        Analyze health event using DeepSeek V3.2 to determine safety status
        
        Args:
            event: Health event to analyze
            
        Returns:
            Tuple of (SafetyStatus, reasoning)
        """
        if not self.api_key:
            # Fallback to rule-based analysis if no API key
            return self._rule_based_analysis(event)
        
        # Build context from recent events
        recent_events = list(self.event_history)[-5:] if len(self.event_history) > 0 else []
        recent_context = []
        for e in recent_events:
            recent_context.append(f"{e.event_type}: {e.value} {e.unit} ({e.safety_status})")
        
        prompt = f"""You are an advanced pediatric medical safety analyzer for a 7-year-old child with Type 1 Diabetes.

Analyze this health event and classify it as SAFE, DANGER, or MONITOR.

Event Details:
- Type: {event.event_type}
- Value: {event.value} {event.unit}
- Urgency: {event.urgency}
- Trend: {event.trend}
- Anomaly Score: {event.anomaly_score}
- Health Score: {event.health_score}
- Correlations: {', '.join(event.correlation_tags) if event.correlation_tags else 'none'}
- Timestamp: {event.timestamp}
- Metadata: {json.dumps(event.metadata, indent=2)}

Recent Event History:
{chr(10).join(recent_context) if recent_context else 'No recent events'}

Current Patient State:
- Glucose: {round(self.current_glucose, 2)} mmol/L
- Heart Rate: {round(self.current_heart_rate, 0)} bpm
- Mood: {round(self.current_mood, 2)}
- Activity: {round(self.current_activity, 2)}
- Stress: {round(self.current_stress, 2)}

Context:
- Patient: 7-year-old child with Type 1 Diabetes
- Normal glucose range: 4.0-7.0 mmol/L
- Critical thresholds: <3.5 mmol/L (hypoglycemia) or >11.0 mmol/L (hyperglycemia)
- Normal heart rate: 70-110 bpm for this age
- Consider correlations and trends when assessing risk

Respond ONLY with a JSON object in this exact format:
{{
    "status": "SAFE" | "DANGER" | "MONITOR",
    "reasoning": "Brief explanation considering trends, correlations, and context"
}}"""

        try:
            async with self.session.post(
                f"{self.api_base}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a pediatric medical safety analyzer. Always respond with valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    # Parse JSON response
                    try:
                        analysis = json.loads(content)
                        status = SafetyStatus[analysis["status"]]
                        reasoning = analysis.get("reasoning", "No reasoning provided")
                        return status, reasoning
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        # Fallback if JSON parsing fails
                        return self._rule_based_analysis(event)
                else:
                    # API error, fallback to rule-based
                    return self._rule_based_analysis(event)
        except Exception as e:
            print(f"LLM analysis error: {e}, using rule-based fallback")
            return self._rule_based_analysis(event)
    
    def _rule_based_analysis(self, event: HealthEvent) -> tuple[SafetyStatus, str]:
        """Fallback rule-based safety analysis"""
        if event.event_type == EventType.GLUCOSE_DROP.value:
            if event.value < 3.5:
                return SafetyStatus.DANGER, "Critical hypoglycemia detected - immediate intervention required"
            elif event.value < 4.0:
                return SafetyStatus.DANGER, "Low blood glucose - intervention needed"
            else:
                return SafetyStatus.MONITOR, "Glucose trending low - monitor closely"
        
        elif event.event_type == EventType.GLUCOSE_SPIKE.value:
            if event.value > 14.0:
                return SafetyStatus.DANGER, "Severe hyperglycemia - medical attention needed"
            elif event.value > 11.0:
                return SafetyStatus.MONITOR, "Elevated blood glucose - monitor and consider insulin"
            else:
                return SafetyStatus.SAFE, "Slightly elevated glucose - within acceptable range"
        
        elif event.event_type == EventType.HEART_RATE_ELEVATED.value:
            if event.value > 130:
                return SafetyStatus.MONITOR, "Elevated heart rate - may indicate stress or medical event"
            else:
                return SafetyStatus.SAFE, "Heart rate within normal range"
        
        elif event.event_type == EventType.MOOD_INDICATOR.value:
            if event.value < 0.3:
                return SafetyStatus.MONITOR, "Low mood detected - may indicate hypoglycemia or fatigue"
            else:
                return SafetyStatus.SAFE, "Mood indicators normal"
        
        elif event.urgency == UrgencyLevel.CRITICAL.value:
            return SafetyStatus.DANGER, "Critical event detected - immediate attention required"
        elif event.urgency == UrgencyLevel.HIGH.value:
            return SafetyStatus.MONITOR, "High urgency event - monitor closely"
        else:
            return SafetyStatus.SAFE, "Event within normal parameters"
    
    async def generate_and_analyze_event(self, save_to_history: bool = True) -> Dict[str, Any]:
        """
        Generate a health event, analyze it with LLM, and return formatted JSON
        
        Args:
            save_to_history: Whether to save the event to child's history file
        
        Returns:
            Dictionary ready to be serialized to JSON
        """
        # Update environment factors
        self._update_environment()
        
        # Generate event
        event = self.generate_random_event()
        
        # Analyze with LLM
        safety_status, reasoning = await self.analyze_with_llm(event)
        
        # Update event with analysis
        event.safety_status = safety_status.value
        event.llm_reasoning = reasoning
        
        # Update stats
        if safety_status == SafetyStatus.DANGER:
            self.stats["danger_events"] += 1
        elif safety_status == SafetyStatus.MONITOR:
            self.stats["monitor_events"] += 1
        else:
            self.stats["safe_events"] += 1
        
        # Convert to dictionary
        event_dict = asdict(event)
        
        # Add statistics summary
        event_dict["statistics"] = {
            "total_events": self.stats["total_events"],
            "danger_count": self.stats["danger_events"],
            "monitor_count": self.stats["monitor_events"],
            "safe_count": self.stats["safe_events"],
            "anomalies_detected": self.stats["anomalies_detected"],
            "uptime_seconds": round(time.time() - self.start_time, 0)
        }
        
        # Save to history if enabled
        if save_to_history and self.child_id:
            self._append_to_history(event_dict)
        
        return event_dict
    
    async def run_scenario(
        self, 
        scenario_id: str, 
        num_events: int = None,
        event_interval_seconds: int = 2,
        save_to_history: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run a predefined scenario and return all generated events.
        
        Args:
            scenario_id: ID of the scenario to run (e.g., "hypoglycemia_episode")
            num_events: Optional override for number of events
            event_interval_seconds: Delay between events (for real-time feel)
            save_to_history: Whether to save events to the child's history file
        
        Returns:
            List of all generated events
        """
        from backend.scenarios import run_scenario, get_scenario
        
        # Get scenario info
        scenario = get_scenario(scenario_id)
        
        # Get child profile for scenario
        child_profile = self.get_profile_dict()
        
        # Run scenario and collect events
        events = []
        for event in run_scenario(scenario_id, child_profile, num_events):
            # Add child_id to event
            if self.child_id:
                event["child_id"] = self.child_id
            
            # Update statistics
            self.stats["total_events"] += 1
            status = event.get("safety_status", "SAFE")
            if status == "DANGER":
                self.stats["danger_events"] += 1
            elif status == "MONITOR":
                self.stats["monitor_events"] += 1
            else:
                self.stats["safe_events"] += 1
            
            # Save to history if requested
            if save_to_history:
                self._append_to_history(event)
            
            events.append(event)
            
            # Small delay for real-time feel (if running interactively)
            if event_interval_seconds > 0:
                await asyncio.sleep(event_interval_seconds)
        
        return events
    
    async def run_scenario_stream(
        self, 
        scenario_id: str, 
        num_events: int = None,
        event_interval_seconds: int = 2,
        save_to_history: bool = True
    ):
        """
        Run a scenario and yield events one at a time (for streaming).
        
        Args:
            scenario_id: ID of the scenario to run
            num_events: Optional override for number of events
            event_interval_seconds: Delay between events
            save_to_history: Whether to save events to history
        
        Yields:
            Event dictionaries one at a time
        """
        from backend.scenarios import run_scenario, get_scenario
        
        # Get scenario info
        scenario = get_scenario(scenario_id)
        
        # Get child profile for scenario
        child_profile = self.get_profile_dict()
        
        # Run scenario and yield events
        for event in run_scenario(scenario_id, child_profile, num_events):
            # Add child_id to event
            if self.child_id:
                event["child_id"] = self.child_id
            
            # Update statistics
            self.stats["total_events"] += 1
            status = event.get("safety_status", "SAFE")
            if status == "DANGER":
                self.stats["danger_events"] += 1
            elif status == "MONITOR":
                self.stats["monitor_events"] += 1
            else:
                self.stats["safe_events"] += 1
            
            # Save to history if requested
            if save_to_history:
                self._append_to_history(event)
            
            yield event
            
            # Small delay for real-time feel
            if event_interval_seconds > 0:
                await asyncio.sleep(event_interval_seconds)
    
    def _get_status_color(self, status: str) -> str:
        """Get ANSI color code for status"""
        colors = {
            "DANGER": "\033[91m",  # Red
            "MONITOR": "\033[93m",  # Yellow
            "SAFE": "\033[92m",  # Green
        }
        return colors.get(status, "\033[0m")
    
    def _format_event_display(self, event: Dict[str, Any]) -> str:
        """Format event for console display with colors and detailed information"""
        status = event.get("safety_status", "UNKNOWN")
        color = self._get_status_color(status)
        reset = "\033[0m"
        bold = "\033[1m"
        dim = "\033[2m"
        event_type = event.get('event_type', 'unknown')
        metadata = event.get('metadata', {})
        
        # Status icons
        status_icons = {
            "DANGER": "🔴",
            "MONITOR": "🟡", 
            "SAFE": "🟢"
        }
        status_icon = status_icons.get(status, "⚪")
        
        # Event type emoji mapping
        event_emojis = {
            'glucose_drop': '📉', 'glucose_spike': '📈', 'glucose_normal': '📊',
            'heart_rate_elevated': '❤️', 'heart_rate_low': '💓',
            'mood_indicator': '😊', 'activity_level': '🏃',
            'asthma_risk': '🌬️', 'oxygen_saturation': '🫁',
            'medication_due': '💊', 'respiratory_rate': '🫁'
        }
        event_emoji = event_emojis.get(event_type, '📋')
        
        # Clean header
        timestamp_str = event.get('timestamp', '')
        if timestamp_str:
            timestamp = timestamp_str[:19].replace('T', ' ') if len(timestamp_str) > 19 else timestamp_str.replace('T', ' ')
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        urgency = str(event.get('urgency', 'unknown')).upper()
        value = event.get('value', 0)
        unit = event.get('unit', '')
        
        lines = [
            f"{color}{'═'*80}{reset}",
            f"{color}{bold}{status_icon} {status:^76} {status_icon}{reset}",
            f"{color}{'═'*80}{reset}",
            f"",
            f"{bold}{event_emoji} Event:{reset} {event_type.replace('_', ' ').title()}",
            f"{bold}📊 Value:{reset} {value} {unit}",
            f"{bold}⚡ Urgency:{reset} {urgency}",
            f"{dim}🕐 {timestamp}{reset}",
            f""
        ]
        
        # Health metrics with better visual design
        if event.get('health_score') is not None:
            health_score = event['health_score']
            health_bar_length = 30
            filled = int(health_score / 100 * health_bar_length)
            health_bar = f"{color}█{reset}" * filled + f"{dim}░{reset}" * (health_bar_length - filled)
            health_color = "\033[92m" if health_score > 70 else "\033[93m" if health_score > 40 else "\033[91m"
            health_status = "Excellent" if health_score > 70 else "Good" if health_score > 40 else "Concerning"
            lines.append(f"{bold}💚 Health Score:{reset} {health_color}{health_score:5.1f}/100{reset} {health_status}")
            lines.append(f"   {health_bar}")
        
        # Anomaly score with visual indicator
        if event.get('anomaly_score') is not None:
            anomaly = event['anomaly_score']
            anomaly_bar_length = 20
            filled = int(anomaly * anomaly_bar_length)
            anomaly_bar = f"\033[91m█{reset}" * filled + f"{dim}░{reset}" * (anomaly_bar_length - filled)
            anomaly_color = "\033[91m" if anomaly > 0.7 else "\033[93m" if anomaly > 0.4 else "\033[92m"
            anomaly_status = "High Risk" if anomaly > 0.7 else "Moderate" if anomaly > 0.4 else "Low"
            lines.append(f"{bold}⚠️  Anomaly Score:{reset} {anomaly_color}{anomaly:.3f}{reset} {anomaly_status}")
            lines.append(f"   {anomaly_bar}")
        
        # Trend with arrow
        trend = event.get('trend', 'N/A')
        if trend is None:
            trend = 'N/A'
        
        trend_colors = {
            'rising': '\033[93m',
            'falling': '\033[91m',
            'volatile': '\033[95m',
            'stable': '\033[92m'
        }
        trend_icons = {
            'rising': '📈',
            'falling': '📉',
            'volatile': '📊',
            'stable': '➡️'
        }
        trend_color = trend_colors.get(trend, reset)
        trend_icon = trend_icons.get(trend, '➡️')
        if trend != 'N/A' and trend is not None:
            trend_display = f"{trend_color}{trend_icon} {trend.upper()}{reset}"
        else:
            trend_display = f"{dim}N/A{reset}"
        lines.append(f"{bold}📈 Trend:{reset} {trend_display}")
        lines.append("")
        
        # Event-specific details with better formatting
        if event_type == 'asthma_risk':
            lines.append(f"{bold}🌍 Environmental Factors:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            if 'pollen_count' in metadata and metadata['pollen_count'] is not None:
                pollen = float(metadata['pollen_count'])
                pollen_bar_length = 15
                filled = int(pollen * pollen_bar_length)
                pollen_bar = f"\033[93m█{reset}" * filled + f"{dim}░{reset}" * (pollen_bar_length - filled)
                pollen_status = "⚠️  HIGH" if pollen > 0.6 else "✓ Normal"
                pollen_color = "\033[93m" if pollen > 0.6 else "\033[92m"
                lines.append(f"  🌸 Pollen:     {pollen_color}{pollen:.2f}{reset} {pollen_status}")
                lines.append(f"     {pollen_bar}")
            if 'air_quality_index' in metadata and metadata['air_quality_index'] is not None:
                aqi = float(metadata['air_quality_index'])
                aqi_color = "\033[91m" if aqi < 50 else "\033[93m" if aqi < 70 else "\033[92m"
                aqi_status = "⚠️  POOR" if aqi < 50 else "⚠️  MODERATE" if aqi < 70 else "✓ Good"
                lines.append(f"  🌫️  Air Quality: {aqi_color}{aqi:5.1f}/100{reset} {aqi_status}")
            if 'respiratory_rate' in metadata and metadata['respiratory_rate'] is not None:
                rr = float(metadata['respiratory_rate'])
                rr_status = "⚠️  Elevated" if rr > 28 else "✓ Normal"
                rr_color = "\033[91m" if rr > 28 else "\033[92m"
                lines.append(f"  🫁 Resp. Rate: {rr_color}{rr:5.0f} breaths/min{reset} {rr_status}")
            if 'humidity' in metadata and metadata['humidity'] is not None:
                lines.append(f"  💧 Humidity:   {float(metadata['humidity']):.2f}")
            if 'location' in metadata and metadata['location']:
                location = str(metadata['location'])
                lines.append(f"  📍 Location:   {location.title()}")
        
        elif event_type in ['glucose_drop', 'glucose_spike', 'glucose_normal']:
            lines.append(f"{bold}🍎 Glucose Analysis:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            value = event.get('value', 0)
            # Show normal range context with visual indicator
            if value < 3.5:
                status_text = "🔴 CRITICAL - Below safe range"
                status_color = "\033[91m"
                range_info = "Normal: 4.0-7.0 mmol/L"
            elif value < 4.0:
                status_text = "🟡 LOW - Approaching critical"
                status_color = "\033[93m"
                range_info = "Normal: 4.0-7.0 mmol/L"
            elif value > 11.0:
                status_text = "🔴 HIGH - Above safe range"
                status_color = "\033[91m"
                range_info = "Normal: 4.0-7.0 mmol/L"
            elif value > 9.0:
                status_text = "🟡 ELEVATED - Above normal"
                status_color = "\033[93m"
                range_info = "Normal: 4.0-7.0 mmol/L"
            else:
                status_text = "✓ Within normal range"
                status_color = "\033[92m"
                range_info = "Normal: 4.0-7.0 mmol/L"
            
            lines.append(f"  {status_color}{status_text}{reset}")
            lines.append(f"  {dim}Range: {range_info}{reset}")
            
            # Effects breakdown
            effects_shown = False
            if 'meal_effect' in metadata and abs(metadata['meal_effect']) > 0.1:
                effect = metadata['meal_effect']
                effect_icon = "📈" if effect > 0 else "📉"
                lines.append(f"  {effect_icon} Meal Effect:    {effect:+.2f} mmol/L")
                effects_shown = True
            if 'activity_effect' in metadata and abs(metadata['activity_effect']) > 0.1:
                effect = metadata['activity_effect']
                effect_icon = "📉" if effect < 0 else "📈"
                lines.append(f"  🏃 Activity Effect: {effect:+.2f} mmol/L")
                effects_shown = True
            if 'medication_effect' in metadata and abs(metadata['medication_effect']) > 0.1:
                effect = metadata['medication_effect']
                lines.append(f"  💊 Medication:     {effect:+.2f} mmol/L")
                effects_shown = True
            if 'time_of_day' in metadata:
                lines.append(f"  🕐 Time:           {metadata['time_of_day']}")
                effects_shown = True
            if not effects_shown:
                lines.append(f"  {dim}No significant effects detected{reset}")
        
        elif event_type in ['heart_rate_elevated', 'heart_rate_low']:
            lines.append(f"{bold}❤️  Heart Rate Analysis:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            value = event['value']
            if value > 120:
                status_text = "🟡 ELEVATED - Above normal"
                status_color = "\033[93m"
            elif value < 70:
                status_text = "🟡 LOW - Below normal"
                status_color = "\033[93m"
            else:
                status_text = "✓ Within normal range"
                status_color = "\033[92m"
            lines.append(f"  {status_color}{status_text}{reset}")
            lines.append(f"  {dim}Normal: 70-110 bpm (age 7){reset}")
            
            if 'activity_level' in metadata and metadata['activity_level'] is not None:
                activity = float(metadata['activity_level'])
                activity_bar = "█" * int(activity * 10) + "░" * (10 - int(activity * 10))
                lines.append(f"  🏃 Activity:       {activity:.2f} [{activity_bar}]")
            if 'stress_level' in metadata and metadata['stress_level'] is not None:
                stress = float(metadata['stress_level'])
                stress_bar_length = 15
                filled = int(stress * stress_bar_length)
                stress_bar = f"\033[91m█{reset}" * filled + f"{dim}░{reset}" * (stress_bar_length - filled)
                lines.append(f"  😰 Stress Level:   {stress:.2f}")
                lines.append(f"     {stress_bar}")
            if 'sleep_state' in metadata and metadata['sleep_state']:
                sleep_state_str = str(metadata['sleep_state'])
                sleep_emoji = "😴" if sleep_state_str != 'awake' else "👁️"
                lines.append(f"  {sleep_emoji} Sleep State:    {sleep_state_str.replace('_', ' ').title()}")
        
        elif event_type == 'mood_indicator':
            lines.append(f"{bold}😊 Mood Analysis:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            value = event.get('value', 0)
            mood_emojis = {
                (0.7, 1.0): "😄",
                (0.5, 0.7): "😊",
                (0.3, 0.5): "😐",
                (0.2, 0.3): "😟",
                (0.0, 0.2): "😰"
            }
            mood_emoji = next((emoji for (low, high), emoji in mood_emojis.items() if low <= value < high), "😐")
            mood_status = "Excellent" if value > 0.7 else "Good" if value > 0.5 else "Neutral" if value > 0.3 else "Low" if value > 0.2 else "Very Low"
            mood_color = "\033[92m" if value > 0.7 else "\033[93m" if value > 0.5 else "\033[91m" if value < 0.3 else reset
            
            mood_bar_length = 20
            filled = int(value * mood_bar_length)
            mood_bar = f"{mood_color}█{reset}" * filled + f"{dim}░{reset}" * (mood_bar_length - filled)
            
            lines.append(f"  {mood_emoji} Mood Level:     {mood_color}{value:.2f}{reset} {mood_status}")
            lines.append(f"     {mood_bar}")
            
            if 'context' in metadata and metadata['context']:
                context_str = str(metadata['context'])
                context_emoji = "🎮" if "play" in context_str.lower() else "😴" if "fatigue" in context_str.lower() else "📚"
                lines.append(f"  {context_emoji} Context:        {context_str.replace('_', ' ').title()}")
            if 'facial_expression_score' in metadata and metadata['facial_expression_score'] is not None:
                lines.append(f"  😊 Facial Score:   {float(metadata['facial_expression_score']):.2f}")
            if 'voice_tone_score' in metadata and metadata['voice_tone_score'] is not None:
                lines.append(f"  🗣️  Voice Tone:     {float(metadata['voice_tone_score']):.2f}")
            if 'interaction_quality' in metadata and metadata['interaction_quality']:
                quality_str = str(metadata['interaction_quality'])
                quality_emoji = "⭐" if quality_str == 'high' else "✓" if quality_str == 'medium' else "⚠️"
                lines.append(f"  {quality_emoji} Interaction:    {quality_str.title()}")
        
        elif event_type == 'activity_level':
            lines.append(f"{bold}🏃 Activity Analysis:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            value = event['value']
            activity_emojis = {
                (0.7, 1.0): "🏃",
                (0.4, 0.7): "🚶",
                (0.0, 0.4): "💤"
            }
            activity_emoji = next((emoji for (low, high), emoji in activity_emojis.items() if low <= value < high), "💤")
            activity_status = "High" if value > 0.7 else "Moderate" if value > 0.4 else "Low"
            
            activity_bar_length = 20
            filled = int(value * activity_bar_length)
            activity_bar = f"\033[92m█{reset}" * filled + f"{dim}░{reset}" * (activity_bar_length - filled)
            
            lines.append(f"  {activity_emoji} Activity:       {value:.2f} ({activity_status})")
            lines.append(f"     {activity_bar}")
            
            if 'steps_per_minute' in metadata:
                lines.append(f"  👣 Steps/Min:      {metadata['steps_per_minute']:.0f}")
            if 'movement_type' in metadata and metadata['movement_type']:
                movement_str = str(metadata['movement_type'])
                movement_emoji = "🏃" if movement_str == 'running' else "🚶" if movement_str == 'walking' else "🪑"
                lines.append(f"  {movement_emoji} Movement:       {movement_str.title()}")
            if 'sleep_state' in metadata:
                sleep_emoji = "😴" if metadata['sleep_state'] != 'awake' else "👁️"
                lines.append(f"  {sleep_emoji} Sleep State:    {metadata['sleep_state'].replace('_', ' ').title()}")
        
        elif event_type == 'medication_due':
            lines.append(f"{bold}💊 Medication Reminder:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            if 'medication_type' in metadata and metadata['medication_type']:
                lines.append(f"  💉 Type:           {str(metadata['medication_type']).title()}")
            if 'dosage' in metadata and metadata['dosage']:
                lines.append(f"  📏 Dosage:        {str(metadata['dosage'])}")
            if 'glucose_at_reminder' in metadata and metadata['glucose_at_reminder'] is not None:
                glucose = float(metadata['glucose_at_reminder'])
                glucose_status = "⚠️" if glucose > 9.0 or glucose < 4.0 else "✓"
                lines.append(f"  🍎 Glucose:       {glucose:.2f} mmol/L {glucose_status}")
            if 'recommended_action' in metadata and metadata['recommended_action']:
                action = str(metadata['recommended_action'])
                action_icon = "⚠️" if "administer" in action.lower() else "⏰"
                action_color = "\033[91m" if "administer" in action.lower() else "\033[93m"
                lines.append(f"  {action_icon} Action:         {action_color}{action}{reset}")
        
        elif event_type == 'oxygen_saturation':
            lines.append(f"{bold}🫁 Oxygen Saturation:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            value = event.get('value', 0)
            if value < 95:
                status_text = "🔴 LOW - Below normal"
                status_color = "\033[91m"
            elif value < 97:
                status_text = "🟡 BELOW OPTIMAL"
                status_color = "\033[93m"
            else:
                status_text = "✓ Normal"
                status_color = "\033[92m"
            lines.append(f"  {status_color}{status_text}{reset}")
            lines.append(f"  {dim}Normal: >95% | Optimal: >97%{reset}")
            if 'perfusion_index' in metadata:
                lines.append(f"  💓 Perfusion:     {metadata['perfusion_index']:.2f}")
        
        # Device information
        if ('device' in metadata and metadata['device']) or ('device_id' in metadata and metadata['device_id']):
            lines.append(f"{bold}📱 Device Info:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            if 'device' in metadata and metadata['device']:
                lines.append(f"  🔧 Device:        {str(metadata['device'])}")
            if 'device_id' in metadata and metadata['device_id']:
                lines.append(f"  🆔 Device ID:     {str(metadata['device_id'])}")
        
        # Correlations
        if event.get('correlation_tags'):
            lines.append(f"")
            lines.append(f"{bold}🔗 Correlations:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            for tag in event['correlation_tags']:
                tag_display = tag.replace('_', ' ').title()
                tag_emoji = "⚠️" if "risk" in tag.lower() or "elevated" in tag.lower() or "low" in tag.lower() else "🔗"
                lines.append(f"  {tag_emoji} {tag_display}")
        
        # AI Reasoning
        reasoning = event.get('llm_reasoning')
        if reasoning:
            lines.append(f"")
            lines.append(f"{bold}🤖 AI Analysis:{reset}")
            lines.append(f"{dim}{'─'*78}{reset}")
            # Wrap long reasoning text
            reasoning_str = str(reasoning)
            max_width = 76
            words = reasoning_str.split()
            current_line = "  "
            for word in words:
                if len(current_line + word) > max_width:
                    lines.append(current_line.rstrip())
                    current_line = f"  {word} "
                else:
                    current_line += word + " "
            if current_line.strip():
                lines.append(current_line.rstrip())
        
        lines.append("")
        lines.append(f"{color}{'═'*80}{reset}")
        
        return "\n".join(lines)
    
    async def run_continuous(self, interval_seconds: int = 30, output_file: Optional[str] = None, verbose: bool = True):
        """
        Run continuous data generation with enhanced display
        
        Args:
            interval_seconds: Time between events (default: 30)
            output_file: Optional file path to write JSON events (for pipeline integration)
            verbose: Show detailed console output
        """
        # Beautiful header
        header_color = "\033[95m"
        reset = "\033[0m"
        bold = "\033[1m"
        
        print(f"\n{header_color}{'═'*80}{reset}")
        print(f"{header_color}{bold}{'🏥 Play-Protect Data Simulator 🤖'.center(80)}{reset}")
        print(f"{header_color}{'═'*80}{reset}")
        print(f"\n{bold}⚙️  Configuration:{reset}")
        
        # Show child info if available
        if self.child_profile:
            child_name = self.child_profile.get("name", "Unknown")
            print(f"  👶 Child: {child_name} (Age {self.child_age}, {self.child_condition})")
        else:
            print(f"  👶 Child: Default (Age 7, diabetes)")
        
        print(f"  📊 Event Interval: {interval_seconds} seconds")
        history_file = self._get_history_file()
        print(f"  📁 History File: {history_file}")
        if output_file:
            print(f"  📁 Additional Output: {output_file}")
        print(f"  🤖 LLM Analysis: {'Enabled' if self.api_key else 'Disabled (rule-based)'}")
        print(f"\n{bold}💡 Tip:{reset} Press Ctrl+C to stop\n")
        print(f"{header_color}{'─'*80}{reset}\n")
        
        try:
            while True:
                event = await self.generate_and_analyze_event()
                
                # Output to console with formatting
                if verbose:
                    try:
                        print(f"\n\033[94m[{datetime.now().strftime('%H:%M:%S')}]\033[0m")
                        print(self._format_event_display(event))
                    except Exception as e:
                        # Fallback to simple display if formatting fails
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Error formatting display: {e}")
                        print(f"Event: {event.get('event_type', 'unknown')} - {event.get('value', 'N/A')} {event.get('unit', '')}")
                        print(f"Status: {event.get('safety_status', 'UNKNOWN')}")
                    
                    # Show statistics every 10 events
                    if self.stats["total_events"] % 10 == 0:
                        stats = event.get("statistics", {})
                        total = stats.get('total_events', 0)
                        danger = stats.get('danger_count', 0)
                        monitor = stats.get('monitor_count', 0)
                        safe = stats.get('safe_count', 0)
                        anomalies = stats.get('anomalies_detected', 0)
                        uptime = stats.get('uptime_seconds', 0)
                        
                        stat_color = "\033[96m"
                        reset = "\033[0m"
                        bold = "\033[1m"
                        dim = "\033[2m"
                        
                        print(f"\n{stat_color}{'═'*80}{reset}")
                        print(f"{stat_color}{bold}{'📊 Statistics Summary'.center(80)}{reset}")
                        print(f"{stat_color}{'═'*80}{reset}")
                        
                        # Safety status with bars
                        print(f"\n{bold}Safety Status Distribution:{reset}")
                        danger_pct = danger*100//total if total > 0 else 0
                        monitor_pct = monitor*100//total if total > 0 else 0
                        safe_pct = safe*100//total if total > 0 else 0
                        
                        danger_bar = "█" * (danger_pct // 5) + "░" * (20 - danger_pct // 5)
                        monitor_bar = "█" * (monitor_pct // 5) + "░" * (20 - monitor_pct // 5)
                        safe_bar = "█" * (safe_pct // 5) + "░" * (20 - safe_pct // 5)
                        
                        print(f"  🔴 DANGER:  {danger:3d} ({danger_pct:3d}%) {dim}[{danger_bar}]{reset}")
                        print(f"  🟡 MONITOR: {monitor:3d} ({monitor_pct:3d}%) {dim}[{monitor_bar}]{reset}")
                        print(f"  🟢 SAFE:    {safe:3d} ({safe_pct:3d}%) {dim}[{safe_bar}]{reset}")
                        
                        print(f"\n{bold}⚠️  Anomalies:{reset} {anomalies} detected ({anomalies*100//total if total > 0 else 0}%)")
                        print(f"{bold}⏱️  Runtime:{reset} {uptime//60}m {uptime%60}s | Avg: {uptime/total:.1f}s/event" if total > 0 else f"{bold}⏱️  Runtime:{reset} {uptime//60}m {uptime%60}s")
                        
                        # Current health state with visual indicators
                        print(f"\n{bold}💚 Current Health State:{reset}")
                        print(f"{dim}{'─'*78}{reset}")
                        
                        # Glucose with bar
                        glucose_status = "⚠️" if self.current_glucose < 4.0 or self.current_glucose > 9.0 else "✓"
                        glucose_color = "\033[91m" if self.current_glucose < 4.0 or self.current_glucose > 9.0 else "\033[92m"
                        glucose_bar_pos = int((self.current_glucose - 2.5) / 12.5 * 20)
                        glucose_bar_pos = max(0, min(20, glucose_bar_pos))
                        glucose_bar = f"{glucose_color}█{reset}" * glucose_bar_pos + f"{dim}░{reset}" * (20 - glucose_bar_pos)
                        print(f"  🍎 Glucose:     {glucose_color}{self.current_glucose:5.2f} mmol/L{reset} {glucose_status}")
                        print(f"     {dim}[{glucose_bar}] 2.5-15.0 mmol/L{reset}")
                        
                        # Heart rate with bar
                        hr_status = "⚠️" if self.current_heart_rate < 70 or self.current_heart_rate > 120 else "✓"
                        hr_color = "\033[91m" if self.current_heart_rate < 70 or self.current_heart_rate > 120 else "\033[92m"
                        hr_bar_pos = int((self.current_heart_rate - 55) / 90 * 20)
                        hr_bar_pos = max(0, min(20, hr_bar_pos))
                        hr_bar = f"{hr_color}█{reset}" * hr_bar_pos + f"{dim}░{reset}" * (20 - hr_bar_pos)
                        print(f"  ❤️  Heart Rate:  {hr_color}{self.current_heart_rate:5.0f} bpm{reset}     {hr_status}")
                        print(f"     {dim}[{hr_bar}] 55-145 bpm{reset}")
                        
                        # Mood with bar
                        mood_status = "⚠️" if self.current_mood < 0.4 else "✓"
                        mood_color = "\033[91m" if self.current_mood < 0.4 else "\033[92m"
                        mood_bar = f"{mood_color}█{reset}" * int(self.current_mood * 20) + f"{dim}░{reset}" * (20 - int(self.current_mood * 20))
                        print(f"  😊 Mood:        {mood_color}{self.current_mood:5.2f}{reset}          {mood_status}")
                        print(f"     {dim}[{mood_bar}] 0.0-1.0{reset}")
                        
                        # Activity
                        activity_bar = f"\033[92m█{reset}" * int(self.current_activity * 20) + f"{dim}░{reset}" * (20 - int(self.current_activity * 20))
                        print(f"  🏃 Activity:    {self.current_activity:5.2f}")
                        print(f"     {dim}[{activity_bar}] 0.0-1.0{reset}")
                        
                        if hasattr(self, 'current_spo2'):
                            spo2_status = "⚠️" if self.current_spo2 < 95 else "✓"
                            spo2_color = "\033[91m" if self.current_spo2 < 95 else "\033[92m"
                            print(f"  🫁 SpO2:        {spo2_color}{self.current_spo2:5.1f}%{reset}         {spo2_status}")
                        if hasattr(self, 'asthma_risk_level'):
                            asthma_status = "⚠️" if self.asthma_risk_level > 0.6 else "✓"
                            asthma_color = "\033[91m" if self.asthma_risk_level > 0.6 else "\033[92m"
                            asthma_bar = f"{asthma_color}█{reset}" * int(self.asthma_risk_level * 20) + f"{dim}░{reset}" * (20 - int(self.asthma_risk_level * 20))
                            print(f"  🌬️  Asthma Risk: {asthma_color}{self.asthma_risk_level:5.2f}{reset}          {asthma_status}")
                            print(f"     {dim}[{asthma_bar}] 0.0-1.0{reset}")
                        
                        print(f"\n{stat_color}{'─'*80}{reset}\n")
                else:
                    # Compact output with better formatting
                    status = event.get("safety_status", "UNKNOWN")
                    status_icon = "🔴" if status == "DANGER" else "🟡" if status == "MONITOR" else "🟢"
                    status_color = self._get_status_color(status)
                    reset = "\033[0m"
                    event_type = event.get('event_type', 'unknown')
                    event_type_display = str(event_type).replace('_', ' ').title()
                    value = event.get('value', 0)
                    unit = event.get('unit', '')
                    print(f"{status_color}[{datetime.now().strftime('%H:%M:%S')}]{reset} {status_icon} {event_type_display:25s} {value:6.2f} {unit:8s} {status_color}{status:^8s}{reset}")
                
                # Save to child's history file
                self._append_to_history(event)
                
                # Also output to custom file if specified
                if output_file:
                    with open(output_file, 'a') as f:
                        f.write(json.dumps(event) + '\n')
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            total = self.stats['total_events']
            danger = self.stats['danger_events']
            monitor = self.stats['monitor_events']
            safe = self.stats['safe_events']
            anomalies = self.stats['anomalies_detected']
            uptime = round(time.time() - self.start_time, 0)
            
            final_color = "\033[93m"
            reset = "\033[0m"
            bold = "\033[1m"
            dim = "\033[2m"
            
            print(f"\n\n{final_color}{'═'*80}{reset}")
            print(f"{final_color}{bold}{'🛑 Session Ended'.center(80)}{reset}")
            print(f"{final_color}{'═'*80}{reset}")
            
            print(f"\n{bold}📊 Final Statistics:{reset}")
            print(f"{dim}{'─'*78}{reset}")
            print(f"  Total Events: {bold}{total}{reset}")
            
            # Safety breakdown with visual bars
            danger_pct = danger*100//total if total > 0 else 0
            monitor_pct = monitor*100//total if total > 0 else 0
            safe_pct = safe*100//total if total > 0 else 0
            
            danger_bar = "\033[91m█\033[0m" * (danger_pct // 5) + dim + "░" * (20 - danger_pct // 5) + reset
            monitor_bar = "\033[93m█\033[0m" * (monitor_pct // 5) + dim + "░" * (20 - monitor_pct // 5) + reset
            safe_bar = "\033[92m█\033[0m" * (safe_pct // 5) + dim + "░" * (20 - safe_pct // 5) + reset
            
            print(f"\n  Safety Status:")
            print(f"    🔴 DANGER:  {danger:3d} ({danger_pct:3d}%) [{danger_bar}]")
            print(f"    🟡 MONITOR: {monitor:3d} ({monitor_pct:3d}%) [{monitor_bar}]")
            print(f"    🟢 SAFE:    {safe:3d} ({safe_pct:3d}%) [{safe_bar}]")
            
            print(f"\n  ⚠️  Anomalies: {anomalies} ({anomalies*100//total if total > 0 else 0}%)")
            print(f"  ⏱️  Runtime: {uptime//60}m {uptime%60}s")
            if total > 0:
                print(f"  📈 Avg Time: {uptime/total:.1f}s per event")
            
            # Final health snapshot
            print(f"\n{bold}💚 Final Health Snapshot:{reset}")
            print(f"{dim}{'─'*78}{reset}")
            
            glucose_status = "⚠️" if self.current_glucose < 4.0 or self.current_glucose > 9.0 else "✓"
            glucose_color = "\033[91m" if self.current_glucose < 4.0 or self.current_glucose > 9.0 else "\033[92m"
            print(f"  🍎 Glucose:     {glucose_color}{self.current_glucose:5.2f} mmol/L{reset} {glucose_status}")
            
            hr_status = "⚠️" if self.current_heart_rate < 70 or self.current_heart_rate > 120 else "✓"
            hr_color = "\033[91m" if self.current_heart_rate < 70 or self.current_heart_rate > 120 else "\033[92m"
            print(f"  ❤️  Heart Rate:  {hr_color}{self.current_heart_rate:5.0f} bpm{reset}     {hr_status}")
            
            mood_status = "⚠️" if self.current_mood < 0.4 else "✓"
            mood_color = "\033[91m" if self.current_mood < 0.4 else "\033[92m"
            print(f"  😊 Mood:        {mood_color}{self.current_mood:5.2f}{reset}          {mood_status}")
            print(f"  🏃 Activity:    {self.current_activity:5.2f}")
            
            if hasattr(self, 'current_spo2'):
                spo2_status = "⚠️" if self.current_spo2 < 95 else "✓"
                spo2_color = "\033[91m" if self.current_spo2 < 95 else "\033[92m"
                print(f"  🫁 SpO2:        {spo2_color}{self.current_spo2:5.1f}%{reset}         {spo2_status}")
            if hasattr(self, 'asthma_risk_level'):
                asthma_status = "⚠️" if self.asthma_risk_level > 0.6 else "✓"
                asthma_color = "\033[91m" if self.asthma_risk_level > 0.6 else "\033[92m"
                print(f"  🌬️  Asthma Risk: {asthma_color}{self.asthma_risk_level:5.2f}{reset}          {asthma_status}")
            
            print(f"\n{final_color}{'═'*80}{reset}\n")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Play-Protect Medical Data Simulator")
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval between events in seconds (default: 30)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for JSON events (default: stdout only)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="DeepSeek API key (or set DEEPSEEK_API_KEY env var)"
    )
    parser.add_argument(
        "--api-base",
        type=str,
        default="https://api.deepseek.com",
        help="DeepSeek API base URL"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Quiet mode - minimal output"
    )
    
    args = parser.parse_args()
    
    async with MedicalDataSimulator(deepseek_api_key=args.api_key, api_base=args.api_base) as simulator:
        await simulator.run_continuous(
            interval_seconds=args.interval,
            output_file=args.output,
            verbose=not args.quiet
        )


if __name__ == "__main__":
    asyncio.run(main())

