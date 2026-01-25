import { useMemo, useState } from 'react';
import { MoodEntry } from './MoodTracker';
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
  chatHistory: Message[];
  moodHistory: MoodEntry[];
  healthLogs?: HealthLog[];
  engagementData?: EngagementData;
  healthMetrics?: HealthMetrics | null;
  healthScore?: number;
  safetyStatus?: string;
  healthEvents?: HealthEvent[];
  simulatorAlerts?: SimulatorAlert[];
  onClose: () => void;
}

// Keywords that might indicate concerning responses
const CONCERN_KEYWORDS = [
  'hurt', 'pain', 'scared', 'dizzy', 'faint', 'blood', 'emergency',
  'help', 'bad', 'worse', 'sick', 'hospital', 'cant breathe', "can't breathe"
];

// Topic categories for conversation analysis
const TOPIC_KEYWORDS: Record<string, string[]> = {
  'Symptoms': ['hurt', 'pain', 'ache', 'sick', 'dizzy', 'tired', 'headache', 'tummy', 'stomach'],
  'Emotions': ['happy', 'sad', 'scared', 'worried', 'angry', 'cry', 'feel', 'mood'],
  'Health Questions': ['why', 'what', 'how', 'glucose', 'sugar', 'insulin', 'medicine', 'doctor'],
  'Daily Life': ['school', 'play', 'friend', 'eat', 'sleep', 'game', 'fun'],
};

export default function ParentDashboard({ 
  chatHistory, 
  moodHistory, 
  healthLogs = [],
  engagementData,
  healthMetrics,
  healthScore = 75,
  safetyStatus = 'SAFE',
  healthEvents = [],
  simulatorAlerts = [],
  onClose 
}: ParentDashboardProps) {
  
  const [activeTab, setActiveTab] = useState<'overview' | 'health' | 'insights'>('overview');
  const [reviewedAlerts, setReviewedAlerts] = useState<Set<string>>(new Set());

  // Analyze chat for concerning messages
  const chatAlerts = useMemo(() => {
    return chatHistory
      .filter(msg => msg.role === 'user')
      .filter(msg => {
        const lowerText = msg.text.toLowerCase();
        return CONCERN_KEYWORDS.some(keyword => lowerText.includes(keyword));
      })
      .map((msg, index) => ({
        id: `chat-${index}`,
        text: msg.text,
        timestamp: msg.timestamp || new Date(),
        source: 'chat' as const
      }));
  }, [chatHistory]);

  // Combine chat alerts with simulator alerts
  const allAlerts = useMemo(() => {
    const simAlerts = simulatorAlerts.map(a => ({
      id: a.id,
      text: `${a.type.replace('_', ' ').toUpperCase()}: ${a.value} ${a.unit} - ${a.message}`,
      timestamp: new Date(a.timestamp),
      source: 'simulator' as const,
      severity: a.severity,
      health_score: a.health_score
    }));
    
    const combined = [
      ...simAlerts,
      ...chatAlerts.map(a => ({ ...a, severity: 'warning', health_score: 0 }))
    ];
    
    return combined.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [chatAlerts, simulatorAlerts]);

  // Calculate mood statistics
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

    return {
      total: last7Days.length,
      counts: moodCounts,
      entries: last7Days,
    };
  }, [moodHistory]);

  // Analyze conversation topics
  const topicAnalysis = useMemo(() => {
    const topics: Record<string, number> = {};
    
    chatHistory
      .filter(msg => msg.role === 'user')
      .forEach(msg => {
        const lowerText = msg.text.toLowerCase();
        Object.entries(TOPIC_KEYWORDS).forEach(([topic, keywords]) => {
          if (keywords.some(keyword => lowerText.includes(keyword))) {
            topics[topic] = (topics[topic] || 0) + 1;
          }
        });
      });

    const total = Object.values(topics).reduce((a, b) => a + b, 0) || 1;
    return Object.entries(topics)
      .map(([topic, count]) => ({
        topic,
        count,
        percentage: Math.round((count / total) * 100)
      }))
      .sort((a, b) => b.count - a.count);
  }, [chatHistory]);

  // Calculate Wellness Score (0-100) - now uses simulator health score
  const wellnessScore = useMemo(() => {
    // Start with simulator health score if available
    let score = healthScore || 70;

    // Mood impact
    const positiveMoods = (moodStats.counts['😊'] || 0);
    const negativeMoods = (moodStats.counts['😢'] || 0) + (moodStats.counts['🤒'] || 0);
    score += positiveMoods * 2;
    score -= negativeMoods * 3;

    // Alert impact
    const unreviewedAlerts = allAlerts.filter(a => !reviewedAlerts.has(a.id)).length;
    score -= unreviewedAlerts * 5;

    // Critical alerts have bigger impact
    const criticalAlerts = simulatorAlerts.filter(a => a.severity === 'critical').length;
    score -= criticalAlerts * 10;

    // Engagement bonus
    if (engagementData) {
      if (engagementData.currentStreak >= 3) score += 5;
      if (engagementData.currentStreak >= 7) score += 5;
    }

    return Math.max(0, Math.min(100, Math.round(score)));
  }, [healthScore, moodStats, allAlerts, reviewedAlerts, engagementData, simulatorAlerts]);

  // Generate smart recommendations based on simulator data
  const recommendations = useMemo(() => {
    const recs: { icon: string; text: string; priority: 'high' | 'medium' | 'low' }[] = [];

    // Check simulator health metrics
    if (healthMetrics) {
      if (healthMetrics.glucose?.status === 'warning') {
        recs.push({
          icon: '🍎',
          text: `Glucose is ${(healthMetrics.glucose?.value || 5.5) < 4 ? 'low' : 'high'} (${healthMetrics.glucose?.value || '--'} mmol/L) - monitor closely`,
          priority: 'high'
        });
      }

      if (healthMetrics.spo2?.status === 'low') {
        recs.push({
          icon: '🫁',
          text: `Oxygen saturation is low (${healthMetrics.spo2?.value || '--'}%) - check breathing`,
          priority: 'high'
        });
      }

      if (healthMetrics.asthma_risk?.status === 'high') {
        recs.push({
          icon: '🌬️',
          text: 'Asthma risk is elevated - ensure inhaler is available',
          priority: 'high'
        });
      }

      if (healthMetrics.mood?.status === 'low') {
        recs.push({
          icon: '💙',
          text: 'Mood indicators are low - consider checking in with your child',
          priority: 'medium'
        });
      }

      if (healthMetrics.activity?.status === 'sedentary') {
        recs.push({
          icon: '🏃',
          text: 'Activity level is low - encourage some movement or play',
          priority: 'low'
        });
      }
    }

    // Check for consecutive tired moods
    const recentMoods = moodStats.entries.slice(-3);
    const tiredCount = recentMoods.filter(m => m.mood === '😫').length;
    if (tiredCount >= 2) {
      recs.push({
        icon: '😴',
        text: 'Child has been tired frequently - consider earlier bedtime',
        priority: 'medium'
      });
    }

    // Safety status based recommendations
    if (safetyStatus === 'DANGER') {
      recs.push({
        icon: '🚨',
        text: 'Critical health event detected - immediate attention required',
        priority: 'high'
      });
    } else if (safetyStatus === 'MONITOR') {
      recs.push({
        icon: '👀',
        text: 'Health metrics need monitoring - check on your child',
        priority: 'medium'
      });
    }

    // Unreviewed alerts
    if (allAlerts.length > 0 && reviewedAlerts.size < allAlerts.length) {
      recs.push({
        icon: '⚠️',
        text: `${allAlerts.length - reviewedAlerts.size} alert(s) need your attention`,
        priority: 'high'
      });
    }

    // Positive reinforcement
    if (wellnessScore >= 80) {
      recs.push({
        icon: '🌟',
        text: 'Great health metrics! Keep up the excellent care!',
        priority: 'low'
      });
    }

    return recs.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }, [healthMetrics, moodStats, safetyStatus, allAlerts, reviewedAlerts, wellnessScore]);

  // Get mood bar height percentage
  const getBarHeight = (count: number) => {
    if (moodStats.total === 0) return 0;
    return (count / moodStats.total) * 100;
  };

  const moodColors: Record<string, string> = {
    '😊': '#00b894',
    '😐': '#fdcb6e',
    '😢': '#74b9ff',
    '😫': '#a29bfe',
    '🤒': '#ff7675',
  };

  // Export data as JSON (downloadable)
  const exportData = () => {
    const data = {
      exportDate: new Date().toISOString(),
      chatHistory: chatHistory,
      moodHistory: moodHistory,
      healthLogs: healthLogs,
      healthEvents: healthEvents,
      healthMetrics: healthMetrics,
      wellnessScore: wellnessScore,
      alerts: allAlerts,
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leo-health-report-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Mark alert as reviewed
  const markAlertReviewed = (alertId: string) => {
    setReviewedAlerts(prev => new Set([...prev, alertId]));
  };

  // Get wellness score color
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#00b894';
    if (score >= 60) return '#fdcb6e';
    if (score >= 40) return '#f39c12';
    return '#ff7675';
  };

  // Get status color
  const getStatusColor = (status: string) => {
    if (status === 'DANGER') return '#ff7675';
    if (status === 'MONITOR') return '#fdcb6e';
    return '#00b894';
  };

  // Get metric status color
  const getMetricStatusColor = (status: string) => {
    if (status === 'warning' || status === 'low' || status === 'high') return '#ff7675';
    if (status === 'elevated' || status === 'moderate') return '#fdcb6e';
    return '#00b894';
  };

  // Get topic color
  const getTopicColor = (topic: string) => {
    const colors: Record<string, string> = {
      'Symptoms': '#ff7675',
      'Emotions': '#a29bfe',
      'Health Questions': '#74b9ff',
      'Daily Life': '#00b894',
    };
    return colors[topic] || '#dfe6e9';
  };

  // Format event type for display
  const formatEventType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  return (
    <div className="dashboard-overlay">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>👨‍👩‍👧 Parent Dashboard</h1>
          <div className="header-actions">
            <div 
              className="safety-status-badge"
              style={{ backgroundColor: getStatusColor(safetyStatus) }}
            >
              {safetyStatus === 'DANGER' ? '🚨' : safetyStatus === 'MONITOR' ? '👀' : '✓'} {safetyStatus}
            </div>
            <button className="export-btn" onClick={exportData} title="Export Data">
              📤 Export
            </button>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'health' ? 'active' : ''}`}
            onClick={() => setActiveTab('health')}
          >
            ❤️ Health
          </button>
          <button 
            className={`tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            💡 Insights
          </button>
        </div>

        {/* Wellness Score Banner */}
        <div className="wellness-banner">
          <div className="wellness-score-container">
            <div 
              className="wellness-score-ring"
              style={{ 
                background: `conic-gradient(${getScoreColor(wellnessScore)} ${wellnessScore * 3.6}deg, #e0e0e0 0deg)`
              }}
            >
              <div className="wellness-score-inner">
                <span className="wellness-score-value">{wellnessScore}</span>
                <span className="wellness-score-label">Wellness</span>
              </div>
            </div>
          </div>
          <div className="wellness-info">
            <h3>Weekly Wellness Score</h3>
            <p>Based on mood patterns, health metrics, and alerts</p>
            <div className="wellness-factors">
              <span className="factor">😊 Moods: {moodStats.total}</span>
              <span className="factor">💬 Messages: {chatHistory.length}</span>
              <span className="factor">🔥 Streak: {engagementData?.currentStreak || 0} days</span>
              <span className="factor" style={{ color: getStatusColor(safetyStatus) }}>
                🩺 {safetyStatus}
              </span>
            </div>
          </div>
        </div>

        {activeTab === 'overview' && (
          <div className="dashboard-grid">
            {/* Real-time Health Metrics */}
            {healthMetrics && healthMetrics.glucose && healthMetrics.heart_rate && (
              <div className="dashboard-card vitals-card">
                <h2>🩺 Live Health Metrics</h2>
                <div className="vitals-grid">
                  <div className="vital-item">
                    <span className="vital-icon">🍎</span>
                    <div className="vital-info">
                      <span className="vital-label">Glucose</span>
                      <span 
                        className="vital-value"
                        style={{ color: getMetricStatusColor(healthMetrics.glucose?.status || 'normal') }}
                      >
                        {healthMetrics.glucose?.value?.toFixed(1) || '--'} {healthMetrics.glucose?.unit || 'mmol/L'}
                      </span>
                    </div>
                  </div>
                  <div className="vital-item">
                    <span className="vital-icon">❤️</span>
                    <div className="vital-info">
                      <span className="vital-label">Heart Rate</span>
                      <span 
                        className="vital-value"
                        style={{ color: getMetricStatusColor(healthMetrics.heart_rate?.status || 'normal') }}
                      >
                        {healthMetrics.heart_rate?.value?.toFixed(0) || '--'} {healthMetrics.heart_rate?.unit || 'bpm'}
                      </span>
                    </div>
                  </div>
                  {healthMetrics.spo2 && (
                    <div className="vital-item">
                      <span className="vital-icon">🫁</span>
                      <div className="vital-info">
                        <span className="vital-label">SpO2</span>
                        <span 
                          className="vital-value"
                          style={{ color: getMetricStatusColor(healthMetrics.spo2?.status || 'normal') }}
                        >
                          {healthMetrics.spo2?.value?.toFixed(0) || '--'}{healthMetrics.spo2?.unit || '%'}
                        </span>
                      </div>
                    </div>
                  )}
                  {healthMetrics.mood && (
                    <div className="vital-item">
                      <span className="vital-icon">😊</span>
                      <div className="vital-info">
                        <span className="vital-label">Mood</span>
                        <span 
                          className="vital-value"
                          style={{ color: getMetricStatusColor(healthMetrics.mood?.status || 'neutral') }}
                        >
                          {((healthMetrics.mood?.value || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  )}
                  {healthMetrics.activity && (
                    <div className="vital-item">
                      <span className="vital-icon">🏃</span>
                      <div className="vital-info">
                        <span className="vital-label">Activity</span>
                        <span className="vital-value">
                          {((healthMetrics.activity?.value || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  )}
                  {healthMetrics.asthma_risk && (
                    <div className="vital-item">
                      <span className="vital-icon">🌬️</span>
                      <div className="vital-info">
                        <span className="vital-label">Asthma Risk</span>
                        <span 
                          className="vital-value"
                          style={{ color: getMetricStatusColor(healthMetrics.asthma_risk?.status || 'low') }}
                        >
                          {((healthMetrics.asthma_risk?.value || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Alerts Section */}
            <div className="dashboard-card alerts-card">
              <h2>🚨 Alerts ({allAlerts.length})</h2>
              {allAlerts.length === 0 ? (
                <div className="no-alerts">
                  <span className="check-icon">✅</span>
                  <p>No alerts - everything looks good!</p>
                </div>
              ) : (
                <div className="alerts-list">
                  {allAlerts.slice(0, 5).map((alert) => (
                    <div 
                      key={alert.id} 
                      className={`alert-item ${reviewedAlerts.has(alert.id) ? 'reviewed' : ''} ${alert.severity === 'critical' ? 'critical' : ''}`}
                    >
                      <span className="alert-icon">
                        {reviewedAlerts.has(alert.id) ? '✓' : alert.severity === 'critical' ? '🔴' : '⚠️'}
                      </span>
                      <div className="alert-content">
                        <p className="alert-text">{alert.text}</p>
                        <span className="alert-time">
                          {new Date(alert.timestamp).toLocaleString()}
                        </span>
                      </div>
                      {!reviewedAlerts.has(alert.id) && (
                        <button 
                          className="review-btn"
                          onClick={() => markAlertReviewed(alert.id)}
                        >
                          ✓
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Smart Recommendations */}
            <div className="dashboard-card recommendations-card">
              <h2>💡 Recommendations</h2>
              {recommendations.length === 0 ? (
                <div className="no-data">
                  <span className="thumbs-up">👍</span>
                  <p>Everything looks great!</p>
                </div>
              ) : (
                <div className="recommendations-list">
                  {recommendations.map((rec, i) => (
                    <div key={i} className={`recommendation-item priority-${rec.priority}`}>
                      <span className="rec-icon">{rec.icon}</span>
                      <p className="rec-text">{rec.text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="dashboard-card actions-card">
              <h2>⚡ Quick Actions</h2>
              <div className="quick-actions">
                <button className="action-btn">
                  <span className="action-icon">🔔</span>
                  <span>Set Reminder</span>
                </button>
                <button className="action-btn">
                  <span className="action-icon">💌</span>
                  <span>Send Encouragement</span>
                </button>
                <button className="action-btn" onClick={exportData}>
                  <span className="action-icon">📄</span>
                  <span>Export Report</span>
                </button>
                <button className="action-btn">
                  <span className="action-icon">👨‍⚕️</span>
                  <span>Share with Doctor</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'health' && (
          <div className="dashboard-grid">
            {/* Recent Health Events */}
            <div className="dashboard-card events-card">
              <h2>📊 Recent Health Events</h2>
              {healthEvents.length === 0 ? (
                <div className="no-data">
                  <span className="health-icon">💉</span>
                  <p>No health events recorded yet</p>
                  <span className="sub-text">Run the simulator to see events</span>
                </div>
              ) : (
                <div className="events-list">
                  {healthEvents.slice(0, 10).map((event, i) => (
                    <div 
                      key={i} 
                      className={`event-item ${event.safety_status.toLowerCase()}`}
                    >
                      <div className="event-header">
                        <span className="event-type">{formatEventType(event.type)}</span>
                        <span 
                          className="event-status"
                          style={{ color: getStatusColor(event.safety_status) }}
                        >
                          {event.safety_status}
                        </span>
                      </div>
                      <div className="event-details">
                        <span className="event-value">{event.value} {event.unit}</span>
                        <span className="event-trend">📈 {event.trend}</span>
                        <span className="event-score">💚 {event.health_score?.toFixed(0) || 'N/A'}</span>
                      </div>
                      {event.reasoning && (
                        <p className="event-reasoning">{event.reasoning}</p>
                      )}
                      <span className="event-time">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Mood Chart */}
            <div className="dashboard-card mood-card">
              <h2>📊 Mood This Week</h2>
              {moodStats.total === 0 ? (
                <div className="no-data">
                  <p>No mood data yet</p>
                </div>
              ) : (
                <div className="mood-chart">
                  <div className="chart-bars">
                    {Object.entries(moodStats.counts).map(([mood, count]) => (
                      <div key={mood} className="chart-bar-container">
                        <div 
                          className="chart-bar"
                          style={{ 
                            height: `${getBarHeight(count)}%`,
                            backgroundColor: moodColors[mood] || '#dfe6e9'
                          }}
                        >
                          <span className="bar-count">{count}</span>
                        </div>
                        <span className="bar-label">{mood}</span>
                      </div>
                    ))}
                  </div>
                  <p className="chart-summary">
                    {moodStats.total} mood entries this week
                  </p>
                </div>
              )}
            </div>

            {/* Mood Timeline */}
            <div className="dashboard-card timeline-card">
              <h2>📅 Mood Timeline</h2>
              <div className="timeline">
                {moodStats.entries.slice(-7).reverse().map((entry, i) => (
                  <div key={i} className="timeline-item">
                    <span className="timeline-mood">{entry.mood}</span>
                    <div className="timeline-info">
                      <span className="timeline-label">{entry.label}</span>
                      <span className="timeline-date">
                        {new Date(entry.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
                {moodStats.entries.length === 0 && (
                  <p className="no-data">No mood entries yet</p>
                )}
              </div>
            </div>

            {/* Chat Summary */}
            <div className="dashboard-card chat-card">
              <h2>💬 Recent Conversations</h2>
              <div className="chat-summary">
                <div className="summary-stat">
                  <span className="stat-number">{chatHistory.length}</span>
                  <span className="stat-label">Total Messages</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-number">
                    {chatHistory.filter(m => m.role === 'user').length}
                  </span>
                  <span className="stat-label">Child Messages</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-number">
                    {chatHistory.filter(m => m.role === 'leo').length}
                  </span>
                  <span className="stat-label">Leo Responses</span>
                </div>
              </div>

              <div className="chat-history">
                <h3>Recent Messages</h3>
                <div className="history-list">
                  {chatHistory.slice(-10).reverse().map((msg, i) => (
                    <div key={i} className={`history-item ${msg.role}`}>
                      <span className="history-role">
                        {msg.role === 'leo' ? '🦁' : '👤'}
                      </span>
                      <p className="history-text">{msg.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="dashboard-grid">
            {/* Topic Analysis */}
            <div className="dashboard-card topics-card">
              <h2>🏷️ Conversation Topics</h2>
              {topicAnalysis.length === 0 ? (
                <div className="no-data">
                  <p>Not enough conversation data yet</p>
                </div>
              ) : (
                <div className="topics-chart">
                  {topicAnalysis.map((topic, i) => (
                    <div key={i} className="topic-row">
                      <div className="topic-label">
                        <span>{topic.topic}</span>
                        <span className="topic-count">{topic.count}</span>
                      </div>
                      <div className="topic-bar-container">
                        <div 
                          className="topic-bar"
                          style={{ 
                            width: `${topic.percentage}%`,
                            backgroundColor: getTopicColor(topic.topic)
                          }}
                        />
                      </div>
                      <span className="topic-percentage">{topic.percentage}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Engagement Insights */}
            <div className="dashboard-card engagement-card">
              <h2>📱 Engagement</h2>
              <div className="engagement-stats">
                <div className="engagement-stat">
                  <div className="engagement-icon">🔥</div>
                  <div className="engagement-value">{engagementData?.currentStreak || 0}</div>
                  <div className="engagement-label">Current Streak</div>
                </div>
                <div className="engagement-stat">
                  <div className="engagement-icon">🏆</div>
                  <div className="engagement-value">{engagementData?.longestStreak || 0}</div>
                  <div className="engagement-label">Best Streak</div>
                </div>
                <div className="engagement-stat">
                  <div className="engagement-icon">💬</div>
                  <div className="engagement-value">
                    {engagementData?.avgMessagesPerDay?.toFixed(1) || 0}
                  </div>
                  <div className="engagement-label">Avg Msgs/Day</div>
                </div>
                <div className="engagement-stat">
                  <div className="engagement-icon">📅</div>
                  <div className="engagement-value">{engagementData?.totalSessions || 0}</div>
                  <div className="engagement-label">Total Sessions</div>
                </div>
              </div>

              {/* Activity Heatmap */}
              <div className="activity-section">
                <h3>Weekly Activity</h3>
                <div className="activity-heatmap">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, i) => {
                    const activity = engagementData?.dailyActivity?.[day] || 0;
                    const intensity = Math.min(activity / 10, 1);
                    return (
                      <div key={i} className="heatmap-cell">
                        <div 
                          className="heatmap-box"
                          style={{ 
                            backgroundColor: `rgba(102, 126, 234, ${0.2 + intensity * 0.8})`
                          }}
                          title={`${day}: ${activity} messages`}
                        />
                        <span className="heatmap-label">{day}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Weekly Summary */}
            <div className="dashboard-card summary-card">
              <h2>📋 Weekly Summary</h2>
              <div className="summary-content">
                <div className="summary-row">
                  <span className="summary-icon">😊</span>
                  <span className="summary-text">
                    Most common mood: {
                      Object.entries(moodStats.counts)
                        .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'
                    }
                  </span>
                </div>
                <div className="summary-row">
                  <span className="summary-icon">💬</span>
                  <span className="summary-text">
                    {chatHistory.filter(m => m.role === 'user').length} questions asked this week
                  </span>
                </div>
                <div className="summary-row">
                  <span className="summary-icon">🎯</span>
                  <span className="summary-text">
                    Top topic: {topicAnalysis[0]?.topic || 'General Chat'}
                  </span>
                </div>
                <div className="summary-row">
                  <span className="summary-icon">⚠️</span>
                  <span className="summary-text">
                    {allAlerts.length} alert{allAlerts.length !== 1 ? 's' : ''} this week
                  </span>
                </div>
                <div className="summary-row">
                  <span className="summary-icon">🩺</span>
                  <span className="summary-text">
                    {healthEvents.length} health events recorded
                  </span>
                </div>
                <div className="summary-row">
                  <span className="summary-icon">💚</span>
                  <span className="summary-text">
                    Average health score: {healthScore?.toFixed(0) || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
