-- Real-time Activity Tracking Tables
-- Run this to create the enhanced activity tracking system

-- Enhanced user stats table
CREATE TABLE IF NOT EXISTS user_stats_realtime (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_study_minutes INT DEFAULT 0,
    modules_completed INT DEFAULT 0,
    current_streak_days INT DEFAULT 0,
    longest_streak_days INT DEFAULT 0,
    total_xp_points INT DEFAULT 0,
    skill_level VARCHAR(20) DEFAULT 'Beginner',
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_stats (user_id)
);

-- Module progress tracking
CREATE TABLE IF NOT EXISTS module_progress_realtime (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    module_id INT NOT NULL,
    module_name VARCHAR(255) NOT NULL,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    time_spent_minutes INT DEFAULT 0,
    quiz_score DECIMAL(5,2) DEFAULT 0.00,
    is_completed BOOLEAN DEFAULT FALSE,
    completion_date TIMESTAMP NULL,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_module (user_id, module_id)
);

-- Real-time activity log
CREATE TABLE IF NOT EXISTS activity_log_realtime (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    activity_type ENUM('module_start', 'module_complete', 'quiz_attempt', 'practice_session', 'skill_unlock', 'streak_milestone', 'login', 'logout') NOT NULL,
    module_id INT NULL,
    description TEXT,
    xp_earned INT DEFAULT 0,
    duration_minutes INT DEFAULT 0,
    metadata JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_activity (user_id, created_at),
    INDEX idx_activity_type (activity_type),
    INDEX idx_module_activity (module_id, activity_type)
);

-- Daily activity summary
CREATE TABLE IF NOT EXISTS daily_activity_summary (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    activity_date DATE NOT NULL,
    total_study_minutes INT DEFAULT 0,
    modules_worked_on INT DEFAULT 0,
    quizzes_completed INT DEFAULT 0,
    practice_sessions INT DEFAULT 0,
    xp_earned INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, activity_date)
);

-- Skill development tracking
CREATE TABLE IF NOT EXISTS skill_development (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    skill_category ENUM('alphabet', 'numbers', 'vocabulary', 'grammar', 'conversation', 'comprehension') NOT NULL,
    skill_level INT DEFAULT 1,
    xp_points INT DEFAULT 0,
    milestones_reached INT DEFAULT 0,
    last_practice_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_skill (user_id, skill_category)
);

-- Live session tracking
CREATE TABLE IF NOT EXISTS live_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_type ENUM('study', 'practice', 'quiz', 'review') NOT NULL,
    module_id INT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    duration_minutes INT DEFAULT 0,
    activities_completed INT DEFAULT 0,
    xp_earned INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_active_sessions (user_id, is_active),
    INDEX idx_session_date (start_time)
);

-- Weekly goals and achievements
CREATE TABLE IF NOT EXISTS weekly_goals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    week_start_date DATE NOT NULL,
    study_minutes_goal INT DEFAULT 300, -- 5 hours default
    modules_goal INT DEFAULT 2,
    practice_sessions_goal INT DEFAULT 10,
    current_study_minutes INT DEFAULT 0,
    current_modules INT DEFAULT 0,
    current_practice_sessions INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_week (user_id, week_start_date)
);

-- Task management system
CREATE TABLE IF NOT EXISTS user_tasks_realtime (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    task_type ENUM('daily', 'weekly', 'module', 'custom') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    is_completed BOOLEAN DEFAULT FALSE,
    due_date DATE NULL,
    completed_at TIMESTAMP NULL,
    xp_reward INT DEFAULT 10,
    module_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_tasks (user_id, is_completed),
    INDEX idx_task_due_date (due_date),
    INDEX idx_task_type (task_type)
);

-- Indexes for performance
CREATE INDEX idx_user_stats_activity ON user_stats_realtime(user_id, last_activity_date);
CREATE INDEX idx_module_progress_user ON module_progress_realtime(user_id, last_accessed);
CREATE INDEX idx_activity_log_recent ON activity_log_realtime(user_id, created_at DESC);
CREATE INDEX idx_daily_summary_recent ON daily_activity_summary(user_id, activity_date DESC);
CREATE INDEX idx_skill_development_user ON skill_development(user_id, skill_category);

-- Insert default skill categories for existing users
INSERT IGNORE INTO skill_development (user_id, skill_category)
SELECT u.id, 'alphabet' FROM users u
UNION ALL
SELECT u.id, 'numbers' FROM users u
UNION ALL
SELECT u.id, 'vocabulary' FROM users u
UNION ALL
SELECT u.id, 'grammar' FROM users u
UNION ALL
SELECT u.id, 'conversation' FROM users u
UNION ALL
SELECT u.id, 'comprehension' FROM users u;

-- Create default weekly goals for active users
INSERT IGNORE INTO weekly_goals (user_id, week_start_date)
SELECT u.id, DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)
FROM users u
WHERE u.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);