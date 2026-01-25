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
  isKidMode?: boolean;
}

export default function ChildSelector({ onChildSelect, selectedChild, isKidMode = true }: ChildSelectorProps) {
  const [children, setChildren] = useState<Child[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newChild, setNewChild] = useState({
    name: '',
    age: 7,
    condition: 'none' as 'diabetes' | 'asthma' | 'both' | 'none',
    parent_name: ''
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch children from API
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

  useEffect(() => {
    fetchChildren();
  }, []);

  const handleAddChild = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!newChild.name.trim()) {
      setError('Please enter the child\'s name');
      return;
    }
    if (!newChild.parent_name.trim()) {
      setError('Please enter the parent/guardian name');
      return;
    }
    
    setIsSubmitting(true);
    try {
      const res = await fetch('http://localhost:8000/api/children', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newChild)
      });
      
      if (res.ok) {
        const created = await res.json();
        await fetchChildren(); // Refresh list
        onChildSelect(created); // Select the new child
        setShowAddForm(false);
        setNewChild({ name: '', age: 7, condition: 'none', parent_name: '' });
        setError('');
      } else {
        const errData = await res.json().catch(() => ({}));
        setError(errData.detail || 'Failed to create profile. Please try again.');
      }
    } catch (err) {
      console.log('Failed to create child profile:', err);
      setError('Connection error. Is the server running?');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getAvatarEmoji = (condition: string) => {
    switch (condition) {
      case 'diabetes': return '🦁';
      case 'asthma': return '🐯';
      case 'both': return '🐻';
      case 'none': return '😊';
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
          
          {/* Add New Child Button - Only show in parent mode */}
          {!isKidMode && (
            <button 
              className="child-option add-child-btn"
              onClick={() => {
                setShowAddForm(true);
                setIsOpen(false);
              }}
            >
              <span className="option-avatar">➕</span>
              <div className="option-info">
                <span className="option-name">Add New Child</span>
                <span className="option-details">Create a profile</span>
              </div>
            </button>
          )}
        </div>
      )}

      {/* Add Child Form Modal */}
      {showAddForm && (
        <div className="add-child-overlay" onClick={() => setShowAddForm(false)}>
          <div className="add-child-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>➕ Add New Child</h3>
              <button className="modal-close" onClick={() => setShowAddForm(false)}>×</button>
            </div>
            
            <form onSubmit={handleAddChild} className="add-child-form">
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-group">
                <label>👶 Child's Name</label>
                <input
                  type="text"
                  value={newChild.name}
                  onChange={e => setNewChild({...newChild, name: e.target.value})}
                  placeholder="e.g., Maya, Ethan..."
                />
              </div>
              
              <div className="form-row">
                <div className="form-group half">
                  <label>🎂 Age</label>
                  <input
                    type="number"
                    min="3"
                    max="18"
                    value={newChild.age}
                    onChange={e => setNewChild({...newChild, age: parseInt(e.target.value) || 7})}
                  />
                </div>
                
                <div className="form-group half">
                  <label>🏥 Health Condition</label>
                  <select
                    value={newChild.condition}
                    onChange={e => setNewChild({...newChild, condition: e.target.value as 'diabetes' | 'asthma' | 'both' | 'none'})}
                  >
                    <option value="none">😊 Healthy / None</option>
                    <option value="diabetes">🦁 Diabetes</option>
                    <option value="asthma">🐯 Asthma</option>
                    <option value="both">🐻 Both</option>
                  </select>
                </div>
              </div>
              
              <div className="form-group">
                <label>👨‍👩‍👧 Parent/Guardian Name</label>
                <input
                  type="text"
                  value={newChild.parent_name}
                  onChange={e => setNewChild({...newChild, parent_name: e.target.value})}
                  placeholder="Your name (for records)"
                />
              </div>
              
              <div className="form-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowAddForm(false)}>
                  Cancel
                </button>
                <button type="submit" className="submit-btn" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating...' : '✓ Create Profile'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export type { Child };
