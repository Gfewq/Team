import { useState, useEffect, useCallback } from 'react';
import ChatBox from './components/ChatBox';
import LeoAvatar from './components/LeoAvatar'; 
import MoodTracker, { MoodEntry } from './components/MoodTracker';
import ParentDashboard from './components/ParentDashboard';
import './App.css';

// 📊 Define the shape of our data (Matches Python Backend)
interface UserStats {
  xp: number;
  level: number;
  status: string;
}

interface Message {
  role: string;
  text: string;
  timestamp?: Date;
}

interface HealthLog {
  metric_type: string;
  value: number;
  unit: string;
  timestamp: Date;
}

interface HealthMetric {
  value: number;
  unit: string;
  status: string;
}

interface HealthMetrics {
  glucose: HealthMetric;
  heart_rate: HealthMetric;
  mood: HealthMetric;
  activity: HealthMetric;
  spo2: HealthMetric;
  asthma_risk: HealthMetric;
}

interface HealthEvent {
  id: string;
  type: string;
  value: number;
  unit: string;
  urgency: string;
  safety_status: string;
  health_score: number;
  anomaly_score: number;
  trend: string;
  reasoning: string;
  timestamp: string;
  correlations: string[];
}

interface SimulatorAlert {
  id: string;
  type: string;
  value: number;
  unit: string;
  severity: string;
  message: string;
  timestamp: string;
  health_score: number;
  urgency: string;
}

interface EngagementData {
  totalSessions: number;
  currentStreak: number;
  longestStreak: number;
  avgMessagesPerDay: number;
  lastActiveDate: Date | null;
  dailyActivity: Record<string, number>;
}

// LocalStorage keys
const MOOD_HISTORY_KEY = 'leo_mood_history';
const CHAT_HISTORY_KEY = 'leo_chat_history';
const HEALTH_LOGS_KEY = 'leo_health_logs';
const ENGAGEMENT_KEY = 'leo_engagement';

function App() {
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
  }, [calculateEngagement]);

  // 5. POLLING: Check the backend every 2 seconds for Health/XP updates
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/'); 
        const data = await res.json();
        setStats(data.stats);
      } catch (e) {
        console.log("Backend offline (Leo is sleeping)");
      }
    };
    
    fetchStats(); // Run once immediately
    const interval = setInterval(fetchStats, 2000); // Run every 2s
    return () => clearInterval(interval);
  }, []);

  // 8. POLLING: Fetch health metrics from simulator
  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        // Fetch current health metrics
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

        // Fetch recent health events
        const eventsRes = await fetch('http://localhost:8000/api/health/events?limit=20');
        if (eventsRes.ok) {
          const data = await eventsRes.json();
          if (data.events && Array.isArray(data.events)) {
            setHealthEvents(data.events);
            
            // Convert simulator events to health logs for the dashboard
            const newLogs: HealthLog[] = data.events
              .filter((e: HealthEvent) => e && e.type && e.timestamp)
              .map((e: HealthEvent) => ({
                metric_type: e.type,
                value: e.value || 0,
                unit: e.unit || '',
                timestamp: new Date(e.timestamp)
              }));
            
            if (newLogs.length > 0) {
              setHealthLogs(prev => {
                // Merge new logs, avoiding duplicates
                const existingIds = new Set(prev.map(l => l.timestamp.toString()));
                const uniqueNew = newLogs.filter(l => !existingIds.has(l.timestamp.toString()));
                return [...prev, ...uniqueNew].slice(-100); // Keep last 100
              });
            }
          }
        }

        // Fetch alerts
        const alertsRes = await fetch('http://localhost:8000/api/health/alerts');
        if (alertsRes.ok) {
          const data = await alertsRes.json();
          if (data.alerts && Array.isArray(data.alerts)) {
            setSimulatorAlerts(data.alerts);
          }
        }
      } catch (e) {
        console.log("Health data fetch failed:", e);
      }
    };

    fetchHealthData();
    const interval = setInterval(fetchHealthData, 3000); // Every 3s
    return () => clearInterval(interval);
  }, []);

  // Handle mood selection
  const handleMoodSelect = (entry: MoodEntry) => {
    setCurrentMood(entry);
    const updatedHistory = [...moodHistory, entry];
    setMoodHistory(updatedHistory);
    localStorage.setItem(MOOD_HISTORY_KEY, JSON.stringify(updatedHistory));
  };

  // Handle chat history updates
  const handleChatUpdate = (messages: Message[]) => {
    setChatHistory(messages);
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messages));
    
    // Update engagement data
    const newEngagement = calculateEngagement(messages);
    setEngagementData(newEngagement);
    localStorage.setItem(ENGAGEMENT_KEY, JSON.stringify(newEngagement));
  };

  // 6. LOGIC: Determine Status Color
  const getStatusClass = () => {
    if (safetyStatus === 'DANGER') return 'status-danger';
    if (safetyStatus === 'MONITOR') return 'status-warn';
    if (stats.status && (stats.status.includes('Help') || stats.status.includes('Check'))) return 'status-warn';
    return 'status-good';
  };

  // Get display status
  const getDisplayStatus = () => {
    if (safetyStatus === 'DANGER') return '⚠️ Alert';
    if (safetyStatus === 'MONITOR') return '👀 Monitor';
    return stats.status || 'Loading...';
  };

  return (
    <div className="app-wrapper">
      {/* --- HUD BAR (Top) --- */}
      <div className="status-hud">
        <div className="stat-pill">⭐ Level {stats.level}</div>
        <div className="stat-pill">✨ {stats.xp} XP</div>
        <div className={`stat-pill ${getStatusClass()}`}>
          ❤️ {getDisplayStatus()}
        </div>
        {healthMetrics && (
          <div className="stat-pill health-pill">
            🩺 {healthScore.toFixed(0)}
          </div>
        )}
        {engagementData.currentStreak > 0 && (
          <div className="stat-pill streak-pill">
            🔥 {engagementData.currentStreak} day streak
          </div>
        )}
        <button className="parent-btn" onClick={() => setShowDashboard(true)}>
          👨‍👩‍👧 Parent View
        </button>
      </div>

      {/* --- REAL-TIME HEALTH ALERT BANNER --- */}
      {safetyStatus === 'DANGER' && (
        <div className="health-alert-banner">
          🚨 Health Alert: {simulatorAlerts[0]?.message || 'Attention needed'}
        </div>
      )}

      {/* --- MAIN GAME SCENE --- */}
      <main className="game-scene">
        
        {/* LEFT: The Avatar */}
        <div className="avatar-zone">
          {/* 🦁 Pass the speaking state so his mouth moves! */}
          <LeoAvatar isSpeaking={isLeoTalking} />
          
          {/* Health Metrics Mini Display */}
          {healthMetrics && healthMetrics.glucose && healthMetrics.heart_rate && healthMetrics.spo2 && (
            <div className="health-mini-display">
              <div className="mini-metric">
                <span className="mini-icon">🍎</span>
                <span className="mini-value">{healthMetrics.glucose.value?.toFixed(1) || '--'}</span>
                <span className="mini-unit">mmol/L</span>
              </div>
              <div className="mini-metric">
                <span className="mini-icon">❤️</span>
                <span className="mini-value">{healthMetrics.heart_rate.value?.toFixed(0) || '--'}</span>
                <span className="mini-unit">bpm</span>
              </div>
              <div className="mini-metric">
                <span className="mini-icon">🫁</span>
                <span className="mini-value">{healthMetrics.spo2.value?.toFixed(0) || '--'}</span>
                <span className="mini-unit">%</span>
              </div>
            </div>
          )}
        </div>
        
        {/* RIGHT: Chat & Mood */}
        <div className="chat-zone">
          {/* 😊 Mood Tracker */}
          <MoodTracker 
            onMoodSelect={handleMoodSelect} 
            currentMood={currentMood}
          />
          {/* 🗣️ ChatBox tells App when it starts/stops typing */}
          <ChatBox 
            onSpeakingStateChange={setIsLeoTalking}
            onChatUpdate={handleChatUpdate}
            currentMood={currentMood}
          />
        </div>

      </main>

      {/* --- PARENT DASHBOARD (Modal) --- */}
      {showDashboard && (
        <ParentDashboard
          chatHistory={chatHistory}
          moodHistory={moodHistory}
          healthLogs={healthLogs}
          engagementData={engagementData}
          healthMetrics={healthMetrics}
          healthScore={healthScore}
          safetyStatus={safetyStatus}
          healthEvents={healthEvents}
          simulatorAlerts={simulatorAlerts}
          onClose={() => setShowDashboard(false)}
        />
      )}
    </div>
  );
}

export default App;
