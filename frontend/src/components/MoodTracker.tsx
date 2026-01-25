import { useState, useEffect } from 'react';
import './MoodTracker.css';

export interface MoodEntry {
  mood: string;
  label: string;
  timestamp: Date;
}

interface MoodTrackerProps {
  onMoodSelect: (mood: MoodEntry) => void;
  currentMood: MoodEntry | null;
}

const MOODS = [
  { emoji: '😊', label: 'Happy', color: '#00b894' },
  { emoji: '😐', label: 'Okay', color: '#fdcb6e' },
  { emoji: '😢', label: 'Sad', color: '#74b9ff' },
  { emoji: '😫', label: 'Tired', color: '#a29bfe' },
  { emoji: '🤒', label: 'Sick', color: '#ff7675' },
];

export default function MoodTracker({ onMoodSelect, currentMood }: MoodTrackerProps) {
  const [selectedMood, setSelectedMood] = useState<string | null>(currentMood?.mood || null);
  const [showConfirmation, setShowConfirmation] = useState(false);

  useEffect(() => {
    if (currentMood) {
      setSelectedMood(currentMood.mood);
    }
  }, [currentMood]);

  const handleMoodClick = (emoji: string, label: string) => {
    setSelectedMood(emoji);
    setShowConfirmation(true);
    
    const entry: MoodEntry = {
      mood: emoji,
      label: label,
      timestamp: new Date(),
    };
    
    onMoodSelect(entry);
    
    // Hide confirmation after 2 seconds
    setTimeout(() => setShowConfirmation(false), 2000);
  };

  return (
    <div className="mood-tracker">
      <div className="mood-header">
        <span className="mood-question">How are you feeling?</span>
      </div>
      
      <div className="mood-buttons">
        {MOODS.map((mood) => (
          <button
            key={mood.emoji}
            className={`mood-btn ${selectedMood === mood.emoji ? 'selected' : ''}`}
            onClick={() => handleMoodClick(mood.emoji, mood.label)}
            style={{ '--mood-color': mood.color } as React.CSSProperties}
            title={mood.label}
          >
            <span className="mood-emoji">{mood.emoji}</span>
            <span className="mood-label">{mood.label}</span>
          </button>
        ))}
      </div>

      {showConfirmation && (
        <div className="mood-confirmation">
          Leo knows you're feeling {selectedMood}!
        </div>
      )}
    </div>
  );
}
