"""
Chat Memory System for Leo
Stores per-child chat history and parent instructions
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque

# Storage directory
DATA_DIR = Path(__file__).parent / "data"
CHAT_DIR = DATA_DIR / "chat_history"
INSTRUCTIONS_FILE = DATA_DIR / "parent_instructions.json"

# Ensure directories exist
CHAT_DIR.mkdir(parents=True, exist_ok=True)

# In-memory caches (also persist to disk)
_chat_history: Dict[str, deque] = {}  # child_id -> deque of messages
_parent_instructions: Dict[str, List[str]] = {}  # child_id -> list of instructions

MAX_HISTORY_PER_CHILD = 50  # Keep last 50 messages per child


def _load_instructions():
    """Load parent instructions from disk"""
    global _parent_instructions
    if INSTRUCTIONS_FILE.exists():
        try:
            with open(INSTRUCTIONS_FILE, 'r') as f:
                _parent_instructions = json.load(f)
        except:
            _parent_instructions = {}


def _save_instructions():
    """Save parent instructions to disk"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(INSTRUCTIONS_FILE, 'w') as f:
        json.dump(_parent_instructions, f, indent=2)


def _get_chat_file(child_id: str) -> Path:
    """Get path to chat history file for a child"""
    return CHAT_DIR / f"{child_id}_chat.json"


def _load_chat_history(child_id: str) -> deque:
    """Load chat history for a child from disk"""
    if child_id in _chat_history:
        return _chat_history[child_id]
    
    chat_file = _get_chat_file(child_id)
    if chat_file.exists():
        try:
            with open(chat_file, 'r') as f:
                data = json.load(f)
                _chat_history[child_id] = deque(data, maxlen=MAX_HISTORY_PER_CHILD)
        except:
            _chat_history[child_id] = deque(maxlen=MAX_HISTORY_PER_CHILD)
    else:
        _chat_history[child_id] = deque(maxlen=MAX_HISTORY_PER_CHILD)
    
    return _chat_history[child_id]


def _save_chat_history(child_id: str):
    """Save chat history for a child to disk"""
    CHAT_DIR.mkdir(parents=True, exist_ok=True)
    chat_file = _get_chat_file(child_id)
    if child_id in _chat_history:
        with open(chat_file, 'w') as f:
            json.dump(list(_chat_history[child_id]), f, indent=2)


def add_message(child_id: str, role: str, message: str, is_kid_mode: bool = True):
    """
    Add a message to a child's chat history
    
    Args:
        child_id: The child's ID
        role: 'user' (child or parent) or 'leo'
        message: The message content
        is_kid_mode: Whether this was in kid mode (child) or parent mode
    """
    if not child_id:
        return
    
    history = _load_chat_history(child_id)
    history.append({
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "message": message,
        "mode": "kid" if is_kid_mode else "parent"
    })
    _chat_history[child_id] = history
    _save_chat_history(child_id)


def get_recent_kid_chat(child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent kid-mode chat messages for a child
    Used by parent mode to know what the child discussed
    """
    if not child_id:
        return []
    
    history = _load_chat_history(child_id)
    kid_messages = [m for m in history if m.get("mode") == "kid"]
    return list(kid_messages)[-limit:]


def get_full_context(child_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get full chat context (both kid and parent messages)"""
    if not child_id:
        return []
    
    history = _load_chat_history(child_id)
    return list(history)[-limit:]


def add_parent_instruction(child_id: str, instruction: str):
    """
    Add a parent instruction for a child
    These are rules Leo should follow when talking to the child
    """
    if not child_id:
        return
    
    _load_instructions()
    
    if child_id not in _parent_instructions:
        _parent_instructions[child_id] = []
    
    # Avoid duplicates
    if instruction not in _parent_instructions[child_id]:
        _parent_instructions[child_id].append(instruction)
        _save_instructions()


def get_parent_instructions(child_id: str) -> List[str]:
    """Get all parent instructions for a child"""
    if not child_id:
        return []
    
    _load_instructions()
    return _parent_instructions.get(child_id, [])


def detect_and_store_instruction(child_id: str, message: str) -> bool:
    """
    Detect if a parent message contains an instruction for Leo to follow
    Returns True if an instruction was detected and stored
    """
    msg_lower = message.lower()
    
    # Instruction patterns
    instruction_patterns = [
        "if he asks", "if she asks", "if they ask",
        "don't let him", "don't let her", "don't let them",
        "tell him", "tell her", "tell them",
        "remind him", "remind her", "remind them",
        "make sure", "ensure that", "when he", "when she",
        "say no to", "deny", "refuse", "don't give",
        "encourage", "discourage", "limit", "restrict"
    ]
    
    for pattern in instruction_patterns:
        if pattern in msg_lower:
            # This looks like an instruction
            add_parent_instruction(child_id, message)
            return True
    
    return False


def format_kid_chat_summary(child_id: str) -> str:
    """Format a summary of what the child talked about"""
    recent = get_recent_kid_chat(child_id, limit=10)
    if not recent:
        return "No recent conversations with the child."
    
    summary_parts = []
    for msg in recent:
        role = "Child said" if msg["role"] == "user" else "Leo replied"
        summary_parts.append(f"- {role}: \"{msg['message'][:100]}{'...' if len(msg['message']) > 100 else ''}\"")
    
    return "\n".join(summary_parts[-6:])  # Last 6 exchanges


def format_parent_instructions(child_id: str) -> str:
    """Format parent instructions for inclusion in prompts"""
    instructions = get_parent_instructions(child_id)
    if not instructions:
        return "No specific parent instructions."
    
    return "\n".join([f"- {inst}" for inst in instructions[-5:]])  # Last 5 instructions


# Initialize on import
_load_instructions()
