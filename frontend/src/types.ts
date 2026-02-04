export interface Message {
    role: string;
    text: string;
    timestamp?: Date;
}

export interface HealthLog {
    metric_type: string;
    value: number;
    unit: string;
    timestamp: Date;
}

export interface HealthMetric {
    value: number;
    unit: string;
    status: string;
}

export interface HealthMetrics {
    glucose: HealthMetric;
    heart_rate: HealthMetric;
    mood: HealthMetric;
    activity: HealthMetric;
    spo2: HealthMetric;
    asthma_risk: HealthMetric;
}

export interface HealthEvent {
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
    metadata?: {
        medication_type?: string;
    };
}

export interface SimulatorAlert {
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

export interface EngagementData {
    totalSessions: number;
    currentStreak: number;
    longestStreak: number;
    avgMessagesPerDay: number;
    lastActiveDate: Date | null;
    dailyActivity: Record<string, number>;
}

export interface UserStats {
    xp: number;
    level: number;
    status: string;
}
