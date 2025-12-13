-- Course Management System Database Schema
-- Run this to create the necessary tables for the learning management system

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    title_hindi VARCHAR(255),
    description TEXT,
    level ENUM('foundation', 'beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    duration_hours INT DEFAULT 0,
    total_modules INT DEFAULT 0,
    category VARCHAR(100) DEFAULT 'general',
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_category (category),
    INDEX idx_active (is_active)
);

-- Modules table
CREATE TABLE IF NOT EXISTS modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    title_hindi VARCHAR(255),
    description TEXT,
    module_order INT NOT NULL,
    duration_minutes INT DEFAULT 0,
    content_type ENUM('lesson', 'quiz', 'practice', 'video', 'interactive') DEFAULT 'lesson',
    content_data JSON,
    prerequisites JSON,
    is_locked BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_course_order (course_id, module_order),
    INDEX idx_active (is_active)
);

-- User course progress tracking
CREATE TABLE IF NOT EXISTS user_course_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    modules_completed INT DEFAULT 0,
    total_modules INT DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    time_spent_minutes INT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_completed BOOLEAN DEFAULT FALSE,
    completion_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_course (user_id, course_id),
    INDEX idx_user_progress (user_id, progress_percentage),
    INDEX idx_completion (is_completed, completion_date)
);

-- User module progress tracking
CREATE TABLE IF NOT EXISTS user_module_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    module_id INT NOT NULL,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    time_spent_minutes INT DEFAULT 0,
    quiz_score DECIMAL(5,2) NULL,
    quiz_attempts INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    completion_date TIMESTAMP NULL,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_module (user_id, module_id),
    INDEX idx_user_progress (user_id, progress_percentage),
    INDEX idx_completion (is_completed, completion_date),
    INDEX idx_last_accessed (last_accessed)
);

-- Quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    questions_data JSON NOT NULL,
    passing_score DECIMAL(5,2) DEFAULT 70.00,
    time_limit_minutes INT DEFAULT 30,
    max_attempts INT DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
    INDEX idx_module (module_id),
    INDEX idx_active (is_active)
);

-- Quiz attempts table
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    quiz_id INT NOT NULL,
    answers_data JSON NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    INDEX idx_user_quiz (user_id, quiz_id),
    INDEX idx_score (score),
    INDEX idx_completed (completed_at)
);

-- Learning streaks table
CREATE TABLE IF NOT EXISTS learning_streaks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    streak_date DATE NOT NULL,
    modules_completed INT DEFAULT 0,
    time_spent_minutes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, streak_date),
    INDEX idx_user_streak (user_id, streak_date)
);

-- Insert default courses
INSERT INTO courses (title, title_hindi, description, level, duration_hours, total_modules, category, sort_order) VALUES
('Learn the Alphabet', 'वर्णमाला सीखें', 'Animated letters, matching games & sign gestures to build the foundation for early readers.', 'beginner', 4, 6, 'language', 1),
('Words & Meanings', 'शब्द और अर्थ', 'Picture cards, audio pronunciation, and memory play for expanding vocabulary.', 'beginner', 3, 8, 'vocabulary', 2),
('Sentence Formation', 'वाक्य निर्माण', 'Drag-and-drop sentence puzzles, grammar hints and practice dialogues.', 'intermediate', 2, 5, 'grammar', 3),
('Sign & Gesture Practice', 'सांकेतिक अभ्यास', 'Webcam-guided practice, slow-motion replay and feedback prompts for ISL gestures.', 'intermediate', 4, 10, 'practice', 4),
('Storytelling & Communication', 'कहानी और संवाद', 'Interactive story prompts, role-play and expressive language tasks to encourage confidence.', 'intermediate', 3, 7, 'communication', 5),
('Basic Math & Logic', 'गणित और तर्क', 'Number games, puzzles and visual logic challenges for developing thinking skills.', 'beginner', 3, 6, 'math', 6);

-- Insert sample modules for Course 1 (Learn the Alphabet)
INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data) VALUES
(1, 'Letters A-E', 'अक्षर अ-ए', 'Learn the first five letters of the alphabet with interactive exercises', 1, 45, 'interactive', '{"letters": ["A", "B", "C", "D", "E"], "exercises": ["recognition", "writing", "pronunciation"]}'),
(1, 'Letters F-J', 'अक्षर फ-ज', 'Continue with letters F through J', 2, 45, 'interactive', '{"letters": ["F", "G", "H", "I", "J"], "exercises": ["recognition", "writing", "pronunciation"]}'),
(1, 'Letters K-O', 'अक्षर क-ओ', 'Learn letters K through O', 3, 45, 'interactive', '{"letters": ["K", "L", "M", "N", "O"], "exercises": ["recognition", "writing", "pronunciation"]}'),
(1, 'Letters P-T', 'अक्षर प-त', 'Practice letters P through T', 4, 45, 'interactive', '{"letters": ["P", "Q", "R", "S", "T"], "exercises": ["recognition", "writing", "pronunciation"]}'),
(1, 'Letters U-Z', 'अक्षर उ-ज़', 'Complete the alphabet with U through Z', 5, 45, 'interactive', '{"letters": ["U", "V", "W", "X", "Y", "Z"], "exercises": ["recognition", "writing", "pronunciation"]}'),
(1, 'Alphabet Review Quiz', 'वर्णमाला समीक्षा प्रश्नोत्तरी', 'Test your knowledge of all 26 letters', 6, 30, 'quiz', '{"quiz_type": "alphabet_review", "question_count": 26}');

-- Insert sample quiz for the first module
INSERT INTO quizzes (module_id, title, questions_data, passing_score, time_limit_minutes, max_attempts) VALUES
(1, 'Letters A-E Quiz', '[
    {
        "question": "Which letter comes after A?",
        "options": ["B", "C", "D", "E"],
        "correct": 0,
        "type": "multiple_choice"
    },
    {
        "question": "What sound does the letter C make?",
        "options": ["Ka", "Sa", "Cha", "Ta"],
        "correct": 1,
        "type": "multiple_choice"
    },
    {
        "question": "Which letter looks like a door?",
        "options": ["A", "B", "D", "E"],
        "correct": 2,
        "type": "multiple_choice"
    }
]', 70.00, 15, 3);