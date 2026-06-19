CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR(50),
    user_role VARCHAR(20),
    action VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    ip_address VARCHAR(50),
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);
CREATE INDEX idx_activity_logs_category ON activity_logs(category);
CREATE INDEX idx_activity_logs_created ON activity_logs(created_at DESC);
