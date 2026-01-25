import { useState, useEffect } from 'react';
import './ChildSelector.css';

interface Child {
  id: string;
  name: string;
  age: number;
  condition: string;
  avatar: string;
  xp: number;
  level: number;
  streak: number;
}

interface ChildSelectorProps {
  onChildSelect: (child: Child | null) => void;
  selectedChild: Child | null;
}

export default function ChildSelector({ onChildSelect, selectedChild }: ChildSelectorProps) {
  const [children, setChildren] = useState<Child[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Fetch children from API
  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/children');
        if (res.ok) {
          const data = await res.json();
          setChildren(data);
          // Auto-select first child if none selected
          if (data.length > 0 && !selectedChild) {
            onChildSelect(data[0]);
          }
        }
      } catch (e) {
        console.log('Could not fetch children');
      } finally {
        setLoading(false);
      }
    };

    fetchChildren();
  }, []);

  const getAvatarEmoji = (condition: string) => {
    switch (condition) {
      case 'diabetes': return '🦁';
      case 'asthma': return '🐯';
      case 'both': return '🐻';
      default: return '🦁';
    }
  };

  if (loading) {
    return (
      <div className="child-selector loading">
        <span className="loading-text">Loading...</span>
      </div>
    );
  }

  if (children.length === 0) {
    return (
      <div className="child-selector empty">
        <span className="empty-text">No profiles yet</span>
      </div>
    );
  }

  return (
    <div className="child-selector">
      <button 
        className="selector-button" 
        onClick={() => setIsOpen(!isOpen)}
      >
        {selectedChild ? (
          <>
            <span className="selected-avatar">{getAvatarEmoji(selectedChild.condition)}</span>
            <span className="selected-name">{selectedChild.name}</span>
            <span className="selected-level">Lv.{selectedChild.level}</span>
          </>
        ) : (
          <span>Select Child</span>
        )}
        <span className="dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="selector-dropdown">
          {children.map((child) => (
            <button
              key={child.id}
              className={`child-option ${selectedChild?.id === child.id ? 'selected' : ''}`}
              onClick={() => {
                onChildSelect(child);
                setIsOpen(false);
              }}
            >
              <span className="option-avatar">{getAvatarEmoji(child.condition)}</span>
              <div className="option-info">
                <span className="option-name">{child.name}</span>
                <span className="option-details">
                  Age {child.age} • {child.condition}
                </span>
              </div>
              <div className="option-stats">
                <span className="option-level">Lv.{child.level}</span>
                {child.streak > 0 && (
                  <span className="option-streak">🔥{child.streak}</span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export type { Child };
