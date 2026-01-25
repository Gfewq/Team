import { useMemo, useState, useEffect } from 'react';
import { MoodEntry } from './MoodTracker';
import { Child } from './ChildSelector';
import './ParentDashboard.css';

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

interface ParentDashboardProps {
  selectedChild: Child | null;
  chatHistory: Message[];
  moodHistory: MoodEntry[];
  healthLogs?: HealthLog[];
  engagementData?: EngagementData;
  healthMetrics?: HealthMetrics | null;
  healthScore?: number;
  safetyStatus?: string;
  healthEvents?: HealthEvent[];
  simulatorAlerts?: SimulatorAlert[];
  medications?: {type: string; time: string; taken: boolean}[];
  onMedicationsUpdate?: (meds: {type: string; time: string; taken: boolean}[]) => void;
  onClose: () => void;
}

export default function ParentDashboard({ 
  selectedChild,
  chatHistory, 
  moodHistory, 
  healthLogs = [],
  engagementData,
  healthMetrics: initialMetrics,
  healthScore: initialScore = 75,
  safetyStatus: initialStatus = 'SAFE',
  healthEvents: initialEvents = [],
  simulatorAlerts: initialAlerts = [],
  medications = [],
  onMedicationsUpdate,
  onClose 
}: ParentDashboardProps) {
  
  const [activeTab, setActiveTab] = useState<'overview' | 'health' | 'medications'>('overview');
  const [medicationsDue, setMedicationsDue] = useState<{type: string; time: string; taken: boolean}[]>(medications);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  
  // Live data state - poll directly from API
  const [liveMetrics, setLiveMetrics] = useState<HealthMetrics | null>(initialMetrics || null);
  const [liveScore, setLiveScore] = useState(initialScore);
  const [liveStatus, setLiveStatus] = useState(initialStatus);
  const [liveEvents, setLiveEvents] = useState<HealthEvent[]>(initialEvents);
  const [liveAlerts, setLiveAlerts] = useState<SimulatorAlert[]>(initialAlerts);

  // Poll for live data
  useEffect(() => {
    if (!selectedChild) return;

    const fetchLiveData = async () => {
      try {
        // Fetch statistics
        const statsRes = await fetch(`http://localhost:8000/api/children/${selectedChild.id}/statistics`);
        if (statsRes.ok) {
          const data = await statsRes.json();
          if (typeof data.avg_health_score === 'number') {
            setLiveScore(data.avg_health_score);
          }
          if (data.danger_count > 0) {
            setLiveStatus('DANGER');
          } else if (data.monitor_count > 0) {
            setLiveStatus('MONITOR');
          } else {
            setLiveStatus('SAFE');
          }
        }

        // Fetch history for events and metrics
        const historyRes = await fetch(`http://localhost:8000/api/children/${selectedChild.id}/history?limit=50`);
        if (historyRes.ok) {
          const data = await historyRes.json();
          if (data.events && Array.isArray(data.events)) {
            setLiveEvents(data.events);
            
            // Extract LATEST metrics from events (sorted by timestamp, most recent first)
            const sortedEvents = [...data.events].sort((a, b) => 
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
            );
            
            // Default metrics
            const metrics: HealthMetrics = {
              glucose: { value: 5.5, unit: 'mmol/L', status: 'normal' },
              heart_rate: { value: 85, unit: 'bpm', status: 'normal' },
              mood: { value: 0.7, unit: 'score', status: 'good' },
              activity: { value: 0.5, unit: 'score', status: 'moderate' },
              spo2: { value: 98, unit: '%', status: 'normal' },
              asthma_risk: { value: 0.2, unit: 'score', status: 'low' }
            };
            
            // Track which metrics we've found (only use most recent)
            const found = { glucose: false, heart: false, mood: false, oxygen: false, asthma: false, activity: false };
            
            for (const event of sortedEvents) {
              const type = (event.type || event.event_type || '').toLowerCase();
              const value = event.value;
              
              if (!found.glucose && (type.includes('glucose') || type.includes('blood_sugar'))) {
                found.glucose = true;
                metrics.glucose = {
                  value: typeof value === 'number' ? value : 5.5,
                  unit: 'mmol/L',
                  status: value < 4 ? 'low' : value > 10 ? 'high' : value > 7 ? 'elevated' : 'normal'
                };
              }
              if (!found.heart && (type.includes('heart') || type.includes('pulse') || type.includes('hr'))) {
                found.heart = true;
                metrics.heart_rate = {
                  value: typeof value === 'number' ? Math.round(value) : 85,
                  unit: 'bpm',
                  status: value < 60 || value > 120 ? 'warning' : 'normal'
                };
              }
              if (!found.mood && type.includes('mood')) {
                found.mood = true;
                const moodVal = typeof value === 'number' ? value : 0.5;
                metrics.mood = {
                  value: Math.round(moodVal * 100),
                  unit: '%',
                  status: moodVal < 0.4 ? 'low' : moodVal > 0.6 ? 'good' : 'neutral'
                };
              }
              if (!found.oxygen && (type.includes('oxygen') || type.includes('spo2') || type.includes('saturation'))) {
                found.oxygen = true;
                metrics.spo2 = {
                  value: typeof value === 'number' ? Math.round(value) : 98,
                  unit: '%',
                  status: value < 95 ? 'low' : 'normal'
                };
              }
              if (!found.asthma && type.includes('asthma')) {
                found.asthma = true;
                const riskVal = typeof value === 'number' ? value : 0.2;
                metrics.asthma_risk = {
                  value: riskVal,
                  unit: 'score',
                  status: riskVal > 0.7 ? 'high' : riskVal > 0.4 ? 'moderate' : 'low'
                };
              }
              if (!found.activity && type.includes('activity')) {
                found.activity = true;
                const actVal = typeof value === 'number' ? value : 0.5;
                metrics.activity = {
                  value: Math.round(actVal * 100),
                  unit: '%',
                  status: actVal > 0.6 ? 'active' : actVal < 0.3 ? 'sedentary' : 'moderate'
                };
              }
            }
            setLiveMetrics(metrics);
          }
        }

        // Fetch alerts
        const alertsRes = await fetch(`http://localhost:8000/api/children/${selectedChild.id}/alerts`);
        if (alertsRes.ok) {
          const data = await alertsRes.json();
          if (data.alerts && Array.isArray(data.alerts)) {
            setLiveAlerts(data.alerts);
          }
        }

        setLastRefresh(new Date());
      } catch (e) {
        console.log("Dashboard poll failed:", e);
      }
    };

    fetchLiveData();
    const interval = setInterval(fetchLiveData, 2000);
    return () => clearInterval(interval);
  }, [selectedChild]);

  // Sync medications with parent
  useEffect(() => {
    if (onMedicationsUpdate && medicationsDue !== medications) {
      onMedicationsUpdate(medicationsDue);
    }
  }, [medicationsDue]);

  // Load medications from props on mount
  useEffect(() => {
    if (medications.length > 0 && medicationsDue.length === 0) {
      setMedicationsDue(medications);
    }
  }, [medications]);

  // Check for medication events
  useEffect(() => {
    const medEvents = liveEvents.filter(e => e.type?.includes('medication'));
    if (medEvents.length > 0) {
      setMedicationsDue(prev => {
        const existing = new Set(prev.map(m => m.time));
        const newMeds = medEvents
          .filter(e => !existing.has(e.timestamp))
          .map(e => ({
            type: 'Insulin',
            time: e.timestamp,
            taken: false
          }));
        return [...prev, ...newMeds].slice(-10);
      });
    }
  }, [liveEvents]);

  // Mark medication as taken
  const markMedicationTaken = async (index: number) => {
    setMedicationsDue(prev => 
      prev.map((m, i) => i === index ? { ...m, taken: true } : m)
    );
  };

  // Get current metrics with proper defaults - USE LIVE DATA
  const currentMetrics = useMemo(() => {
    if (liveMetrics) {
      return {
        glucose: liveMetrics.glucose?.value ?? '--',
        glucoseStatus: liveMetrics.glucose?.status ?? 'normal',
        heartRate: liveMetrics.heart_rate?.value ?? '--',
        heartRateStatus: liveMetrics.heart_rate?.status ?? 'normal',
        spo2: liveMetrics.spo2?.value ?? '--',
        spo2Status: liveMetrics.spo2?.status ?? 'normal',
        mood: liveMetrics.mood?.value ?? '--',
        moodStatus: liveMetrics.mood?.status ?? 'neutral',
        activity: liveMetrics.activity?.value ?? '--',
        activityStatus: liveMetrics.activity?.status ?? 'moderate',
        asthmaRisk: liveMetrics.asthma_risk?.value ?? '--',
        asthmaStatus: liveMetrics.asthma_risk?.status ?? 'low'
      };
    }
    return null;
  }, [liveMetrics]);

  // Calculate real stats from events - USE LIVE DATA
  const eventStats = useMemo(() => {
    const total = liveEvents.length;
    const danger = liveEvents.filter(e => e.safety_status === 'DANGER').length;
    const monitor = liveEvents.filter(e => e.safety_status === 'MONITOR').length;
    const safe = liveEvents.filter(e => e.safety_status === 'SAFE').length;
    
    const glucoseEvents = liveEvents.filter(e => e.type?.includes('glucose'));
    const avgGlucose = glucoseEvents.length > 0 
      ? glucoseEvents.reduce((sum, e) => sum + e.value, 0) / glucoseEvents.length 
      : 5.5;
    
    const hrEvents = liveEvents.filter(e => e.type?.includes('heart'));
    const avgHR = hrEvents.length > 0
      ? hrEvents.reduce((sum, e) => sum + e.value, 0) / hrEvents.length
      : 85;

    return { total, danger, monitor, safe, avgGlucose, avgHR };
  }, [liveEvents]);

  // Get mood stats
  const moodStats = useMemo(() => {
    const last7Days = moodHistory.filter(entry => {
      const entryDate = new Date(entry.timestamp);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return entryDate >= weekAgo;
    });

    const moodCounts: Record<string, number> = {};
    last7Days.forEach(entry => {
      moodCounts[entry.mood] = (moodCounts[entry.mood] || 0) + 1;
    });

    return { total: last7Days.length, counts: moodCounts };
  }, [moodHistory]);

  // Get status color
  const getStatusColor = (status: string) => {
    if (status === 'DANGER' || status === 'warning' || status === 'low' || status === 'high') return '#ff7675';
    if (status === 'MONITOR' || status === 'elevated' || status === 'moderate') return '#fdcb6e';
    return '#00b894';
  };

  // Format event type
  const formatEventType = (type: string) => {
    return type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'Unknown';
  };

  // Format time ago
  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="dashboard-overlay">
      <div className="dashboard-container">
        {/* Header */}
        <div className="dashboard-header">
          <div className="header-left">
            <h1>📊 Parent Dashboard</h1>
            {selectedChild && (
              <span className="child-name-badge">
                {selectedChild.name} (Age {selectedChild.age})
              </span>
            )}
          </div>
          <div className="header-right">
            <div 
              className="safety-badge"
              style={{ backgroundColor: getStatusColor(liveStatus) }}
            >
              {liveStatus === 'DANGER' ? '🚨' : liveStatus === 'MONITOR' ? '👀' : '✓'} {liveStatus}
            </div>
            <span className="last-update">Updated: {lastRefresh.toLocaleTimeString()}</span>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
        </div>

        {/* Tabs */}
        <div className="tab-navigation">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📈 Live Metrics
          </button>
          <button 
            className={`tab-btn ${activeTab === 'health' ? 'active' : ''}`}
            onClick={() => setActiveTab('health')}
          >
            📋 Event History
          </button>
          <button 
            className={`tab-btn ${activeTab === 'medications' ? 'active' : ''}`}
            onClick={() => setActiveTab('medications')}
          >
            💊 Medications
            {medicationsDue.filter(m => !m.taken).length > 0 && (
              <span className="med-badge">{medicationsDue.filter(m => !m.taken).length}</span>
            )}
          </button>
        </div>

        {/* Overview Tab - Live Metrics */}
        {activeTab === 'overview' && (
          <div className="dashboard-content">
            {/* Health Score Banner */}
            <div className="health-score-banner">
              <div className="score-circle" style={{ 
                background: `conic-gradient(${getStatusColor(liveStatus)} ${liveScore * 3.6}deg, #e0e0e0 0deg)`
              }}>
                <div className="score-inner">
                  <span className="score-value">{liveScore.toFixed(0)}</span>
                </div>
              </div>
              <div className="score-info">
                <h2>Health Score</h2>
                <p>Based on {eventStats.total} recent events</p>
                <div className="score-breakdown">
                  <span className="breakdown-item safe">✓ {eventStats.safe} Safe</span>
                  <span className="breakdown-item monitor">👀 {eventStats.monitor} Monitor</span>
                  <span className="breakdown-item danger">⚠ {eventStats.danger} Alerts</span>
                </div>
              </div>
            </div>

            {/* Live Metrics Grid */}
            {currentMetrics && (
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-icon">🍎</div>
                  <div className="metric-info">
                    <span className="metric-label">Glucose</span>
                    <span className="metric-value" style={{ color: getStatusColor(currentMetrics.glucoseStatus) }}>
                      {typeof currentMetrics.glucose === 'number' ? currentMetrics.glucose.toFixed(1) : currentMetrics.glucose}
                    </span>
                    <span className="metric-unit">mmol/L</span>
                  </div>
                  <div className={`metric-status ${currentMetrics.glucoseStatus}`}>
                    {currentMetrics.glucoseStatus}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">❤️</div>
                  <div className="metric-info">
                    <span className="metric-label">Heart Rate</span>
                    <span className="metric-value" style={{ color: getStatusColor(currentMetrics.heartRateStatus) }}>
                      {typeof currentMetrics.heartRate === 'number' ? currentMetrics.heartRate.toFixed(0) : currentMetrics.heartRate}
                    </span>
                    <span className="metric-unit">bpm</span>
                  </div>
                  <div className={`metric-status ${currentMetrics.heartRateStatus}`}>
                    {currentMetrics.heartRateStatus}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">🫁</div>
                  <div className="metric-info">
                    <span className="metric-label">SpO2</span>
                    <span className="metric-value" style={{ color: getStatusColor(currentMetrics.spo2Status) }}>
                      {typeof currentMetrics.spo2 === 'number' ? currentMetrics.spo2.toFixed(0) : currentMetrics.spo2}
                    </span>
                    <span className="metric-unit">%</span>
                  </div>
                  <div className={`metric-status ${currentMetrics.spo2Status}`}>
                    {currentMetrics.spo2Status}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">😊</div>
                  <div className="metric-info">
                    <span className="metric-label">Mood</span>
                    <span className="metric-value" style={{ color: getStatusColor(currentMetrics.moodStatus) }}>
                      {typeof currentMetrics.mood === 'number' ? (currentMetrics.mood * 100).toFixed(0) + '%' : currentMetrics.mood}
                    </span>
                    <span className="metric-unit">score</span>
                  </div>
                  <div className={`metric-status ${currentMetrics.moodStatus}`}>
                    {currentMetrics.moodStatus}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">🏃</div>
                  <div className="metric-info">
                    <span className="metric-label">Activity</span>
                    <span className="metric-value">
                      {typeof currentMetrics.activity === 'number' ? (currentMetrics.activity * 100).toFixed(0) + '%' : currentMetrics.activity}
                    </span>
                    <span className="metric-unit">score</span>
                  </div>
                  <div className={`metric-status ${currentMetrics.activityStatus}`}>
                    {currentMetrics.activityStatus}
                  </div>
                </div>

                {selectedChild?.condition !== 'diabetes' && (
                  <div className="metric-card">
                    <div className="metric-icon">🌬️</div>
                    <div className="metric-info">
                      <span className="metric-label">Asthma Risk</span>
                      <span className="metric-value" style={{ color: getStatusColor(currentMetrics.asthmaStatus) }}>
                        {typeof currentMetrics.asthmaRisk === 'number' ? (currentMetrics.asthmaRisk * 100).toFixed(0) + '%' : currentMetrics.asthmaRisk}
                      </span>
                      <span className="metric-unit">risk</span>
                    </div>
                    <div className={`metric-status ${currentMetrics.asthmaStatus}`}>
                      {currentMetrics.asthmaStatus}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Alerts */}
            {liveAlerts.length > 0 && (
              <div className="alerts-section">
                <h3>⚠️ Recent Alerts</h3>
                <div className="alerts-list">
                  {liveAlerts.slice(0, 5).map((alert, i) => (
                    <div key={i} className={`alert-item ${alert.severity}`}>
                      <span className="alert-icon">
                        {alert.severity === 'critical' ? '🔴' : '🟡'}
                      </span>
                      <div className="alert-content">
                        <span className="alert-type">{formatEventType(alert.type)}</span>
                        <span className="alert-message">{alert.message}</span>
                      </div>
                      <span className="alert-time">{formatTimeAgo(alert.timestamp)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Child Stats */}
            {selectedChild && (
              <div className="child-stats-section">
                <h3>🎮 {selectedChild.name}'s Progress</h3>
                <div className="stats-row">
                  <div className="stat-box">
                    <span className="stat-icon">⭐</span>
                    <span className="stat-value">{selectedChild.level}</span>
                    <span className="stat-label">Level</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-icon">✨</span>
                    <span className="stat-value">{selectedChild.xp}</span>
                    <span className="stat-label">XP</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-icon">🔥</span>
                    <span className="stat-value">{selectedChild.streak}</span>
                    <span className="stat-label">Streak</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-icon">💬</span>
                    <span className="stat-value">{chatHistory.length}</span>
                    <span className="stat-label">Chats</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Health History Tab */}
        {activeTab === 'health' && (
          <div className="dashboard-content">
            <div className="events-section">
              <div className="section-header">
                <h3>📋 Health Event History</h3>
                <span className="event-count">{liveEvents.length} events</span>
              </div>
              
              {liveEvents.length === 0 ? (
                <div className="no-data">
                  <span className="no-data-icon">📊</span>
                  <p>No health events recorded yet</p>
                  <span className="no-data-hint">Start the sensor stream to see events</span>
                </div>
              ) : (
                <div className="events-list">
                  {liveEvents.slice(0, 20).map((event, i) => (
                    <div key={i} className={`event-row ${event.safety_status?.toLowerCase()}`}>
                      <div className="event-status-indicator" style={{ backgroundColor: getStatusColor(event.safety_status) }} />
                      <div className="event-main">
                        <span className="event-type">{formatEventType(event.type)}</span>
                        <span className="event-value">
                          {event.value?.toFixed(1)} {event.unit}
                        </span>
                      </div>
                      <div className="event-details">
                        <span className="event-trend">📈 {event.trend || 'stable'}</span>
                        <span className="event-score">💚 {event.health_score?.toFixed(0) || '--'}</span>
                      </div>
                      <span className="event-time">{formatTimeAgo(event.timestamp)}</span>
                      {event.reasoning && (
                        <div className="event-reasoning">{event.reasoning}</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Mood History */}
            <div className="mood-section">
              <h3>😊 Mood History</h3>
              <div className="mood-summary">
                <span>Total entries: {moodStats.total}</span>
                <div className="mood-counts">
                  {Object.entries(moodStats.counts).map(([mood, count]) => (
                    <span key={mood} className="mood-count">{mood} {count}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Medications Tab */}
        {activeTab === 'medications' && (
          <div className="dashboard-content">
            <div className="medications-section">
              <h3>💊 Medication Tracking</h3>
              <p className="med-description">
                Track medication reminders and mark when taken
              </p>

              {medicationsDue.length === 0 ? (
                <div className="no-data">
                  <span className="no-data-icon">💊</span>
                  <p>No medication reminders</p>
                  <span className="no-data-hint">Medication events will appear here</span>
                </div>
              ) : (
                <div className="medications-list">
                  {medicationsDue.map((med, i) => (
                    <div key={i} className={`medication-item ${med.taken ? 'taken' : 'pending'}`}>
                      <div className="med-icon">
                        {med.taken ? '✅' : '💊'}
                      </div>
                      <div className="med-info">
                        <span className="med-type">{med.type}</span>
                        <span className="med-time">{formatTimeAgo(med.time)}</span>
                      </div>
                      {!med.taken && (
                        <button 
                          className="med-take-btn"
                          onClick={() => markMedicationTaken(i)}
                        >
                          Mark Taken
                        </button>
                      )}
                      {med.taken && (
                        <span className="med-taken-label">Taken ✓</span>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Quick Add Medication */}
              <div className="quick-add-med">
                <h4>Quick Log</h4>
                <div className="quick-buttons">
                  <button 
                    className="quick-med-btn"
                    onClick={() => setMedicationsDue(prev => [...prev, {
                      type: 'Insulin',
                      time: new Date().toISOString(),
                      taken: true
                    }])}
                  >
                    💉 Log Insulin
                  </button>
                  <button 
                    className="quick-med-btn"
                    onClick={() => setMedicationsDue(prev => [...prev, {
                      type: 'Inhaler',
                      time: new Date().toISOString(),
                      taken: true
                    }])}
                  >
                    🌬️ Log Inhaler
                  </button>
                  <button 
                    className="quick-med-btn"
                    onClick={() => setMedicationsDue(prev => [...prev, {
                      type: 'Snack',
                      time: new Date().toISOString(),
                      taken: true
                    }])}
                  >
                    🍎 Log Snack
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
