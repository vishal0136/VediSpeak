-- =====================================
-- DATABASE SETUP
-- =====================================
CREATE DATABASE IF NOT EXISTS isl_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE isl_app;

-- =====================================
-- USERS TABLE (Core User Information)
-- =====================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,         -- unique phone
    password VARCHAR(255) NOT NULL,
    otp_code VARCHAR(10) DEFAULT NULL,
    otp_expiry DATETIME DEFAULT NULL,
    oauth_provider VARCHAR(50) DEFAULT NULL,
    oauth_id VARCHAR(255) DEFAULT NULL,
    profession VARCHAR(100) DEFAULT NULL,
    bio TEXT DEFAULT NULL,
    profile_photo VARCHAR(255) DEFAULT 'default.png',
    resume_path VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_oauth_id ON users(oauth_id);

-- =====================================
-- USER STATS TABLE (Activity & Points)
-- =====================================
CREATE TABLE IF NOT EXISTS user_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    courses INT DEFAULT 0,                 -- total enrolled courses
    progress INT DEFAULT 0,                -- overall percentage
    achievements INT DEFAULT 0,            -- number of badges
    points INT DEFAULT 0,                  -- gamified points
    modules_completed INT DEFAULT 0,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type ENUM('study','online_test') NOT NULL,
    duration_minutes INT NOT NULL,
    activity_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_userstats_user ON user_stats(user_id);
CREATE INDEX idx_useractivity_user ON user_activity(user_id);

-- =====================================
-- ENROLLED COURSES TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS enrolled_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    description TEXT DEFAULT NULL,
    duration VARCHAR(50) DEFAULT NULL,
    total_classes INT DEFAULT 10,
    completed_classes INT DEFAULT 0,
    progress INT DEFAULT 0,
    badge_icon VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_enrolled_user ON enrolled_courses(user_id);

-- =====================================
-- ACHIEVEMENTS / BADGES TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    badge_title VARCHAR(100) NOT NULL,
    badge_desc TEXT DEFAULT NULL,
    module_name VARCHAR(100) DEFAULT NULL,  
    progress INT DEFAULT 0,                 
    earned_date DATE DEFAULT NULL,
    badge_icon VARCHAR(255) DEFAULT 'default_badge.png',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_achievements_user ON achievements(user_id);

-- =====================================
-- PORTFOLIO LINKS TABLE
-- =====================================
CREATE TABLE IF NOT EXISTS portfolio_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    platform VARCHAR(50) NOT NULL,         
    url VARCHAR(255) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_portfolio_user ON portfolio_links(user_id);

SELECT * FROM users;
SELECT * FROM user_stats;
SELECT * FROM enrolled_courses;
SELECT * FROM achievements;
SELECT * FROM portfolio_links;

-- =====================================
-- ENHANCED TABLES FOR REAL-TIME FEATURES
-- =====================================

-- User Tasks Table
CREATE TABLE IF NOT EXISTS user_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    text TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_tasks_user ON user_tasks(user_id);
CREATE INDEX idx_user_tasks_completed ON user_tasks(completed);

-- User Activity Log Table (for real-time activity tracking)
CREATE TABLE IF NOT EXISTS user_activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    xp_earned INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_activity_log_user ON user_activity_log(user_id);
CREATE INDEX idx_activity_log_type ON user_activity_log(activity_type);

-- User Sessions Table (for focus session tracking)
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_type VARCHAR(50) DEFAULT 'study',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_active ON user_sessions(end_time);

-- User Skills Table (for skill progress tracking)
CREATE TABLE IF NOT EXISTS user_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    progress_percentage INT DEFAULT 0,
    xp_earned INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_skill (user_id, skill_name)
);

CREATE INDEX idx_user_skills_user ON user_skills(user_id);

-- User Achievements Extended Table
CREATE TABLE IF NOT EXISTS user_achievements_extended (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    achievement_type VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    icon VARCHAR(100) DEFAULT 'trophy',
    xp_reward INT DEFAULT 0,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_achievements_ext_user ON user_achievements_extended(user_id);
CREATE INDEX idx_achievements_ext_type ON user_achievements_extended(achievement_type);

-- Real-time Notifications Table
CREATE TABLE IF NOT EXISTS user_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'error') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user ON user_notifications(user_id);
CREATE INDEX idx_notifications_read ON user_notifications(is_read);

-- Insert sample data for testing
INSERT IGNORE INTO user_tasks (user_id, text, priority, completed) VALUES
(1, 'Complete Python Module 5', 'high', FALSE),
(1, 'Review Machine Learning Notes', 'medium', TRUE),
(1, 'Practice Data Structures', 'high', FALSE),
(1, 'Read Research Paper on AI', 'low', FALSE),
(1, 'Update Portfolio Website', 'medium', TRUE),
(1, 'Prepare for Technical Interview', 'high', FALSE),
(1, 'Learn Docker Fundamentals', 'medium', TRUE),
(1, 'Build REST API Project', 'high', FALSE);

INSERT IGNORE INTO user_activity_log (user_id, activity_type, description, xp_earned) VALUES
(1, 'task_completed', 'Completed Python Course Module', 50),
(1, 'session_started', 'Started Machine Learning Project', 25),
(1, 'task_created', 'Added new learning task', 10),
(1, 'session_ended', 'Completed 45-minute study session', 30),
(1, 'achievement_earned', 'Earned 15-Day Streak Master badge', 100);

INSERT IGNORE INTO user_skills (user_id, skill_name, progress_percentage, xp_earned) VALUES
(1, 'Python Programming', 85, 850),
(1, 'Machine Learning', 72, 720),
(1, 'Data Analysis', 68, 680),
(1, 'Web Development', 91, 910);

INSERT IGNORE INTO user_achievements_extended (user_id, achievement_type, title, description, icon, xp_reward) VALUES
(1, 'streak', '15-Day Streak Master', 'Maintained daily learning for 15 consecutive days', 'fire', 100),
(1, 'skill', 'Python Expert', 'Completed advanced Python programming course', 'code', 75),
(1, 'task', 'Task Master', 'Completed 100 tasks this month', 'tasks', 50);

-- Learning Management System Tables
CREATE TABLE IF NOT EXISTS learning_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    module_id INT NOT NULL,
    lesson_id INT NOT NULL,
    progress DECIMAL(5,2) DEFAULT 0.00,
    completed BOOLEAN DEFAULT FALSE,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_progress (user_id, module_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS learning_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    module_id INT DEFAULT NULL,
    lesson_id INT DEFAULT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    duration_minutes INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10) DEFAULT '📚',
    color_from VARCHAR(20) DEFAULT 'amber-200',
    color_to VARCHAR(20) DEFAULT 'pink-200',
    total_lessons INT DEFAULT 0,
    estimated_hours DECIMAL(4,2) DEFAULT 0.00,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default learning modules
INSERT INTO learning_modules (id, title, description, icon, color_from, color_to, total_lessons, estimated_hours, difficulty_level, sort_order) VALUES
(1, 'Learn the Alphabet', 'Animated letters, matching games & sign gestures', '🔤', 'amber-200', 'pink-200', 20, 3.5, 'beginner', 1),
(2, 'Words & Meanings', 'Picture cards, audio pronunciation & memory play', '🧠', 'sky-200', 'indigo-200', 15, 2.8, 'beginner', 2),
(3, 'Sentence Formation', 'Drag-and-drop puzzles & grammar hints', '🧩', 'pink-200', 'amber-200', 12, 2.2, 'intermediate', 3),
(4, 'Sign & Gesture Practice', 'Webcam-guided practice & feedback', '🤟', 'indigo-200', 'sky-200', 18, 4.0, 'intermediate', 4),
(5, 'Storytelling & Communication', 'Interactive stories & role-play', '📖', 'amber-200', 'indigo-200', 10, 3.2, 'intermediate', 5),
(6, 'Basic Math & Logic', 'Number games & visual logic challenges', '➗', 'green-200', 'amber-200', 14, 2.5, 'beginner', 6)
ON DUPLICATE KEY UPDATE
title = VALUES(title),
description = VALUES(description),
icon = VALUES(icon),
total_lessons = VALUES(total_lessons),
estimated_hours = VALUES(estimated_hours);