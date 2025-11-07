-- ==========================================================
-- RESET DATABASE: SIGN LANGUAGE LEARNING PLATFORM
-- ==========================================================

-- Tắt kiểm tra foreign key (MySQL)
SET FOREIGN_KEY_CHECKS = 0;

-- Xóa dữ liệu bảng con trước
DELETE FROM users_aisessionlog;
DELETE FROM users_usertest;
DELETE FROM users_userflashcard;
DELETE FROM users_aisession;
DELETE FROM users_reminder;

-- Xóa dữ liệu bảng chính
DELETE FROM users_testquestion;
DELETE FROM users_flashcard;
DELETE FROM users_topic;

-- Reset auto_increment
ALTER TABLE users_topic AUTO_INCREMENT = 1;
ALTER TABLE users_flashcard AUTO_INCREMENT = 1;
ALTER TABLE users_testquestion AUTO_INCREMENT = 1;
ALTER TABLE users_userflashcard AUTO_INCREMENT = 1;
ALTER TABLE users_usertest AUTO_INCREMENT = 1;
ALTER TABLE users_aisession AUTO_INCREMENT = 1;
ALTER TABLE users_aisessionlog AUTO_INCREMENT = 1;
ALTER TABLE users_reminder AUTO_INCREMENT = 1;

-- Bật lại kiểm tra foreign key
SET FOREIGN_KEY_CHECKS = 1;

-- ==========================================================
-- DATABASE SEED DATA
-- ==========================================================

-- ==============
-- 1. TOPICS
-- ==============
INSERT INTO users_topic (id, title, description, created_at)
VALUES
(1, 'Bảng chữ cái ngôn ngữ ký hiệu', 'Học cách biểu diễn từng chữ cái A–Z bằng tay.', NOW()),
(2, 'Số đếm bằng ký hiệu', 'Học cách biểu diễn các số 0–9 bằng tay.', NOW()),
(3, 'Cảm xúc và lời chào', 'Các ký hiệu thể hiện cảm xúc và lời chào cơ bản.', NOW());

-- ==============
-- 2. FLASHCARDS
-- ==============
INSERT INTO users_flashcard (id, topic_id, front_text, back_text, image_url)
VALUES
(1, 1, 'A', 'Ký hiệu chữ A trong ngôn ngữ ký hiệu.', 'https://example.com/sign_a.jpg'),
(2, 1, 'B', 'Ký hiệu chữ B trong ngôn ngữ ký hiệu.', 'https://example.com/sign_b.jpg'),
(3, 2, '1', 'Ký hiệu số 1 – giơ ngón trỏ.', 'https://example.com/sign_1.jpg'),
(4, 2, '5', 'Ký hiệu số 5 – xòe cả bàn tay.', 'https://example.com/sign_5.jpg'),
(5, 3, 'Xin chào', 'Đưa tay từ cằm ra ngoài.', 'https://example.com/sign_hello.jpg'),
(6, 3, 'Cảm ơn', 'Chạm tay vào cằm và đưa ra ngoài.', 'https://example.com/sign_thanks.jpg');

-- ==============
-- 3. USER_FLASHCARDS
-- ==============
INSERT INTO users_userflashcard (id, user_id, flashcard_id, learned, last_reviewed, correct_count, wrong_count)
VALUES
(1, 'aFH57', 1, TRUE, NOW(), 3, 0),
(2, 'aFH57', 2, TRUE, NOW(), 2, 1),
(3, '2NJj1', 3, FALSE, NULL, 0, 0),
(4, '2NJj1', 6, TRUE, NOW(), 1, 0);

-- ==============
-- 4. TEST_QUESTIONS
-- ==============
INSERT INTO users_testquestion (id, topic_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(1, 1, 'Ký hiệu nào thể hiện chữ A?', 'Nắm tay lại', 'Giơ hai ngón tay', 'Đưa tay ra', 'Bẻ cong ngón cái', 'A'),
(2, 2, 'Ký hiệu nào thể hiện số 5?', 'Giơ ngón trỏ', 'Giơ cả bàn tay', 'Nắm tay lại', 'Giơ hai ngón', 'B'),
(3, 3, 'Ký hiệu "Cảm ơn" được thực hiện như thế nào?', 'Giơ tay lên cao', 'Đưa tay từ cằm ra ngoài', 'Vỗ tay', 'Chạm mũi', 'B');

-- ==============
-- 5. USER_TESTS
-- ==============
INSERT INTO users_usertest (id, user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
(1, 'aFH57', 1, 'A', TRUE, NOW()),
(2, 'aFH57', 2, 'A', FALSE, NOW()),
(3, '2NJj1', 3, 'B', TRUE, NOW());

-- ==============
-- 6. AI_SESSIONS
-- ==============
INSERT INTO users_aisession (id, user_id, start_time, end_time, result_summary, feedback)
VALUES
(1, 'aFH57', NOW() - INTERVAL 15 MINUTE, NOW(), 'Độ chính xác: 92%', 'Nhận diện chính xác các ký hiệu A, B, và 5. Cần luyện thêm phần "Cảm ơn".'),
(2, '2NJj1', NOW() - INTERVAL 10 MINUTE, NOW(), 'Độ chính xác: 85%', 'Cần giữ tay ổn định hơn khi ký hiệu các chữ cái.');

-- ==============
-- 7. AI_SESSION_LOGS
-- ==============
INSERT INTO users_aisessionlog (id, session_id, frame_time, recognized_symbol, expected_symbol, is_correct, ai_explanation)
VALUES
(1, 1, NOW(), 'A', 'A', TRUE, 'Nhận diện chính xác hình dạng bàn tay.'),
(2, 1, NOW(), 'B', 'B', TRUE, 'Góc nghiêng tay hợp lệ.'),
(3, 1, NOW(), 'C', 'C', FALSE, 'Ngón cái chưa cong đủ để tạo thành hình chữ C.'),
(4, 2, NOW(), '1', '1', TRUE, 'Đúng ký hiệu số 1.'),
(5, 2, NOW(), '5', '5', TRUE, 'Bàn tay mở hoàn chỉnh.');

-- ==============
-- 8. REMINDERS
-- ==============
INSERT INTO users_reminder (id, user_id, topic_id, message, scheduled_time, is_sent)
VALUES
(1, 'aFH57', 1, 'Ôn lại ký hiệu chữ A–B lúc 19:00 tối nay nhé!', NOW() + INTERVAL 1 HOUR, FALSE),
(2, '2NJj1', 3, 'Đừng quên luyện tập phần "Cảm ơn" trước khi đi ngủ!', NOW() + INTERVAL 2 HOUR, FALSE);
