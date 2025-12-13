-- Populate Modules and Quizzes for All Courses
-- This script creates comprehensive modules and quizzes for the LMS platform

-- Clear existing modules and quizzes (except course 1 which already has some)
DELETE FROM quiz_attempts WHERE quiz_id IN (SELECT id FROM quizzes WHERE module_id > 6);
DELETE FROM quizzes WHERE module_id > 6;
DELETE FROM user_module_progress WHERE module_id > 6;
DELETE FROM modules WHERE id > 6;

-- =============================================
-- COURSE 2: Words & Meanings (8 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data) VALUES
(2, 'Basic Nouns', 'मूल संज्ञा', 'Learn common household items, family members, and everyday objects', 1, 30, 'interactive', '{"words": ["house", "family", "mother", "father", "book", "water"], "exercises": ["picture_match", "pronunciation", "spelling"]}'),
(2, 'Action Words', 'क्रिया शब्द', 'Discover verbs and action words through animations', 2, 35, 'interactive', '{"words": ["run", "walk", "eat", "drink", "read", "write"], "exercises": ["action_match", "sentence_build"]}'),
(2, 'Colors & Shapes', 'रंग और आकार', 'Learn colors and basic shapes with visual exercises', 3, 25, 'interactive', '{"colors": ["red", "blue", "green", "yellow"], "shapes": ["circle", "square", "triangle"], "exercises": ["color_match", "shape_identify"]}'),
(2, 'Numbers & Counting', 'संख्या और गिनती', 'Master numbers 1-20 with counting games', 4, 40, 'interactive', '{"numbers": "1-20", "exercises": ["counting", "number_match", "simple_math"]}'),
(2, 'Body Parts', 'शरीर के अंग', 'Identify and name different body parts', 5, 30, 'interactive', '{"body_parts": ["head", "hand", "foot", "eye", "nose", "mouth"], "exercises": ["body_map", "pronunciation"]}'),
(2, 'Food & Drinks', 'खाना और पेय', 'Learn vocabulary related to food and beverages', 6, 35, 'interactive', '{"food": ["rice", "bread", "milk", "fruit", "vegetable"], "exercises": ["food_match", "healthy_choices"]}'),
(2, 'Animals & Nature', 'जानवर और प्रकृति', 'Explore animals and nature vocabulary', 7, 30, 'interactive', '{"animals": ["cat", "dog", "bird", "tree", "flower"], "exercises": ["animal_sounds", "habitat_match"]}'),
(2, 'Vocabulary Review', 'शब्दावली समीक्षा', 'Comprehensive review of all learned words', 8, 45, 'quiz', '{"quiz_type": "comprehensive", "question_count": 25}');

-- =============================================
-- COURSE 3: Sentence Formation (5 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data) VALUES
(3, 'Basic Sentence Structure', 'मूल वाक्य संरचना', 'Learn Subject + Verb + Object pattern', 1, 40, 'interactive', '{"patterns": ["SVO"], "examples": ["I eat food", "She reads book"], "exercises": ["sentence_build", "pattern_match"]}'),
(3, 'Questions & Answers', 'प्रश्न और उत्तर', 'Form questions and provide appropriate answers', 2, 35, 'interactive', '{"question_words": ["what", "where", "when", "who"], "exercises": ["question_form", "answer_match"]}'),
(3, 'Describing Things', 'वस्तुओं का वर्णन', 'Use adjectives to describe objects and people', 3, 30, 'interactive', '{"adjectives": ["big", "small", "red", "happy"], "exercises": ["description_build", "adjective_match"]}'),
(3, 'Time & Place', 'समय और स्थान', 'Express when and where things happen', 4, 35, 'interactive', '{"time_words": ["today", "yesterday", "morning"], "place_words": ["here", "there", "home"], "exercises": ["time_place_sentences"]}'),
(3, 'Sentence Mastery', 'वाक्य निपुणता', 'Create complex sentences with confidence', 5, 40, 'quiz', '{"quiz_type": "sentence_formation", "question_count": 20}');

-- =============================================
-- COURSE 4: Sign & Gesture Practice (10 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_data) VALUES
(4, 'Hand Positions', 'हाथ की स्थिति', 'Learn basic hand shapes and positions for ISL', 1, 25, 'practice', '{"hand_shapes": ["flat", "fist", "point", "cup"], "exercises": ["shape_practice", "position_hold"]}'),
(4, 'ISL Alphabet A-E', 'ISL वर्णमाला अ-ए', 'Master the first five letters in ISL', 2, 30, 'practice', '{"letters": ["A", "B", "C", "D", "E"], "exercises": ["letter_practice", "recognition_test"]}'),
(4, 'ISL Alphabet F-J', 'ISL वर्णमाला फ-ज', 'Continue with letters F through J', 3, 30, 'practice', '{"letters": ["F", "G", "H", "I", "J"], "exercises": ["letter_practice", "recognition_test"]}'),
(4, 'ISL Alphabet K-O', 'ISL वर्णमाला क-ओ', 'Practice letters K through O', 4, 30, 'practice', '{"letters": ["K", "L", "M", "N", "O"], "exercises": ["letter_practice", "recognition_test"]}'),
(4, 'ISL Alphabet P-T', 'ISL वर्णमाला प-त', 'Learn letters P through T', 5, 30, 'practice', '{"letters": ["P", "Q", "R", "S", "T"], "exercises": ["letter_practice", "recognition_test"]}'),
(4, 'ISL Alphabet U-Z', 'ISL वर्णमाला उ-ज़', 'Complete the ISL alphabet', 6, 30, 'practice', '{"letters": ["U", "V", "W", "X", "Y", "Z"], "exercises": ["letter_practice", "recognition_test"]}'),
(4, 'Numbers 0-9', 'संख्या 0-9', 'Learn ISL number signs', 7, 35, 'practice', '{"numbers": "0-9", "exercises": ["number_practice", "counting_signs"]}'),
(4, 'Common Words', 'सामान्य शब्द', 'Practice signs for everyday words', 8, 40, 'practice', '{"words": ["hello", "thank you", "please", "sorry"], "exercises": ["word_practice", "conversation"]}'),
(4, 'Simple Sentences', 'सरल वाक्य', 'Combine signs to form basic sentences', 9, 45, 'practice', '{"sentences": ["I am happy", "What is your name"], "exercises": ["sentence_signing", "conversation_practice"]}'),
(4, 'ISL Assessment', 'ISL मूल्यांकन', 'Comprehensive ISL skills assessment', 10, 50, 'quiz', '{"quiz_type": "isl_comprehensive", "question_count": 30}');

-- =============================================
-- COURSE 5: Storytelling & Communication (7 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data) VALUES
(5, 'Story Elements', 'कहानी के तत्व', 'Learn about characters, setting, and plot', 1, 35, 'interactive', '{"elements": ["character", "setting", "plot"], "exercises": ["element_identify", "story_map"]}'),
(5, 'Character Creation', 'पात्र निर्माण', 'Create interesting characters with personalities', 2, 40, 'interactive', '{"traits": ["brave", "kind", "funny", "smart"], "exercises": ["character_build", "trait_match"]}'),
(5, 'Setting the Scene', 'दृश्य निर्धारण', 'Describe when and where stories take place', 3, 30, 'interactive', '{"settings": ["forest", "city", "home", "school"], "exercises": ["scene_describe", "setting_match"]}'),
(5, 'Plot Development', 'कथानक विकास', 'Build exciting story plots with beginning, middle, end', 4, 45, 'interactive', '{"plot_points": ["beginning", "problem", "solution", "ending"], "exercises": ["plot_sequence", "story_build"]}'),
(5, 'Dialogue Writing', 'संवाद लेखन', 'Write conversations between characters', 5, 35, 'interactive', '{"dialogue_types": ["greeting", "question", "emotion"], "exercises": ["dialogue_create", "conversation_practice"]}'),
(5, 'Story Presentation', 'कहानी प्रस्तुति', 'Present stories with confidence and expression', 6, 40, 'practice', '{"presentation_skills": ["voice", "gesture", "expression"], "exercises": ["story_tell", "audience_engage"]}'),
(5, 'Creative Writing', 'रचनात्मक लेखन', 'Create original stories and share them', 7, 50, 'quiz', '{"quiz_type": "creative_story", "question_count": 15}');

-- =============================================
-- COURSE 6: Basic Math & Logic (6 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data) VALUES
(6, 'Number Recognition', 'संख्या पहचान', 'Recognize and write numbers 1-100', 1, 30, 'interactive', '{"numbers": "1-100", "exercises": ["number_write", "number_sequence", "number_match"]}'),
(6, 'Counting & Ordering', 'गिनती और क्रम', 'Count objects and arrange numbers in order', 2, 35, 'interactive', '{"counting": "1-50", "exercises": ["object_count", "number_order", "skip_count"]}'),
(6, 'Addition Basics', 'जोड़ की मूल बातें', 'Learn to add numbers using visual aids', 3, 40, 'interactive', '{"addition": "single_digit", "exercises": ["visual_add", "number_line", "word_problems"]}'),
(6, 'Subtraction Basics', 'घटाव की मूल बातें', 'Understand subtraction with hands-on activities', 4, 40, 'interactive', '{"subtraction": "single_digit", "exercises": ["visual_subtract", "take_away", "word_problems"]}'),
(6, 'Shapes & Patterns', 'आकार और पैटर्न', 'Identify shapes and complete patterns', 5, 35, 'interactive', '{"shapes": ["circle", "square", "triangle", "rectangle"], "exercises": ["shape_identify", "pattern_complete", "shape_sort"]}'),
(6, 'Math Challenge', 'गणित चुनौती', 'Apply all math skills in fun challenges', 6, 45, 'quiz', '{"quiz_type": "math_comprehensive", "question_count": 25}');

-- =============================================
-- CREATE QUIZZES FOR ALL MODULES
-- =============================================

-- Course 2 Quizzes
INSERT INTO quizzes (module_id, title, questions_data, passing_score, time_limit_minutes, max_attempts) VALUES
((SELECT id FROM modules WHERE course_id = 2 AND module_order = 1), 'Basic Nouns Quiz', '[
    {"question": "What do you call the place where you live?", "options": ["House", "Car", "Tree", "Book"], "correct": 0, "type": "multiple_choice"},
    {"question": "Who takes care of you at home?", "options": ["Teacher", "Mother", "Doctor", "Friend"], "correct": 1, "type": "multiple_choice"},
    {"question": "What do you use to read stories?", "options": ["Spoon", "Ball", "Book", "Shoe"], "correct": 2, "type": "multiple_choice"}
]', 70.00, 10, 3),

((SELECT id FROM modules WHERE course_id = 2 AND module_order = 2), 'Action Words Quiz', '[
    {"question": "What do you do with your legs to move fast?", "options": ["Eat", "Run", "Sleep", "Read"], "correct": 1, "type": "multiple_choice"},
    {"question": "What do you do with food?", "options": ["Eat", "Throw", "Break", "Hide"], "correct": 0, "type": "multiple_choice"},
    {"question": "What do you do with a book?", "options": ["Eat", "Wear", "Read", "Drink"], "correct": 2, "type": "multiple_choice"}
]', 70.00, 10, 3),

((SELECT id FROM modules WHERE course_id = 2 AND module_order = 3), 'Colors & Shapes Quiz', '[
    {"question": "What color is the sun?", "options": ["Blue", "Yellow", "Green", "Purple"], "correct": 1, "type": "multiple_choice"},
    {"question": "How many sides does a triangle have?", "options": ["2", "3", "4", "5"], "correct": 1, "type": "multiple_choice"},
    {"question": "What shape is a ball?", "options": ["Square", "Triangle", "Circle", "Rectangle"], "correct": 2, "type": "multiple_choice"}
]', 70.00, 10, 3);

-- Course 3 Quizzes
INSERT INTO quizzes (module_id, title, questions_data, passing_score, time_limit_minutes, max_attempts) VALUES
((SELECT id FROM modules WHERE course_id = 3 AND module_order = 1), 'Basic Sentence Structure Quiz', '[
    {"question": "Complete the sentence: I ___ food.", "options": ["eat", "food", "am", "the"], "correct": 0, "type": "multiple_choice"},
    {"question": "What comes first in a sentence?", "options": ["Verb", "Object", "Subject", "Adjective"], "correct": 2, "type": "multiple_choice"},
    {"question": "Which is a complete sentence?", "options": ["Running fast", "She sings", "Beautiful flower", "In the garden"], "correct": 1, "type": "multiple_choice"}
]', 70.00, 15, 3),

((SELECT id FROM modules WHERE course_id = 3 AND module_order = 2), 'Questions & Answers Quiz', '[
    {"question": "Which word is used to ask about a person?", "options": ["What", "Where", "Who", "When"], "correct": 2, "type": "multiple_choice"},
    {"question": "Complete the question: ___ is your name?", "options": ["What", "Where", "Who", "When"], "correct": 0, "type": "multiple_choice"},
    {"question": "Which is the correct answer to \"Where do you live?\"", "options": ["My name is John", "I live in Delhi", "I am 10 years old", "I like apples"], "correct": 1, "type": "multiple_choice"}
]', 70.00, 15, 3);

-- Course 4 Quizzes  
INSERT INTO quizzes (module_id, title, questions_data, passing_score, time_limit_minutes, max_attempts) VALUES
((SELECT id FROM modules WHERE course_id = 4 AND module_order = 1), 'Hand Positions Quiz', '[
    {"question": "Which hand shape is used for the letter A in ISL?", "options": ["Flat hand", "Closed fist", "Pointing finger", "Cup shape"], "correct": 1, "type": "multiple_choice"},
    {"question": "How should you hold your hand for clear ISL signs?", "options": ["Loosely", "Firmly and clearly", "Very tight", "Moving constantly"], "correct": 1, "type": "multiple_choice"},
    {"question": "What is the most important thing in ISL hand positions?", "options": ["Speed", "Clarity", "Size", "Color"], "correct": 1, "type": "multiple_choice"}
]', 80.00, 10, 3);

-- Course 5 Quizzes
INSERT INTO quizzes (module_id, title, questions_data, passing_score, time_limit_minutes, max_attempts) VALUES
((SELECT id FROM modules WHERE course_id = 5 AND module_order = 1), 'Story Elements Quiz', '[
    {"question": "What are the main parts of a story?", "options": ["Beginning, middle, end", "Characters only", "Setting only", "Plot only"], "correct": 0, "type": "multiple_choice"},
    {"question": "Who are the people in a story called?", "options": ["Settings", "Plots", "Characters", "Themes"], "correct": 2, "type": "multiple_choice"},
    {"question": "Where and when a story happens is called?", "options": ["Character", "Plot", "Theme", "Setting"], "correct": 3, "type": "multiple_choice"}
]', 70.00, 15, 3);

-- Course 6 Quizzes
INSERT INTO quizzes (module_id, title, questions_data, passing_score, time_limit_minutes, max_attempts) VALUES
((SELECT id FROM modules WHERE course_id = 6 AND module_order = 1), 'Number Recognition Quiz', '[
    {"question": "What number comes after 9?", "options": ["8", "10", "11", "9"], "correct": 1, "type": "multiple_choice"},
    {"question": "Which is the smallest number?", "options": ["5", "1", "3", "7"], "correct": 1, "type": "multiple_choice"},
    {"question": "How do you write the number twenty?", "options": ["2", "12", "20", "200"], "correct": 2, "type": "multiple_choice"}
]', 70.00, 10, 3),

((SELECT id FROM modules WHERE course_id = 6 AND module_order = 3), 'Addition Basics Quiz', '[
    {"question": "What is 2 + 3?", "options": ["4", "5", "6", "7"], "correct": 1, "type": "multiple_choice"},
    {"question": "If you have 3 apples and get 2 more, how many do you have?", "options": ["3", "2", "5", "1"], "correct": 2, "type": "multiple_choice"},
    {"question": "What is 1 + 1?", "options": ["1", "2", "3", "0"], "correct": 1, "type": "multiple_choice"}
]', 70.00, 15, 3);