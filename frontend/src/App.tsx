import { useState, useEffect, useCallback } from 'react';
import ChatBox from './components/ChatBox';
import LeoAvatar from './components/LeoAvatar';
import MoodTracker, { MoodEntry } from './components/MoodTracker';
import ParentDashboard from './components/ParentDashboard';
import ChildSelector, { Child } from './components/ChildSelector';
import VisionMode from './components/VisionMode';
import ScavengerHuntMode from './components/ScavengerHuntMode';
import { useVoice } from './hooks/useVoice';
import './App.css';

// 🌟 Motivational Thoughts of the Day
const THOUGHTS_OF_THE_DAY = [
  "You are braver than you believe! 🦁",
  "Every day is a new adventure! 🌈",
  "You make the world brighter! ✨",
  "Be kind to yourself today! 💕",
  "You are doing amazing! 🌟",
  "Small steps lead to big wins! 👣",
  "Your smile is your superpower! 😊",
  "Today is going to be great! 🎉",
  "You are stronger than you know! 💪",
  "Believe in your dreams! 🌙",
  "You are loved just as you are! ❤️",
  "Keep shining bright! ☀️",
  "Every mistake helps you grow! 🌱",
  "You are one of a kind! 🦄",
  "Be proud of how far you've come! 🏆",
  "Your kindness makes a difference! 🤗",
  "Dream big, little champion! 🚀",
  "You've got this! 💫",
  "Today you will learn something new! 📚",
  "Your courage inspires others! 🌺",
  "Happiness starts with a smile! 😄",
  "You are a wonderful friend! 🤝",
  "Keep being awesome! 🎨",
  "Your heart is full of gold! 💛",
  "Adventure awaits you today! 🗺️",
  "You make people happy! 🎈",
  "Be yourself, you're amazing! 🌻",
  "Good things are coming your way! 🍀",
  "You are a superhero! 🦸",
  "Keep trying, never give up! 🎯",
  "Your imagination is magical! ✨",
  "Spread joy wherever you go! 🌸",
  "You are important and special! 👑",
  "Today is full of possibilities! 🌅",
  "Be curious and explore! 🔍",
  "Your laugh is contagious! 😂",
  "You are capable of great things! 🏅",
  "Make today unforgettable! 📸",
  "You bring sunshine to others! 🌞",
  "Keep your head high! 🦒",
  "You are a star! ⭐",
  "Take care of your body, it's amazing! 🏃",
  "Friends are treasures! 💎",
  "Learning is your superpower! 🧠",
  "You are creative and smart! 🎭",
  "Enjoy the little moments! 🦋",
  "You make a difference! 🌍",
  "Stay positive and strong! 💪",
  "Your future is bright! 🔆",
  "Today, be your best self! 🌟"
];

import {
  UserStats,
  Message,
  HealthLog,
  HealthMetrics,
  HealthEvent,
  SimulatorAlert,
  EngagementData
} from './types';

// LocalStorage keys
const MOOD_HISTORY_KEY = 'leo_mood_history';
const CHAT_HISTORY_KEY = 'leo_chat_history';
const HEALTH_LOGS_KEY = 'leo_health_logs';
const ENGAGEMENT_KEY = 'leo_engagement';
const MEDICATIONS_KEY = 'leo_medications';

function App() {
  // Voice Hook
  const { speak, toggleMute, isMuted } = useVoice();

  // 1. STATE: Health Stats & Speaking Logic
  const [stats, setStats] = useState<UserStats>({ xp: 0, level: 1, status: 'Connecting...' });
  const [isLeoTalking, setIsLeoTalking] = useState(false);

  // 2. STATE: Mood Tracking
  const [currentMood, setCurrentMood] = useState<MoodEntry | null>(null);
  const [moodHistory, setMoodHistory] = useState<MoodEntry[]>([]);

  // 3. STATE: Chat History (for parent dashboard)
  const [chatHistory, setChatHistory] = useState<Message[]>([]);

  // 4. STATE: Parent Dashboard visibility
  const [showDashboard, setShowDashboard] = useState(false);

  // 5. STATE: Health Logs
  const [healthLogs, setHealthLogs] = useState<HealthLog[]>([]);

  // 6. STATE: Engagement Data
  const [engagementData, setEngagementData] = useState<EngagementData>({
    totalSessions: 0,
    currentStreak: 0,
    longestStreak: 0,
    avgMessagesPerDay: 0,
    lastActiveDate: null,
    dailyActivity: {}
  });

  // 7. STATE: Real-time health metrics from simulator
  const [healthMetrics, setHealthMetrics] = useState<HealthMetrics | null>(null);
  const [healthScore, setHealthScore] = useState<number>(75);
  const [safetyStatus, setSafetyStatus] = useState<string>('SAFE');
  const [healthEvents, setHealthEvents] = useState<HealthEvent[]>([]);
  const [simulatorAlerts, setSimulatorAlerts] = useState<SimulatorAlert[]>([]);

  // 8. STATE: Selected Child Profile
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);

  // 9. STATE: Kid Mode (simplified UI) vs Parent mode toggle (for quick access)
  const [isKidMode, setIsKidMode] = useState(true);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordInput, setPasswordInput] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [securityAnswer, setSecurityAnswer] = useState('');

  const PARENT_PASSWORD = "1234"; // Demo password
  const SECURITY_QUESTION = "What is Leo's favorite animal?";
  const SECURITY_ANSWER = "lion"; // Case insensitive

  const handleModeToggle = () => {
    if (isKidMode) {
      // Switching to parent mode - require password
      setShowPasswordModal(true);
      setPasswordInput('');
      setPasswordError('');
    } else {
      // Switching back to kid mode - no password needed
      setIsKidMode(true);
    }
  };

  const handlePasswordSubmit = () => {
    if (passwordInput === PARENT_PASSWORD) {
      setIsKidMode(false);
      setShowPasswordModal(false);
      setPasswordInput('');
      setPasswordError('');
      setShowForgotPassword(false);
    } else {
      setPasswordError('Incorrect password');
      setPasswordInput('');
    }
  };

  const handleSecurityAnswer = () => {
    if (securityAnswer.toLowerCase().trim() === SECURITY_ANSWER) {
      // Correct answer - show password and go back
      setPasswordError('');
      setShowForgotPassword(false);
      setSecurityAnswer('');
      alert(`Your password is: ${PARENT_PASSWORD}`);
    } else {
      setPasswordError('Incorrect answer. Try again!');
      setSecurityAnswer('');
    }
  };

  const handleClosePasswordModal = () => {
    setShowPasswordModal(false);
    setShowForgotPassword(false);
    setPasswordInput('');
    setSecurityAnswer('');
    setPasswordError('');
  };

  // 10. STATE: Medications (persisted)
  const [medications, setMedications] = useState<{ type: string; time: string; taken: boolean }[]>([]);

  // 11. STATE: Help popup visibility and Leo's worried expression
  const [showHelpPopup, setShowHelpPopup] = useState(false);
  const [leoWorried, setLeoWorried] = useState(false);

  // 12. STATE: SOS trigger counter - increments when SOS button is clicked
  const [sosTrigger, setSosTrigger] = useState(0);

  // 13. STATE: Vision Mode
  const [showVision, setShowVision] = useState(false);
  const [showScavengerHunt, setShowScavengerHunt] = useState(false);

  // Calculate engagement data from chat history
  const calculateEngagement = useCallback((messages: Message[]): EngagementData => {
    const days: Record<string, number> = {};
    const uniqueDates = new Set<string>();

    messages.forEach(msg => {
      if (msg.timestamp) {
        const date = new Date(msg.timestamp);
        const dateStr = date.toISOString().split('T')[0];
        const dayName = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()];

        uniqueDates.add(dateStr);
        days[dayName] = (days[dayName] || 0) + 1;
      }
    });

    // Calculate streak
    const sortedDates = Array.from(uniqueDates).sort().reverse();
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 0;

    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

    // Check if active today or yesterday to start counting streak
    if (sortedDates.includes(today) || sortedDates.includes(yesterday)) {
      for (let i = 0; i < sortedDates.length; i++) {
        const currentDate = new Date(sortedDates[i]);
        const prevDate = i > 0 ? new Date(sortedDates[i - 1]) : new Date();

        const diffDays = i === 0
          ? Math.floor((new Date().getTime() - currentDate.getTime()) / 86400000)
          : Math.floor((prevDate.getTime() - currentDate.getTime()) / 86400000);

        if (diffDays <= 1) {
          tempStreak++;
          currentStreak = tempStreak;
        } else {
          if (tempStreak > longestStreak) longestStreak = tempStreak;
          tempStreak = 1;
        }
      }
    }

    if (tempStreak > longestStreak) longestStreak = tempStreak;

    const totalDays = uniqueDates.size || 1;
    const avgMessages = messages.length / totalDays;

    return {
      totalSessions: uniqueDates.size,
      currentStreak,
      longestStreak: Math.max(longestStreak, currentStreak),
      avgMessagesPerDay: avgMessages,
      lastActiveDate: sortedDates[0] ? new Date(sortedDates[0]) : null,
      dailyActivity: days
    };
  }, []);

  // Load saved data from localStorage on mount
  useEffect(() => {
    try {
      const savedMoods = localStorage.getItem(MOOD_HISTORY_KEY);
      if (savedMoods) {
        const parsed = JSON.parse(savedMoods);
        if (Array.isArray(parsed)) {
          setMoodHistory(parsed);
        }
      }
    } catch (e) {
      console.log("Failed to load mood history");
    }

    try {
      const savedChats = localStorage.getItem(CHAT_HISTORY_KEY);
      if (savedChats) {
        const parsed = JSON.parse(savedChats);
        if (Array.isArray(parsed)) {
          setChatHistory(parsed);
          setEngagementData(calculateEngagement(parsed));
        }
      }
    } catch (e) {
      console.log("Failed to load chat history");
    }

    try {
      const savedHealthLogs = localStorage.getItem(HEALTH_LOGS_KEY);
      if (savedHealthLogs) {
        const parsed = JSON.parse(savedHealthLogs);
        if (Array.isArray(parsed)) {
          setHealthLogs(parsed);
        }
      }
    } catch (e) {
      console.log("Failed to load health logs");
    }

    try {
      const savedEngagement = localStorage.getItem(ENGAGEMENT_KEY);
      if (savedEngagement) {
        const parsed = JSON.parse(savedEngagement);
        if (parsed && typeof parsed === 'object') {
          setEngagementData(prev => ({ ...prev, ...parsed }));
        }
      }
    } catch (e) {
      console.log("Failed to load engagement data");
    }

    try {
      const savedMeds = localStorage.getItem(MEDICATIONS_KEY);
      if (savedMeds) {
        const parsed = JSON.parse(savedMeds);
        if (Array.isArray(parsed)) {
          setMedications(parsed);
        }
      }
    } catch (e) {
      console.log("Failed to load medications");
    }
  }, [calculateEngagement]);

  // 5. POLLING: Only fetch global stats when NO child is selected
  useEffect(() => {
    // Skip if a child is selected - child-specific polling handles it
    if (selectedChild) return;

    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/');
        const data = await res.json();
        setStats(data.stats);
      } catch (e) {
        console.log("Backend offline (Leo is sleeping)");
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, [selectedChild]);

  // 8. POLLING: Fetch health metrics from child-specific or global endpoints
  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        if (selectedChild) {
          // Fetch child's statistics (includes XP, level, health stats)
          const statsRes = await fetch(`http://localhost:8000/api/children/${selectedChild.id}/statistics`);
          if (statsRes.ok) {
            const data = await statsRes.json();

            // Update stats from child's actual data
            setStats({
              xp: data.xp ?? selectedChild.xp,
              level: data.level ?? selectedChild.level,
              status: data.danger_count > 0 ? 'Needs Help!' :
                data.monitor_count > 0 ? 'Check In' : 'Super Strong!'
            });

            // Update health score
            if (typeof data.avg_health_score === 'number') {
              setHealthScore(data.avg_health_score);
            }

            // Determine safety status from recent events
            if (data.danger_count > 0) {
              setSafetyStatus('DANGER');
            } else if (data.monitor_count > 0) {
              setSafetyStatus('MONITOR');
            } else {
              setSafetyStatus('SAFE');
            }
          }

          // Fetch child's history (for events and metrics)
          const historyRes = await fetch(`http://localhost:8000/api/children/${selectedChild.id}/history?limit=50`);
          if (historyRes.ok) {
            const data = await historyRes.json();
            if (data.events && Array.isArray(data.events)) {
              setHealthEvents(data.events);

              // Extract current metrics from recent events
              const metrics: HealthMetrics = {
                glucose: { value: 5.5, unit: 'mmol/L', status: 'normal' },
                heart_rate: { value: 85, unit: 'bpm', status: 'normal' },
                mood: { value: 0.7, unit: 'score', status: 'good' },
                activity: { value: 0.5, unit: 'score', status: 'moderate' },
                spo2: { value: 98, unit: '%', status: 'normal' },
                asthma_risk: { value: 0.2, unit: 'score', status: 'low' }
              };

              // Find most recent value for each metric type
              for (const event of data.events.slice().reverse()) {
                const type = event.type || '';
                if (type.includes('glucose') && metrics.glucose.value === 5.5) {
                  metrics.glucose = {
                    value: event.value,
                    unit: 'mmol/L',
                    status: event.value < 4 ? 'warning' : event.value > 9 ? 'elevated' : 'normal'
                  };
                }
                if (type.includes('heart') && metrics.heart_rate.value === 85) {
                  metrics.heart_rate = {
                    value: event.value,
                    unit: 'bpm',
                    status: event.value < 70 || event.value > 120 ? 'warning' : 'normal'
                  };
                }
                if (type.includes('mood') && metrics.mood.value === 0.7) {
                  metrics.mood = {
                    value: event.value,
                    unit: 'score',
                    status: event.value < 0.4 ? 'low' : event.value > 0.6 ? 'good' : 'neutral'
                  };
                }
                if (type.includes('oxygen') && metrics.spo2.value === 98) {
                  metrics.spo2 = {
                    value: event.value,
                    unit: '%',
                    status: event.value < 95 ? 'low' : 'normal'
                  };
                }
                if (type.includes('asthma') && metrics.asthma_risk.value === 0.2) {
                  metrics.asthma_risk = {
                    value: event.value,
                    unit: 'score',
                    status: event.value > 0.7 ? 'high' : event.value > 0.4 ? 'moderate' : 'low'
                  };
                }
                if (type.includes('activity') && metrics.activity.value === 0.5) {
                  metrics.activity = {
                    value: event.value,
                    unit: 'score',
                    status: event.value > 0.6 ? 'active' : event.value < 0.3 ? 'sedentary' : 'moderate'
                  };
                }
              }
              setHealthMetrics(metrics);

              // Update health logs
              const newLogs: HealthLog[] = data.events
                .filter((e: HealthEvent) => e && e.type && e.timestamp)
                .map((e: HealthEvent) => ({
                  metric_type: e.type,
                  value: e.value || 0,
                  unit: e.unit || '',
                  timestamp: new Date(e.timestamp)
                }));

              if (newLogs.length > 0) {
                setHealthLogs(newLogs);
              }
            }
          }

          // Fetch child's alerts
          const alertsRes = await fetch(`http://localhost:8000/api/children/${selectedChild.id}/alerts`);
          if (alertsRes.ok) {
            const data = await alertsRes.json();
            if (data.alerts && Array.isArray(data.alerts)) {
              setSimulatorAlerts(data.alerts);
            }
          }
        } else {
          // Fallback to global endpoints when no child selected
          const metricsRes = await fetch('http://localhost:8000/api/health/current');
          if (metricsRes.ok) {
            const data = await metricsRes.json();
            if (data.metrics) {
              setHealthMetrics(data.metrics);
            }
            if (typeof data.health_score === 'number') {
              setHealthScore(data.health_score);
            }
            if (data.safety_status) {
              setSafetyStatus(data.safety_status);
            }
          }

          const eventsRes = await fetch('http://localhost:8000/api/health/events?limit=20');
          if (eventsRes.ok) {
            const data = await eventsRes.json();
            if (data.events && Array.isArray(data.events)) {
              setHealthEvents(data.events);
            }
          }

          const alertsRes = await fetch('http://localhost:8000/api/health/alerts');
          if (alertsRes.ok) {
            const data = await alertsRes.json();
            if (data.alerts && Array.isArray(data.alerts)) {
              setSimulatorAlerts(data.alerts);
            }
          }
        }
      } catch (e) {
        console.log("Health data fetch failed:", e);
      }
    };

    fetchHealthData();
    // Poll every 2 seconds for real-time feel
    const interval = setInterval(fetchHealthData, 2000);
    return () => clearInterval(interval);
  }, [selectedChild]);

  // Handle child selection
  const handleChildSelect = (child: Child | null) => {
    setSelectedChild(child);
    if (child) {
      setStats({
        xp: child.xp,
        level: child.level,
        status: 'Loading...'
      });
    }
  };

  // Handle mood selection
  const handleMoodSelect = (entry: MoodEntry) => {
    setCurrentMood(entry);
    const updatedHistory = [...moodHistory, entry];
    setMoodHistory(updatedHistory);
    localStorage.setItem(MOOD_HISTORY_KEY, JSON.stringify(updatedHistory));
  };

  // Handle chat history updates
  const handleChatUpdate = useCallback((messages: Message[]) => {
    // PREVENT INFINITE LOOP: Only update if length changed or it's a new array reference that implies content change
    // Using length check is simple and effective for a chat log
    if (messages.length === chatHistory.length && messages.every((m, i) => m.text === chatHistory[i]?.text)) {
      return;
    }

    // Check if there's a new message from Leo to speak
    if (messages.length > chatHistory.length) {
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.role === 'assistant' && !isMuted) {
        speak(lastMsg.text);
      }
    }

    setChatHistory(messages);
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messages));

    // Update engagement data
    const newEngagement = calculateEngagement(messages);
    setEngagementData(newEngagement);
    localStorage.setItem(ENGAGEMENT_KEY, JSON.stringify(newEngagement));
  }, [chatHistory, isMuted, speak, calculateEngagement]);

  // Handle medication updates - now per-child
  const handleMedicationsUpdate = useCallback((meds: { type: string; time: string; taken: boolean }[]) => {
    setMedications(meds);
    // Save to child-specific key if child is selected
    const key = selectedChild ? `${MEDICATIONS_KEY}_${selectedChild.id}` : MEDICATIONS_KEY;
    localStorage.setItem(key, JSON.stringify(meds));
  }, [selectedChild]);

  // Load medications when child changes
  useEffect(() => {
    if (selectedChild) {
      const key = `${MEDICATIONS_KEY}_${selectedChild.id}`;
      try {
        const saved = localStorage.getItem(key);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed)) {
            setMedications(parsed);
            return;
          }
        }
      } catch (e) {
        console.log("Failed to load child medications");
      }
      // No saved medications for this child, reset to empty
      setMedications([]);
    }
  }, [selectedChild]);

  // Handle help keyword detection
  const handleHelpDetected = () => {
    setShowHelpPopup(true);
    setLeoWorried(true);
    // Reset Leo's expression after 5 seconds
    setTimeout(() => setLeoWorried(false), 5000);
  };



  return (
    <div className={`app-wrapper ${isKidMode ? 'kid-mode' : 'detail-mode'} ${showHelpPopup || leoWorried ? 'help-mode' : ''}`}>

      {/* --- VISION MODE --- */}
      {showVision && (
        <VisionMode
          onClose={() => setShowVision(false)}
          onObjectDetected={(detected) => {
            // If Leo sees something interesting, maybe he can say it?
            if (detected.length > 0 && !isMuted) {
              // Simple throttle could be added here to prevent spam
            }
          }}
        />
      )}

      {/* --- SCAVENGER HUNT MODE --- */}
      {showScavengerHunt && (
        <ScavengerHuntMode
          onClose={() => setShowScavengerHunt(false)}
          onAddXP={(amount) => {
            // 1. Optimistic UI update
            setStats(prev => ({ ...prev, xp: prev.xp + amount }));
            if (!isMuted) speak("Wow! You earned " + amount + " XP!");

            // 2. Persist to Backend
            if (selectedChild) {
              fetch(`http://localhost:8000/api/children/${selectedChild.id}/xp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount, reason: 'Scavenger Hunt' })
              }).catch(e => console.error("XP Save Failed", e));
            }
          }}
        />
      )}

      {/* --- FLOATING HELP BUTTON --- */}
      <button
        className="floating-help-btn"
        onClick={() => {
          setShowHelpPopup(true);
          setLeoWorried(true);
          setSosTrigger(prev => prev + 1); // Trigger Leo's response
          setTimeout(() => setLeoWorried(false), 5000);
        }}
        title="Need help?"
      >
        🆘
      </button>

      {/* --- HUD BAR (Top) --- */}
      <div className="status-hud">
        {/* Child Selector */}
        <ChildSelector
          onChildSelect={handleChildSelect}
          selectedChild={selectedChild}
          isKidMode={isKidMode}
        />

        {/* Kid-friendly stats - Combined Level & XP Progress */}
        {isKidMode && (
          <div className="xp-progress-container" title={`Level ${stats.level} - ${stats.xp} XP / ${stats.level * 100} XP`}>
            <div className="xp-info">
              <span className="level-badge">⭐ {stats.level}</span>
              <span className="xp-text">{stats.xp} / {stats.level * 100} XP</span>
            </div>
            <div className="xp-bar-bg">
              <div
                className="xp-bar-fill"
                style={{ width: `${Math.min(100, (stats.xp / (stats.level * 100)) * 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Mood status - always visible, updates when mood is selected */}
        <div className={`stat-pill status-pill ${currentMood ? 'status-mood' : safetyStatus === 'DANGER' ? 'status-danger' : safetyStatus === 'MONITOR' ? 'status-warn' : 'status-good'}`}>
          <span className="stat-icon">
            {currentMood?.mood || (safetyStatus === 'DANGER' ? '😟' : safetyStatus === 'MONITOR' ? '🤔' : '😊')}
          </span>
          <span className="stat-value">
            {currentMood?.label || (
              safetyStatus === 'DANGER' ? "Let's check!" :
                safetyStatus === 'MONITOR' ? 'Doing okay' :
                  'How are you?'
            )}
          </span>
        </div>

        {/* Streak - show only in kid mode */}
        {isKidMode && (engagementData.currentStreak > 0 || (selectedChild?.streak || 0) > 0) && (
          <div className="stat-pill streak-pill">
            🔥 {engagementData.currentStreak || selectedChild?.streak || 0} day{(engagementData.currentStreak || selectedChild?.streak || 0) !== 1 ? 's' : ''}!
          </div>
        )}

        {/* Health score - only in detail mode */}
        {!isKidMode && (
          <div className="stat-pill health-pill">
            🩺 {healthScore.toFixed(0)}
          </div>
        )}

        {/* Mode Toggle - switches between kid and parent mode */}
        <button
          className={`mode-toggle-btn ${isKidMode ? 'kid' : 'parent'}`}
          onClick={handleModeToggle}
          title={isKidMode ? 'Switch to Parent Mode' : 'Switch to Kid Mode'}
        >
          {isKidMode ? '🔒' : '🧒'}
          <span>{isKidMode ? 'Parent Mode' : 'Kid Mode'}</span>
        </button>

        {/* Parent Dashboard Button - REMOVED FROM HUD (Moved to Bottom Left) */}

        {/* Vision Mode Button - HIDDEN IN KID MODE AS REQUESTED */}
        {!isKidMode && (
          <button
            className="mode-toggle-btn vision-btn"
            onClick={() => setShowVision(true)}
            title="Enable Leo Vision"
          >
            👁️
            <span>Leo Vision</span>
          </button>
        )}

        {/* Scavenger Hunt Button */}
        {isKidMode && (
          <button
            className="mode-toggle-btn game-btn"
            onClick={() => setShowScavengerHunt(true)}
            title="Play Scavenger Hunt"
            style={{ marginLeft: '10px', background: 'linear-gradient(45deg, #FFD700, #FFA500)', color: '#000' }}
          >
            🕵️‍♂️
            <span>Hunt</span>
          </button>
        )}

        {/* Sound Toggle (Moved to end) */}
        <button
          className="mode-toggle-btn sound-btn"
          onClick={toggleMute}
          title={isMuted ? "Unmute Leo" : "Mute Leo"}
          style={{ marginLeft: '10px' }}
        >
          {isMuted ? '🔇' : '🔊'}
        </button>
      </div>

      {/* --- REAL-TIME HEALTH ALERT BANNER (kid-friendly) --- */}
      {safetyStatus === 'DANGER' && (
        <div className="health-alert-banner">
          {isKidMode ? (
            <>
              <span className="alert-emoji">🦁</span>
              <span>Hey {selectedChild?.name || 'friend'}! Leo wants to check on you!</span>
            </>
          ) : (
            <>🚨 Health Alert: {simulatorAlerts[0]?.message || 'Attention needed'}</>
          )}
        </div>
      )}

      {/* --- ENCOURAGEMENT BANNER (for kids) --- */}
      {isKidMode && safetyStatus === 'SAFE' && stats.level >= 2 && (
        <div className="encouragement-banner">
          <span>🌟</span>
          <span>You're doing amazing, {selectedChild?.name || 'superstar'}! Keep it up!</span>
          <span>🌟</span>
        </div>
      )}

      {/* --- MAIN GAME SCENE --- */}
      <main className="game-scene">

        {/* LEFT: The Avatar */}
        <div className="avatar-zone">
          <LeoAvatar isSpeaking={isLeoTalking} isWorried={leoWorried} />

          {/* Thought of the Day - below avatar */}
          {isKidMode && (
            <div className="kid-health-display thought-of-day">
              <div className="paw-icon">🐾</div>
              <span className="health-text">
                {THOUGHTS_OF_THE_DAY[Math.floor(new Date().getTime() / (1000 * 60 * 60 * 24)) % THOUGHTS_OF_THE_DAY.length]}
              </span>
              <div className="paw-icon">🐾</div>
            </div>
          )}

          {/* Detailed Health Metrics Display (for detail mode) */}
          {!isKidMode && healthMetrics && (
            <div className="health-mini-display">
              <div className="mini-metric">
                <span className="mini-icon">🍎</span>
                <span className="mini-value">
                  {typeof healthMetrics.glucose?.value === 'number'
                    ? healthMetrics.glucose.value.toFixed(1)
                    : '--'}
                </span>
                <span className="mini-unit">mmol/L</span>
              </div>
              <div className="mini-metric">
                <span className="mini-icon">❤️</span>
                <span className="mini-value">
                  {typeof healthMetrics.heart_rate?.value === 'number'
                    ? healthMetrics.heart_rate.value.toFixed(0)
                    : '--'}
                </span>
                <span className="mini-unit">bpm</span>
              </div>
              <div className="mini-metric">
                <span className="mini-icon">🫁</span>
                <span className="mini-value">
                  {typeof healthMetrics.spo2?.value === 'number'
                    ? healthMetrics.spo2.value.toFixed(0)
                    : '--'}
                </span>
                <span className="mini-unit">%</span>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: Chat & Mood */}
        <div className="chat-zone">
          {/* 😊 Mood Tracker - only show in kid mode */}
          {isKidMode && (
            <MoodTracker
              onMoodSelect={handleMoodSelect}
              currentMood={currentMood}
            />
          )}
          {/* 🗣️ ChatBox tells App when it starts/stops typing */}
          <ChatBox
            onSpeakingStateChange={setIsLeoTalking}
            onChatUpdate={handleChatUpdate}
            currentMood={currentMood}
            onHelpDetected={handleHelpDetected}
            sosTrigger={sosTrigger}
            isKidMode={isKidMode}
            childName={selectedChild?.name}
            childId={selectedChild?.id}
            childCondition={selectedChild?.condition}
            childAge={selectedChild?.age}
            onMessageComplete={(msg) => {
              if (!isMuted) {
                speak(msg);
              }
            }}
          />
        </div>

      </main>

      {/* --- PARENT DASHBOARD (Modal) --- */}
      {showDashboard && (
        <ParentDashboard
          selectedChild={selectedChild}
          chatHistory={chatHistory}
          moodHistory={moodHistory}
          healthLogs={healthLogs}
          engagementData={engagementData}
          healthMetrics={healthMetrics}
          healthScore={healthScore}
          safetyStatus={safetyStatus}
          healthEvents={healthEvents}
          simulatorAlerts={simulatorAlerts}
          medications={medications}
          onMedicationsUpdate={handleMedicationsUpdate}
          onClose={() => setShowDashboard(false)}
        />
      )}

      {/* --- HELP POPUP --- */}
      {showHelpPopup && (
        <div className="help-popup-overlay" onClick={() => setShowHelpPopup(false)}>
          <div className="help-popup" onClick={e => e.stopPropagation()}>
            <div className="help-popup-header">
              <span className="help-icon">🆘</span>
              <h3>Need Help?</h3>
              <button className="help-close" onClick={() => setShowHelpPopup(false)}>×</button>
            </div>
            <div className="help-popup-content">
              <p>If you need help, please call:</p>
              <a href="tel:+17807094350" className="help-number">
                📞 +1 (780) 709-4350
              </a>
              <div className="help-divider">or</div>
              <a href="tel:911" className="emergency-number">
                🚨 Emergency: 911
              </a>
              <p className="help-note">A grown-up can help you!</p>
            </div>
          </div>
        </div>
      )}

      {/* Password Modal for Parent Mode */}
      {showPasswordModal && (
        <div className="password-modal-overlay" onClick={handleClosePasswordModal}>
          <div className="password-modal" onClick={e => e.stopPropagation()}>
            <div className="password-header">
              <span>{showForgotPassword ? '🤔' : '🔐'}</span>
              <h3>{showForgotPassword ? 'Forgot Password' : 'Parent Access'}</h3>
              <button className="password-close" onClick={handleClosePasswordModal}>×</button>
            </div>
            <div className="password-content">
              {!showForgotPassword ? (
                <>
                  <p>Enter password to access Parent Mode</p>
                  <input
                    type="password"
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handlePasswordSubmit()}
                    placeholder="Enter password..."
                    autoFocus
                  />
                  {passwordError && <div className="password-error">{passwordError}</div>}
                  <button className="password-submit" onClick={handlePasswordSubmit}>
                    Unlock 🔓
                  </button>
                  <button
                    className="forgot-password-link"
                    onClick={() => {
                      setShowForgotPassword(true);
                      setPasswordError('');
                    }}
                  >
                    Forgot Password?
                  </button>
                </>
              ) : (
                <>
                  <p className="security-question">🦁 {SECURITY_QUESTION}</p>
                  <input
                    type="text"
                    value={securityAnswer}
                    onChange={(e) => setSecurityAnswer(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSecurityAnswer()}
                    placeholder="Your answer..."
                    autoFocus
                  />
                  {passwordError && <div className="password-error">{passwordError}</div>}
                  <button className="password-submit" onClick={handleSecurityAnswer}>
                    Verify Answer ✓
                  </button>
                  <button
                    className="forgot-password-link"
                    onClick={() => {
                      setShowForgotPassword(false);
                      setPasswordError('');
                      setSecurityAnswer('');
                    }}
                  >
                    ← Back to Login
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
      {/* --- PARENT BUTTON (Fixed Bottom Left) --- */}
      {!isKidMode && (
        <button className="fixed-parent-btn" onClick={() => setShowDashboard(true)}>
          🔒 Parent Mode
        </button>
      )}

    </div>
  );
}

export default App;
