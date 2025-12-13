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

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data, prerequisites, is_locked, is_active) VALUES
(2, 'Basic Nouns', 'मूल संज्ञा', 'Learn common household items, family members, and everyday objects', 1, 30, 'interactive', '{"words": ["house", "family", "mother", "father", "book", "water"], "exercises": ["picture_match", "pronunciation", "spelling"]}', '[]', 0, 1),
(2, 'Action Words', 'क्रिया शब्द', 'Discover verbs and action words through animations', 2, 35, 'interactive', '{"words": ["run", "walk", "eat", "drink", "read", "write"], "exercises": ["action_match", "sentence_build"]}', '[7]', 1, 1),
(2, 'Colors & Shapes', 'रंग और आकार', 'Learn colors and basic shapes with visual exercises', 3, 25, 'interactive', '{"colors": ["red", "blue", "green", "yellow"], "shapes": ["circle", "square", "triangle"], "exercises": ["color_match", "shape_identify"]}', '[8]', 1, 1),
(2, 'Numbers & Counting', 'संख्या और गिनती', 'Master numbers 1-20 with counting games', 4, 40, 'interactive', '{"numbers": "1-20", "exercises": ["counting", "number_match", "simple_math"]}', '[9]', 1, 1),
(2, 'Body Parts', 'शरीर के अंग', 'Identify and name different body parts', 5, 30, 'interactive', '{"body_parts": ["head", "hand", "foot", "eye", "nose", "mouth"], "exercises": ["body_map", "pronunciation"]}', '[10]', 1, 1),
(2, 'Food & Drinks', 'खाना और पेय', 'Learn vocabulary related to food and beverages', 6, 35, 'interactive', '{"food": ["rice", "bread", "milk", "fruit", "vegetable"], "exercises": ["food_match", "healthy_choices"]}', '[11]', 1, 1),
(2, 'Animals & Nature', 'जानवर और प्रकृति', 'Explore animals and nature vocabulary', 7, 30, 'interactive', '{"animals": ["cat", "dog", "bird", "tree", "flower"], "exercises": ["animal_sounds", "habitat_match"]}', '[12]', 1, 1),
(2, 'Vocabulary Review', 'शब्दावली समीक्षा', 'Comprehensive review of all learned words', 8, 45, 'quiz', '{"quiz_type": "comprehensive", "question_count": 25}', '[13]', 1, 1);

-- =============================================
-- COURSE 3: Sentence Formation (5 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data, prerequisites, is_locked, is_active) VALUES
(3, 'Basic Sentence Structure', 'मूल वाक्य संरचना', 'Learn Subject + Verb + Object pattern', 1, 40, 'interactive', '{"patterns": ["SVO"], "examples": ["I eat food", "She reads book"], "exercises": ["sentence_build", "pattern_match"]}', '[]', 0, 1),
(3, 'Questions & Answers', 'प्रश्न और उत्तर', 'Form questions and provide appropriate answers', 2, 35, 'interactive', '{"question_words": ["what", "where", "when", "who"], "exercises": ["question_form", "answer_match"]}', '[15]', 1, 1),
(3, 'Describing Things', 'वस्तुओं का वर्णन', 'Use adjectives to describe objects and people', 3, 30, 'interactive', '{"adjectives": ["big", "small", "red", "happy"], "exercises": ["description_build", "adjective_match"]}', '[16]', 1, 1),
(3, 'Time & Place', 'समय और स्थान', 'Express when and where things happen', 4, 35, 'interactive', '{"time_words": ["today", "yesterday", "morning"], "place_words": ["here", "there", "home"], "exercises": ["time_place_sentences"]}', '[17]', 1, 1),
(3, 'Sentence Mastery', 'वाक्य निपुणता', 'Create complex sentences with confidence', 5, 40, 'quiz', '{"quiz_type": "sentence_formation", "question_count": 20}', '[18]', 1, 1);

-- =============================================
-- COURSE 4: Sign & Gesture Practice (10 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data, prerequisites, is_locked, is_active) VALUES
(4, 'Hand Positions', 'हाथ की स्थिति', 'Learn basic hand shapes and positions for ISL', 1, 25, 'practice', '{"hand_shapes": ["flat", "fist", "point", "cup"], "exercises": ["shape_practice", "position_hold"]}', '[]', 0, 1),
(4, 'ISL Alphabet A-E', 'ISL वर्णमाला अ-ए', 'Master the first five letters in ISL', 2, 30, 'practice', '{"letters": ["A", "B", "C", "D", "E"], "exercises": ["letter_practice", "recognition_test"]}', '[20]', 1, 1),
(4, 'ISL Alphabet F-J', 'ISL वर्णमाला फ-ज', 'Continue with letters F through J', 3, 30, 'practice', '{"letters": ["F", "G", "H", "I", "J"], "exercises": ["letter_practice", "recognition_test"]}', '[21]', 1, 1),
(4, 'ISL Alphabet K-O', 'ISL वर्णमाला क-ओ', 'Practice letters K through O', 4, 30, 'practice', '{"letters": ["K", "L", "M", "N", "O"], "exercises": ["letter_practice", "recognition_test"]}', '[22]', 1, 1),
(4, 'ISL Alphabet P-T', 'ISL वर्णमाला प-त', 'Learn letters P through T', 5, 30, 'practice', '{"letters": ["P", "Q", "R", "S", "T"], "exercises": ["letter_practice", "recognition_test"]}', '[23]', 1, 1),
(4, 'ISL Alphabet U-Z', 'ISL वर्णमाला उ-ज़', 'Complete the ISL alphabet', 6, 30, 'practice', '{"letters": ["U", "V", "W", "X", "Y", "Z"], "exercises": ["letter_practice", "recognition_test"]}', '[24]', 1, 1),
(4, 'Numbers 0-9', 'संख्या 0-9', 'Learn ISL number signs', 7, 35, 'practice', '{"numbers": "0-9", "exercises": ["number_practice", "counting_signs"]}', '[25]', 1, 1),
(4, 'Common Words', 'सामान्य शब्द', 'Practice signs for everyday words', 8, 40, 'practice', '{"words": ["hello", "thank you", "please", "sorry"], "exercises": ["word_practice", "conversation"]}', '[26]', 1, 1),
(4, 'Simple Sentences', 'सरल वाक्य', 'Combine signs to form basic sentences', 9, 45, 'practice', '{"sentences": ["I am happy", "What is your name"], "exercises": ["sentence_signing", "conversation_practice"]}', '[27]', 1, 1),
(4, 'ISL Assessment', 'ISL मूल्यांकन', 'Comprehensive ISL skills assessment', 10, 50, 'quiz', '{"quiz_type": "isl_comprehensive", "question_count": 30}', '[28]', 1, 1);

-- =============================================
-- COURSE 5: Storytelling & Communication (7 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data, prerequisites, is_locked, is_active) VALUES
(5, 'Story Elements', 'कहानी के तत्व', 'Learn about characters, setting, and plot', 1, 35, 'interactive', '{"elements": ["character", "setting", "plot"], "exercises": ["element_identify", "story_map"]}', '[]', 0, 1),
(5, 'Character Creation', 'पात्र निर्माण', 'Create interesting characters with personalities', 2, 40, 'interactive', '{"traits": ["brave", "kind", "funny", "smart"], "exercises": ["character_build", "trait_match"]}', '[30]', 1, 1),
(5, 'Setting the Scene', 'दृश्य निर्धारण', 'Describe when and where stories take place', 3, 30, 'interactive', '{"settings": ["forest", "city", "home", "school"], "exercises": ["scene_describe", "setting_match"]}', '[31]', 1, 1),
(5, 'Plot Development', 'कथानक विकास', 'Build exciting story plots with beginning, middle, end', 4, 45, 'interactive', '{"plot_points": ["beginning", "problem", "solution", "ending"], "exercises": ["plot_sequence", "story_build"]}', '[32]', 1, 1),
(5, 'Dialogue Writing', 'संवाद लेखन', 'Write conversations between characters', 5, 35, 'interactive', '{"dialogue_types": ["greeting", "question", "emotion"], "exercises": ["dialogue_create", "conversation_practice"]}', '[33]', 1, 1),
(5, 'Story Presentation', 'कहानी प्रस्तुति', 'Present stories with confidence and expression', 6, 40, 'practice', '{"presentation_skills": ["voice", "gesture", "expression"], "exercises": ["story_tell", "audience_engage"]}', '[34]', 1, 1),
(5, 'Creative Writing', 'रचनात्मक लेखन', 'Create original stories and share them', 7, 50, 'quiz', '{"quiz_type": "creative_story", "question_count": 15}', '[35]', 1, 1);

-- =============================================
-- COURSE 6: Basic Math & Logic (6 modules)
-- =============================================

INSERT INTO modules (course_id, title, title_hindi, description, module_order, duration_minutes, content_type, content_data, prerequisites, is_locked, is_active) VALUES
(6, 'Number Recognition', 'संख्या पहचान', 'Recognize and write numbers 1-100', 1, 30, 'interactive', '{"numbers": "1-100", "exercises": ["number_write", "number_sequence", "number_match"]}', '[]', 0, 1),
(6, 'Counting & Ordering', 'गिनती और क्रम', 'Count objects and arrange numbers in order', 2, 35, 'interactive', '{"counting": "1-50", "exercises": ["object_count", "number_order", "skip_count"]}', '[37]', 1, 1),
(6, 'Addition Basics', 'जोड़ की मूल बातें', 'Learn to add numbers using visual aids', 3, 40, 'interactive', '{"addition": "single_digit", "exercises": ["visual_add", "number_line", "word_problems"]}', '[38]', 1, 1),
(6, 'Subtraction Basics', 'घटाव की मूल बातें', 'Understand subtraction with hands-on activities', 4, 40, 'interactive', '{"subtraction": "single_digit", "exercises": ["visual_subtract", "take_away", "word_problems"]}', '[39]', 1, 1),
(6, 'Shapes & Patterns', 'आकार और पैटर्न', 'Identify shapes and complete patterns', 5, 35, 'interactive', '{"shapes": ["circle", "square", "triangle", "rectangle"], "exercises": ["shape_identify", "pattern_complete", "shape_sort"]}', '[40]', 1, 1),
(6, 'Math Challenge', 'गणित चुनौती', 'Apply all math skills in fun challenges', 6, 45, 'quiz', '{"quiz_type": "math_comprehensive", "question_count": 25}', '[41]', 1, 1);