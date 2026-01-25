"""
Simulation Scenarios
Predefined health scenarios for meaningful simulations instead of pure random events.
"""

from typing import Dict, List, Any, Callable, Generator
from dataclasses import dataclass
from enum import Enum
import random
from datetime import datetime


class ScenarioCategory(Enum):
    EPISODE = "episode"  # Short events (5-15 mins)
    FULL_DAY = "full_day"  # Full day patterns (simulated in accelerated time)


@dataclass
class ScenarioDefinition:
    """Definition of a simulation scenario"""
    id: str
    name: str
    description: str
    category: ScenarioCategory
    duration_minutes: int
    applicable_conditions: List[str]  # ["diabetes", "asthma", "both"]
    generate_events: Callable  # Function that generates events


# === Event Generation Helpers ===

def _create_event(
    event_type: str,
    value: float,
    unit: str,
    urgency: str,
    safety_status: str,
    health_score: float,
    metadata: Dict[str, Any] = None,
    trend: str = "stable",
    anomaly_score: float = 0.1,
    reasoning: str = "",
    correlations: List[str] = None
) -> Dict[str, Any]:
    """Helper to create a properly formatted event"""
    return {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "value": round(value, 2),
        "unit": unit,
        "urgency": urgency,
        "safety_status": safety_status,
        "health_score": round(health_score, 1),
        "metadata": metadata or {},
        "trend": trend,
        "anomaly_score": round(anomaly_score, 3),
        "llm_reasoning": reasoning,
        "correlation_tags": correlations or []
    }


# === Episode Scenarios ===

def generate_hypoglycemia_episode(child_profile: Dict, num_events: int = 5) -> Generator[Dict, None, None]:
    """
    Simulates a hypoglycemia (low blood sugar) episode.
    Glucose drops to 3.2-3.8, mood drops, fatigue increases.
    """
    baseline_glucose = child_profile.get("baseline_glucose", 5.5)
    
    # Phase 1: Initial drop
    glucose = baseline_glucose - random.uniform(0.5, 1.0)
    yield _create_event(
        event_type="glucose_drop",
        value=glucose,
        unit="mmol/L",
        urgency="medium",
        safety_status="MONITOR",
        health_score=65,
        trend="falling",
        anomaly_score=0.4,
        reasoning="Glucose trending downward. Monitor for hypoglycemia symptoms.",
        correlations=["trending_low"],
        metadata={"phase": "initial_drop", "device": "cgm"}
    )
    
    # Phase 2: Critical low
    for i in range(num_events - 3):
        glucose = random.uniform(3.2, 3.8)
        mood = random.uniform(0.2, 0.4)
        
        yield _create_event(
            event_type="glucose_drop",
            value=glucose,
            unit="mmol/L",
            urgency="critical",
            safety_status="DANGER",
            health_score=35,
            trend="falling" if i == 0 else "stable",
            anomaly_score=0.85,
            reasoning="Critical hypoglycemia detected. Immediate intervention needed - provide fast-acting glucose.",
            correlations=["hypoglycemia", "low_mood", "fatigue"],
            metadata={"phase": "critical", "requires_intervention": True}
        )
        
        # Accompanying mood drop
        yield _create_event(
            event_type="mood_indicator",
            value=mood,
            unit="normalized_score",
            urgency="high",
            safety_status="MONITOR",
            health_score=40,
            reasoning="Low mood likely caused by hypoglycemia. Child may feel shaky, confused, or irritable.",
            correlations=["hypoglycemia_symptom"],
            metadata={"context": "hypoglycemia_effect"}
        )
    
    # Phase 3: Recovery (after treatment)
    glucose = random.uniform(4.5, 5.5)
    yield _create_event(
        event_type="glucose_normal",
        value=glucose,
        unit="mmol/L",
        urgency="low",
        safety_status="SAFE",
        health_score=75,
        trend="rising",
        anomaly_score=0.2,
        reasoning="Glucose recovering to normal range after treatment.",
        correlations=["recovering"],
        metadata={"phase": "recovery"}
    )


def generate_hyperglycemia_spike(child_profile: Dict, num_events: int = 4) -> Generator[Dict, None, None]:
    """
    Simulates a post-meal glucose spike (hyperglycemia).
    Glucose rises to 10-14 range, then gradually comes down.
    """
    # Phase 1: Rapid rise after meal
    glucose = random.uniform(9.0, 11.0)
    yield _create_event(
        event_type="glucose_spike",
        value=glucose,
        unit="mmol/L",
        urgency="medium",
        safety_status="MONITOR",
        health_score=60,
        trend="rising",
        anomaly_score=0.5,
        reasoning="Post-meal glucose spike detected. This is typical after eating.",
        correlations=["post_meal"],
        metadata={"phase": "rising", "meal_effect": 2.5}
    )
    
    # Phase 2: Peak
    glucose = random.uniform(11.0, 14.0)
    yield _create_event(
        event_type="glucose_spike",
        value=glucose,
        unit="mmol/L",
        urgency="high",
        safety_status="MONITOR",
        health_score=50,
        trend="stable",
        anomaly_score=0.7,
        reasoning="Glucose at peak. Consider insulin correction if prescribed.",
        correlations=["hyperglycemia", "needs_monitoring"],
        metadata={"phase": "peak", "above_target": True}
    )
    
    # Phase 3-4: Gradual decline
    for i in range(num_events - 2):
        glucose = random.uniform(7.0, 10.0) - (i * 1.5)
        glucose = max(glucose, 5.5)
        yield _create_event(
            event_type="glucose_spike" if glucose > 9.0 else "glucose_normal",
            value=glucose,
            unit="mmol/L",
            urgency="low" if glucose < 9.0 else "medium",
            safety_status="SAFE" if glucose < 9.0 else "MONITOR",
            health_score=70 + (i * 5),
            trend="falling",
            anomaly_score=0.3 - (i * 0.1),
            reasoning="Glucose returning to normal range." if glucose < 9.0 else "Glucose still elevated but trending down.",
            correlations=["recovering"] if glucose < 9.0 else ["still_elevated"],
            metadata={"phase": "declining"}
        )


def generate_asthma_trigger(child_profile: Dict, num_events: int = 5) -> Generator[Dict, None, None]:
    """
    Simulates an asthma trigger event.
    Rising respiratory rate, SpO2 drop, increased risk score.
    """
    # Phase 1: Environmental trigger detected
    yield _create_event(
        event_type="environmental_trigger",
        value=0.75,
        unit="risk_score",
        urgency="medium",
        safety_status="MONITOR",
        health_score=65,
        reasoning="High pollen count detected in the environment. Asthma risk increasing.",
        correlations=["high_pollen", "trigger_detected"],
        metadata={
            "pollen_count": 0.8,
            "air_quality_index": 55,
            "location": "outdoor"
        }
    )
    
    # Phase 2: Rising asthma risk
    for i in range(2):
        risk = 0.6 + (i * 0.15)
        resp_rate = 26 + (i * 3)
        yield _create_event(
            event_type="asthma_risk",
            value=risk,
            unit="risk_score",
            urgency="high",
            safety_status="DANGER" if risk > 0.7 else "MONITOR",
            health_score=50 - (i * 10),
            trend="rising",
            anomaly_score=risk,
            reasoning="Asthma symptoms developing. Consider preventive inhaler use." if i == 0 else "Significant asthma risk. Use rescue inhaler if prescribed.",
            correlations=["high_pollen", "elevated_respiratory_rate"],
            metadata={
                "respiratory_rate": resp_rate,
                "pollen_count": 0.8,
                "air_quality_index": 50
            }
        )
    
    # Phase 3: SpO2 drop
    spo2 = random.uniform(94, 96)
    yield _create_event(
        event_type="oxygen_saturation",
        value=spo2,
        unit="%",
        urgency="high",
        safety_status="DANGER",
        health_score=45,
        trend="falling",
        anomaly_score=0.75,
        reasoning="Oxygen saturation dropping. This requires immediate attention.",
        correlations=["asthma_episode", "low_oxygen"],
        metadata={"perfusion_index": 2.1}
    )
    
    # Phase 4: Recovery after treatment
    yield _create_event(
        event_type="asthma_risk",
        value=0.3,
        unit="risk_score",
        urgency="low",
        safety_status="SAFE",
        health_score=80,
        trend="falling",
        anomaly_score=0.2,
        reasoning="Asthma symptoms subsiding after treatment. Continue monitoring.",
        correlations=["recovering"],
        metadata={
            "respiratory_rate": 22,
            "treatment_given": True
        }
    )


def generate_anxiety_episode(child_profile: Dict, num_events: int = 4) -> Generator[Dict, None, None]:
    """
    Simulates an anxiety/stress episode.
    Elevated heart rate, low mood, high stress indicators.
    """
    baseline_hr = child_profile.get("baseline_heart_rate", 90)
    
    # Phase 1: Rising heart rate
    hr = baseline_hr + random.uniform(25, 35)
    yield _create_event(
        event_type="heart_rate_elevated",
        value=hr,
        unit="bpm",
        urgency="medium",
        safety_status="MONITOR",
        health_score=60,
        trend="rising",
        anomaly_score=0.5,
        reasoning="Elevated heart rate detected. May indicate stress or anxiety.",
        correlations=["stress_indicator"],
        metadata={"activity_level": 0.3, "stress_level": 0.7}
    )
    
    # Phase 2: Low mood + high stress
    yield _create_event(
        event_type="mood_indicator",
        value=random.uniform(0.25, 0.35),
        unit="normalized_score",
        urgency="high",
        safety_status="MONITOR",
        health_score=50,
        reasoning="Child appears anxious or upset. Consider checking in with them.",
        correlations=["high_stress", "elevated_heart_rate"],
        metadata={
            "context": "stress_observed",
            "facial_expression_score": 0.3,
            "interaction_quality": "low"
        }
    )
    
    yield _create_event(
        event_type="stress_indicator",
        value=0.8,
        unit="normalized_score",
        urgency="high",
        safety_status="MONITOR",
        health_score=45,
        reasoning="High stress levels detected. Child may benefit from calming activities.",
        correlations=["anxiety_episode", "needs_support"],
        metadata={"source": "behavioral_analysis"}
    )
    
    # Phase 3: Calming down
    yield _create_event(
        event_type="mood_indicator",
        value=random.uniform(0.55, 0.65),
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=75,
        trend="rising",
        reasoning="Child is calming down. Mood improving.",
        correlations=["recovering"],
        metadata={"context": "calming_activity", "interaction_quality": "medium"}
    )


def generate_healthy_reading(child_profile: Dict, num_events: int = 4) -> Generator[Dict, None, None]:
    """
    Simulates healthy, normal readings across all metrics.
    """
    baseline_glucose = child_profile.get("baseline_glucose", 5.5)
    baseline_hr = child_profile.get("baseline_heart_rate", 90)
    
    # Normal glucose
    yield _create_event(
        event_type="glucose_normal",
        value=baseline_glucose + random.uniform(-0.5, 0.5),
        unit="mmol/L",
        urgency="low",
        safety_status="SAFE",
        health_score=90,
        reasoning="Glucose levels are excellent. Keep up the good work!",
        metadata={"device": "cgm", "time_of_day": datetime.now().strftime("%H:%M")}
    )
    
    # Normal heart rate
    yield _create_event(
        event_type="heart_rate_elevated",  # Using this type but with normal values
        value=baseline_hr + random.uniform(-5, 10),
        unit="bpm",
        urgency="low",
        safety_status="SAFE",
        health_score=92,
        reasoning="Heart rate is normal and healthy.",
        metadata={"activity_level": 0.4}
    )
    
    # Good mood
    yield _create_event(
        event_type="mood_indicator",
        value=random.uniform(0.7, 0.9),
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=95,
        reasoning="Child is in a great mood! Everything looks good.",
        metadata={"context": "play_activity", "interaction_quality": "high"}
    )
    
    # Good activity
    yield _create_event(
        event_type="activity_level",
        value=random.uniform(0.5, 0.7),
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=93,
        reasoning="Healthy activity level. Child is active and engaged.",
        metadata={"movement_type": "walking", "steps_per_minute": 80}
    )


# === Full Day Scenarios ===

def generate_healthy_school_day(child_profile: Dict, num_events: int = 12) -> Generator[Dict, None, None]:
    """
    Simulates a typical healthy school day.
    Morning routine -> school -> lunch -> afternoon -> evening
    """
    baseline_glucose = child_profile.get("baseline_glucose", 5.5)
    baseline_hr = child_profile.get("baseline_heart_rate", 90)
    
    phases = [
        ("morning", "Waking up, getting ready for school"),
        ("breakfast", "Breakfast - expect glucose rise"),
        ("school_morning", "Morning classes"),
        ("recess", "Active play during recess"),
        ("lunch", "Lunch time - glucose spike expected"),
        ("school_afternoon", "Afternoon classes"),
        ("after_school", "After school activities"),
        ("dinner", "Dinner time"),
        ("evening", "Evening wind-down"),
        ("bedtime", "Getting ready for bed")
    ]
    
    events_per_phase = max(1, num_events // len(phases))
    
    for phase_id, phase_desc in phases:
        if phase_id == "morning":
            yield _create_event(
                event_type="glucose_normal",
                value=baseline_glucose + random.uniform(-0.3, 0.3),
                unit="mmol/L",
                urgency="low",
                safety_status="SAFE",
                health_score=85,
                reasoning=f"Morning glucose check - normal range. {phase_desc}",
                metadata={"phase": phase_id, "time_context": "morning"}
            )
        elif phase_id in ["breakfast", "lunch", "dinner"]:
            # Meal-related glucose spike
            yield _create_event(
                event_type="glucose_spike",
                value=baseline_glucose + random.uniform(2.0, 3.5),
                unit="mmol/L",
                urgency="low",
                safety_status="SAFE",
                health_score=75,
                trend="rising",
                reasoning=f"Post-meal glucose rise - this is normal. {phase_desc}",
                correlations=["post_meal"],
                metadata={"phase": phase_id, "meal_effect": 2.5}
            )
        elif phase_id == "recess":
            # Active play
            yield _create_event(
                event_type="activity_level",
                value=random.uniform(0.7, 0.9),
                unit="normalized_score",
                urgency="low",
                safety_status="SAFE",
                health_score=95,
                reasoning=f"Great physical activity! {phase_desc}",
                correlations=["high_activity"],
                metadata={"phase": phase_id, "movement_type": "running", "steps_per_minute": 110}
            )
            yield _create_event(
                event_type="heart_rate_elevated",
                value=baseline_hr + random.uniform(20, 35),
                unit="bpm",
                urgency="low",
                safety_status="SAFE",
                health_score=90,
                reasoning="Elevated heart rate due to physical activity - healthy response.",
                metadata={"phase": phase_id, "activity_level": 0.8}
            )
        elif phase_id in ["school_morning", "school_afternoon"]:
            yield _create_event(
                event_type="mood_indicator",
                value=random.uniform(0.6, 0.8),
                unit="normalized_score",
                urgency="low",
                safety_status="SAFE",
                health_score=88,
                reasoning=f"Child engaged in learning. {phase_desc}",
                metadata={"phase": phase_id, "context": "school_activity"}
            )
        elif phase_id == "evening":
            yield _create_event(
                event_type="activity_level",
                value=random.uniform(0.3, 0.5),
                unit="normalized_score",
                urgency="low",
                safety_status="SAFE",
                health_score=85,
                reasoning="Winding down for the evening.",
                metadata={"phase": phase_id, "movement_type": "sedentary"}
            )
        elif phase_id == "bedtime":
            yield _create_event(
                event_type="glucose_normal",
                value=baseline_glucose + random.uniform(-0.2, 0.5),
                unit="mmol/L",
                urgency="low",
                safety_status="SAFE",
                health_score=90,
                reasoning="Bedtime glucose check - good levels for overnight.",
                metadata={"phase": phase_id, "time_context": "bedtime"}
            )


def generate_sick_day(child_profile: Dict, num_events: int = 10) -> Generator[Dict, None, None]:
    """
    Simulates a sick day - elevated temperature, low activity, variable glucose.
    """
    baseline_glucose = child_profile.get("baseline_glucose", 5.5)
    
    # Temperature elevated
    yield _create_event(
        event_type="temperature_anomaly",
        value=38.2,
        unit="celsius",
        urgency="medium",
        safety_status="MONITOR",
        health_score=55,
        reasoning="Elevated temperature detected. Child may be unwell.",
        correlations=["fever", "illness"],
        metadata={"baseline_temp": 36.8}
    )
    
    # Variable glucose (illness can affect it)
    for i in range(3):
        glucose = baseline_glucose + random.uniform(-1.0, 2.5)
        glucose = max(3.5, min(12.0, glucose))
        status = "SAFE" if 4.0 <= glucose <= 9.0 else "MONITOR"
        yield _create_event(
            event_type="glucose_spike" if glucose > 7.0 else "glucose_normal" if glucose >= 4.0 else "glucose_drop",
            value=glucose,
            unit="mmol/L",
            urgency="medium" if status == "MONITOR" else "low",
            safety_status=status,
            health_score=60 if status == "SAFE" else 45,
            trend="volatile",
            reasoning="Glucose levels may be more variable during illness. Monitor closely.",
            correlations=["illness_effect"],
            metadata={"illness_impact": True}
        )
    
    # Low activity
    yield _create_event(
        event_type="activity_level",
        value=random.uniform(0.1, 0.25),
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=50,
        reasoning="Low activity - expected when unwell. Rest is important.",
        metadata={"movement_type": "sedentary", "sleep_state": "light_sleep"}
    )
    
    # Low mood
    yield _create_event(
        event_type="mood_indicator",
        value=random.uniform(0.3, 0.45),
        unit="normalized_score",
        urgency="medium",
        safety_status="MONITOR",
        health_score=55,
        reasoning="Child may be feeling down due to illness. Extra comfort recommended.",
        correlations=["illness_effect"],
        metadata={"context": "unwell"}
    )
    
    # Hydration reminder
    yield _create_event(
        event_type="hydration_level",
        value=0.5,
        unit="normalized_score",
        urgency="medium",
        safety_status="MONITOR",
        health_score=60,
        reasoning="Hydration is important when sick. Encourage fluids.",
        metadata={"reminder": "encourage_fluids"}
    )


def generate_active_play_day(child_profile: Dict, num_events: int = 10) -> Generator[Dict, None, None]:
    """
    Simulates a very active play day - high activity, lower glucose from exercise.
    """
    baseline_glucose = child_profile.get("baseline_glucose", 5.5)
    baseline_hr = child_profile.get("baseline_heart_rate", 90)
    
    # High activity phases
    for i in range(4):
        activity = random.uniform(0.7, 0.95)
        yield _create_event(
            event_type="activity_level",
            value=activity,
            unit="normalized_score",
            urgency="low",
            safety_status="SAFE",
            health_score=95,
            reasoning="Excellent physical activity! Exercise is great for health.",
            correlations=["high_activity", "exercise"],
            metadata={"movement_type": "running", "steps_per_minute": int(activity * 120)}
        )
        
        # Elevated HR from exercise
        hr = baseline_hr + random.uniform(25, 45)
        yield _create_event(
            event_type="heart_rate_elevated",
            value=hr,
            unit="bpm",
            urgency="low",
            safety_status="SAFE",
            health_score=90,
            reasoning="Heart rate elevated due to exercise - this is healthy!",
            correlations=["exercise_response"],
            metadata={"activity_level": activity}
        )
    
    # Glucose dropping from exercise (important for diabetics)
    glucose = baseline_glucose - random.uniform(0.8, 1.5)
    status = "MONITOR" if glucose < 4.5 else "SAFE"
    yield _create_event(
        event_type="glucose_drop" if glucose < 4.5 else "glucose_normal",
        value=glucose,
        unit="mmol/L",
        urgency="medium" if glucose < 4.5 else "low",
        safety_status=status,
        health_score=70 if status == "SAFE" else 55,
        trend="falling",
        reasoning="Exercise lowers blood glucose. Consider a snack if continuing activity." if glucose < 4.5 else "Glucose is good after exercise.",
        correlations=["exercise_effect"],
        metadata={"exercise_impact": True}
    )
    
    # Great mood from play
    yield _create_event(
        event_type="mood_indicator",
        value=random.uniform(0.8, 0.95),
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=98,
        reasoning="Child is having a great time! Physical play boosts mood.",
        correlations=["positive_activity"],
        metadata={"context": "play_activity", "interaction_quality": "high"}
    )


def generate_stressful_test_day(child_profile: Dict, num_events: int = 8) -> Generator[Dict, None, None]:
    """
    Simulates a stressful school test day.
    Elevated stress, mood fluctuations, glucose variability from stress.
    """
    baseline_glucose = child_profile.get("baseline_glucose", 5.5)
    baseline_hr = child_profile.get("baseline_heart_rate", 90)
    
    # Morning anxiety
    yield _create_event(
        event_type="stress_indicator",
        value=0.65,
        unit="normalized_score",
        urgency="medium",
        safety_status="MONITOR",
        health_score=60,
        reasoning="Child appears stressed - may be nervous about school test.",
        correlations=["pre_test_anxiety"],
        metadata={"source": "behavioral_analysis", "context": "school_test"}
    )
    
    yield _create_event(
        event_type="heart_rate_elevated",
        value=baseline_hr + random.uniform(15, 25),
        unit="bpm",
        urgency="low",
        safety_status="SAFE",
        health_score=65,
        reasoning="Slightly elevated heart rate - could be test-related anxiety.",
        correlations=["stress_response"],
        metadata={"activity_level": 0.2, "stress_level": 0.65}
    )
    
    # Stress can affect glucose
    yield _create_event(
        event_type="glucose_spike",
        value=baseline_glucose + random.uniform(1.0, 2.0),
        unit="mmol/L",
        urgency="low",
        safety_status="SAFE",
        health_score=70,
        trend="rising",
        reasoning="Stress can raise blood glucose. This is a normal body response.",
        correlations=["stress_response"],
        metadata={"stress_impact": True}
    )
    
    # Lower mood during test
    yield _create_event(
        event_type="mood_indicator",
        value=random.uniform(0.4, 0.55),
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=65,
        reasoning="Child seems focused but slightly anxious. Normal for test situations.",
        metadata={"context": "concentration", "interaction_quality": "medium"}
    )
    
    # Post-test relief
    yield _create_event(
        event_type="mood_indicator",
        value=random.uniform(0.7, 0.85),
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=85,
        trend="rising",
        reasoning="Test is over! Child seems relieved and happier.",
        correlations=["stress_relief"],
        metadata={"context": "post_test_relief", "interaction_quality": "high"}
    )
    
    yield _create_event(
        event_type="stress_indicator",
        value=0.25,
        unit="normalized_score",
        urgency="low",
        safety_status="SAFE",
        health_score=90,
        trend="falling",
        reasoning="Stress levels back to normal after test completion.",
        metadata={"context": "relaxed"}
    )


# === Scenario Registry ===

SCENARIOS: Dict[str, ScenarioDefinition] = {
    # Episode scenarios
    "hypoglycemia_episode": ScenarioDefinition(
        id="hypoglycemia_episode",
        name="Hypoglycemia Episode",
        description="Low blood sugar episode with mood changes and recovery",
        category=ScenarioCategory.EPISODE,
        duration_minutes=10,
        applicable_conditions=["diabetes", "both"],
        generate_events=generate_hypoglycemia_episode
    ),
    "hyperglycemia_spike": ScenarioDefinition(
        id="hyperglycemia_spike",
        name="Post-Meal Glucose Spike",
        description="Blood sugar spike after eating, then gradual decline",
        category=ScenarioCategory.EPISODE,
        duration_minutes=15,
        applicable_conditions=["diabetes", "both"],
        generate_events=generate_hyperglycemia_spike
    ),
    "asthma_trigger": ScenarioDefinition(
        id="asthma_trigger",
        name="Asthma Trigger Event",
        description="Environmental trigger causing asthma symptoms",
        category=ScenarioCategory.EPISODE,
        duration_minutes=10,
        applicable_conditions=["asthma", "both"],
        generate_events=generate_asthma_trigger
    ),
    "anxiety_episode": ScenarioDefinition(
        id="anxiety_episode",
        name="Anxiety/Stress Episode",
        description="Elevated stress with heart rate and mood changes",
        category=ScenarioCategory.EPISODE,
        duration_minutes=8,
        applicable_conditions=["diabetes", "asthma", "both"],
        generate_events=generate_anxiety_episode
    ),
    "healthy_reading": ScenarioDefinition(
        id="healthy_reading",
        name="Healthy Readings",
        description="All metrics in normal, healthy ranges",
        category=ScenarioCategory.EPISODE,
        duration_minutes=5,
        applicable_conditions=["diabetes", "asthma", "both"],
        generate_events=generate_healthy_reading
    ),
    
    # Full day scenarios
    "healthy_school_day": ScenarioDefinition(
        id="healthy_school_day",
        name="Healthy School Day",
        description="Typical healthy day with school, meals, and activities",
        category=ScenarioCategory.FULL_DAY,
        duration_minutes=30,
        applicable_conditions=["diabetes", "asthma", "both"],
        generate_events=generate_healthy_school_day
    ),
    "sick_day": ScenarioDefinition(
        id="sick_day",
        name="Sick Day",
        description="Day when child is unwell with variable health metrics",
        category=ScenarioCategory.FULL_DAY,
        duration_minutes=25,
        applicable_conditions=["diabetes", "asthma", "both"],
        generate_events=generate_sick_day
    ),
    "active_play_day": ScenarioDefinition(
        id="active_play_day",
        name="Active Play Day",
        description="Very active day with lots of physical play and exercise",
        category=ScenarioCategory.FULL_DAY,
        duration_minutes=25,
        applicable_conditions=["diabetes", "asthma", "both"],
        generate_events=generate_active_play_day
    ),
    "stressful_test_day": ScenarioDefinition(
        id="stressful_test_day",
        name="Stressful Test Day",
        description="School day with a test causing stress and mood changes",
        category=ScenarioCategory.FULL_DAY,
        duration_minutes=20,
        applicable_conditions=["diabetes", "asthma", "both"],
        generate_events=generate_stressful_test_day
    ),
}


def get_scenario(scenario_id: str) -> ScenarioDefinition:
    """Get a scenario by ID"""
    if scenario_id not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    return SCENARIOS[scenario_id]


def list_scenarios(condition: str = None) -> List[Dict[str, Any]]:
    """List all available scenarios, optionally filtered by condition"""
    result = []
    for scenario in SCENARIOS.values():
        if condition is None or condition in scenario.applicable_conditions:
            result.append({
                "id": scenario.id,
                "name": scenario.name,
                "description": scenario.description,
                "category": scenario.category.value,
                "duration_minutes": scenario.duration_minutes,
                "conditions": scenario.applicable_conditions
            })
    return result


def run_scenario(scenario_id: str, child_profile: Dict, num_events: int = None) -> Generator[Dict, None, None]:
    """
    Run a scenario and yield events.
    
    Args:
        scenario_id: ID of the scenario to run
        child_profile: Child profile dict with baseline values
        num_events: Optional override for number of events
    
    Yields:
        Event dictionaries
    """
    scenario = get_scenario(scenario_id)
    
    # Use default event count based on scenario type
    if num_events is None:
        num_events = 5 if scenario.category == ScenarioCategory.EPISODE else 12
    
    yield from scenario.generate_events(child_profile, num_events)
