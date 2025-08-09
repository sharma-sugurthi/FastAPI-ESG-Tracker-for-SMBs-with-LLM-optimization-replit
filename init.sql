-- ESG Compliance Tracker Database Initialization

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS esg_tracker;

-- Use the database
\c esg_tracker;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    industry VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create ESG questionnaires table
CREATE TABLE IF NOT EXISTS esg_questionnaires (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    company_name VARCHAR(255),
    industry VARCHAR(100),
    answers JSONB,
    score FLOAT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ESG tasks table
CREATE TABLE IF NOT EXISTS esg_tasks (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    task TEXT NOT NULL,
    description TEXT,
    points INTEGER,
    category VARCHAR(50),
    difficulty VARCHAR(20),
    estimated_impact VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create scraping requests table
CREATE TABLE IF NOT EXISTS scraping_requests (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    url TEXT NOT NULL,
    status VARCHAR(50),
    scraped_content JSONB,
    gdpr_compliance JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create regulatory alerts table
CREATE TABLE IF NOT EXISTS regulatory_alerts (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    source VARCHAR(50),
    source_url TEXT,
    category VARCHAR(50),
    keywords TEXT[],
    relevance_score FLOAT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    completed_tasks INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create predictive alerts table
CREATE TABLE IF NOT EXISTS predictive_alerts (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    alert_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    predicted_impact TEXT,
    recommended_actions JSONB,
    timeline_days INTEGER,
    confidence_score FLOAT,
    data_sources JSONB,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Create ESG score history table for trend analysis
CREATE TABLE IF NOT EXISTS esg_score_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    overall_score FLOAT,
    environmental_score FLOAT,
    social_score FLOAT,
    governance_score FLOAT,
    emissions_score FLOAT,
    energy_score FLOAT,
    waste_score FLOAT,
    diversity_score FLOAT,
    employee_score FLOAT,
    community_score FLOAT,
    ethics_score FLOAT,
    transparency_score FLOAT,
    badge VARCHAR(50),
    level INTEGER,
    industry_percentile FLOAT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_predictive_alerts_user_id ON predictive_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_predictive_alerts_risk_level ON predictive_alerts(risk_level);
CREATE INDEX IF NOT EXISTS idx_predictive_alerts_expires_at ON predictive_alerts(expires_at);
CREATE INDEX IF NOT EXISTS idx_esg_score_history_user_id ON esg_score_history(user_id);
CREATE INDEX IF NOT EXISTS idx_esg_score_history_calculated_at ON esg_score_history(calculated_at);

-- Insert sample predictive alerts for testing
INSERT INTO predictive_alerts (
    id, user_id, alert_type, risk_level, title, description, predicted_impact,
    recommended_actions, timeline_days, confidence_score, data_sources,
    created_at, expires_at
) VALUES 
(
    'alert-001',
    'user-123',
    'compliance_gap',
    'high',
    'Critical Environmental Score Alert',
    'Your environmental performance score has dropped below compliance thresholds',
    'Risk of regulatory penalties and stakeholder concerns within 60 days',
    '["Conduct immediate energy audit", "Implement waste reduction program", "Review packaging sustainability"]',
    60,
    0.85,
    '["esg_scoring", "trend_analysis"]',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '60 days'
),
(
    'alert-002',
    'user-123',
    'regulatory_deadline',
    'critical',
    'CSRD Reporting Deadline Approaching',
    'CSRD compliance deadline in 30 days with current readiness score of 45%',
    'Risk of missing mandatory reporting deadline and facing penalties',
    '["Review CSRD requirements", "Prepare sustainability documentation", "Consider expert consultation"]',
    30,
    0.92,
    '["regulatory_calendar", "compliance_analysis"]',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '30 days'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_questionnaires_user_id ON esg_questionnaires(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON esg_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON esg_tasks(status);
CREATE INDEX IF NOT EXISTS idx_scraping_user_id ON scraping_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_category ON regulatory_alerts(category);
CREATE INDEX IF NOT EXISTS idx_alerts_published ON regulatory_alerts(published_at);

-- Insert sample data for testing
INSERT INTO users (id, email, full_name, company_name, industry) VALUES
('demo-user-1', 'demo@example.com', 'Demo User', 'Demo Retail Co.', 'retail')
ON CONFLICT (id) DO NOTHING;

-- Insert sample regulatory alerts
INSERT INTO regulatory_alerts (id, title, summary, source, category, relevance_score, published_at) VALUES
('alert-1', 'New ESG Reporting Requirements for 2024', 'Companies must now report on additional ESG metrics including scope 3 emissions.', 'google_news', 'regulatory', 0.9, CURRENT_TIMESTAMP),
('alert-2', 'EU Taxonomy Updates for Retail Sector', 'Updated sustainability criteria for retail businesses operating in the EU.', 'google_news', 'policy_changes', 0.8, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

