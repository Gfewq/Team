"""
Child Profile Management
Handles CRUD operations for child profiles with JSON file storage.
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from backend.models import ChildProfile, ChildProfileCreate, ChildProfileUpdate


# Data directory paths
DATA_DIR = Path(__file__).parent.parent / "data"
PROFILES_FILE = DATA_DIR / "profiles.json"
HISTORY_DIR = DATA_DIR / "history"


def ensure_data_dirs():
    """Ensure data directories exist"""
    DATA_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)
    if not PROFILES_FILE.exists():
        with open(PROFILES_FILE, 'w') as f:
            json.dump({"children": []}, f, indent=2)


def _load_profiles() -> Dict[str, Any]:
    """Load profiles from JSON file"""
    ensure_data_dirs()
    try:
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"children": []}


def _save_profiles(data: Dict[str, Any]):
    """Save profiles to JSON file"""
    ensure_data_dirs()
    with open(PROFILES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def generate_child_id() -> str:
    """Generate a unique child ID"""
    return f"child_{uuid.uuid4().hex[:8]}"


def get_age_appropriate_baselines(age: int, condition: str) -> Dict[str, Any]:
    """Get age-appropriate baseline values for a child"""
    # Heart rate decreases with age (pediatric norms)
    if age <= 5:
        hr = 100
    elif age <= 8:
        hr = 90
    elif age <= 12:
        hr = 85
    else:
        hr = 80
    
    return {
        "baseline_heart_rate": hr,
        "baseline_glucose": 5.5 if condition in ["diabetes", "both"] else 5.0,
        "baseline_spo2": 98.0
    }


# === CRUD Operations ===

def create_child(profile_data: ChildProfileCreate) -> ChildProfile:
    """Create a new child profile"""
    data = _load_profiles()
    
    # Generate ID and set defaults
    child_id = generate_child_id()
    baselines = get_age_appropriate_baselines(profile_data.age, profile_data.condition)
    
    child_dict = {
        "id": child_id,
        "name": profile_data.name,
        "age": profile_data.age,
        "condition": profile_data.condition,
        "parent_name": profile_data.parent_name,
        "avatar": profile_data.avatar or "lion",
        "baseline_glucose": profile_data.baseline_glucose or baselines["baseline_glucose"],
        "baseline_heart_rate": profile_data.baseline_heart_rate or baselines["baseline_heart_rate"],
        "baseline_spo2": baselines["baseline_spo2"],
        "xp": 0,
        "level": 1,
        "streak": 0,
        "created_at": datetime.now().isoformat()
    }
    
    data["children"].append(child_dict)
    _save_profiles(data)
    
    # Create history file for this child
    history_file = HISTORY_DIR / f"{child_id}.jsonl"
    history_file.touch()
    
    return ChildProfile(**child_dict)


def get_child(child_id: str) -> Optional[ChildProfile]:
    """Get a child profile by ID"""
    data = _load_profiles()
    for child in data["children"]:
        if child["id"] == child_id:
            return ChildProfile(**child)
    return None


def list_children() -> List[ChildProfile]:
    """List all child profiles"""
    data = _load_profiles()
    return [ChildProfile(**child) for child in data["children"]]


def update_child(child_id: str, updates: ChildProfileUpdate) -> Optional[ChildProfile]:
    """Update a child profile"""
    data = _load_profiles()
    
    for i, child in enumerate(data["children"]):
        if child["id"] == child_id:
            # Apply updates (only non-None values)
            update_dict = updates.model_dump(exclude_none=True)
            
            # If age changed, update baselines
            if "age" in update_dict or "condition" in update_dict:
                new_age = update_dict.get("age", child["age"])
                new_condition = update_dict.get("condition", child["condition"])
                baselines = get_age_appropriate_baselines(new_age, new_condition)
                # Only update baselines if not explicitly provided
                if "baseline_heart_rate" not in update_dict:
                    update_dict["baseline_heart_rate"] = baselines["baseline_heart_rate"]
            
            child.update(update_dict)
            data["children"][i] = child
            _save_profiles(data)
            return ChildProfile(**child)
    
    return None


def delete_child(child_id: str) -> bool:
    """Delete a child profile"""
    data = _load_profiles()
    
    for i, child in enumerate(data["children"]):
        if child["id"] == child_id:
            del data["children"][i]
            _save_profiles(data)
            
            # Optionally delete history file
            history_file = HISTORY_DIR / f"{child_id}.jsonl"
            if history_file.exists():
                history_file.unlink()
            
            return True
    
    return False


def update_child_stats(child_id: str, xp_gain: int = 0, level_up: bool = False) -> Optional[ChildProfile]:
    """Update a child's gamification stats"""
    data = _load_profiles()
    
    for i, child in enumerate(data["children"]):
        if child["id"] == child_id:
            child["xp"] = child.get("xp", 0) + xp_gain
            
            # Check for level up
            level = child.get("level", 1)
            xp_for_next_level = level * 100
            
            if child["xp"] >= xp_for_next_level:
                child["level"] = level + 1
                child["xp"] = child["xp"] - xp_for_next_level
            
            data["children"][i] = child
            _save_profiles(data)
            return ChildProfile(**child)
    
    return None


# === History Operations ===

def get_child_history_file(child_id: str) -> Path:
    """Get the path to a child's history file"""
    ensure_data_dirs()
    return HISTORY_DIR / f"{child_id}.jsonl"


def append_event_to_history(child_id: str, event: Dict[str, Any]):
    """Append an event to a child's history"""
    history_file = get_child_history_file(child_id)
    
    # Add child_id to event
    event["child_id"] = child_id
    
    with open(history_file, 'a') as f:
        f.write(json.dumps(event) + '\n')


def get_child_history(child_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get a child's event history"""
    history_file = get_child_history_file(child_id)
    
    if not history_file.exists():
        return []
    
    events = []
    try:
        with open(history_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    events.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading history for {child_id}: {e}")
    
    return events


def clear_child_history(child_id: str):
    """Clear a child's event history"""
    history_file = get_child_history_file(child_id)
    if history_file.exists():
        with open(history_file, 'w') as f:
            pass  # Empty the file
