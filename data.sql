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


INSERT INTO auth_user (
    id, password, last_login, is_superuser, username, first_name,
    last_name, email, is_staff, is_active, date_joined
)
VALUES
(1, 'pbkdf2_sha256$600000$YVJo98r3n2DP69mcQEMUoo$JRDcOJvHH3GeHQRtQuB3OoRhKmuhwWEqvoNqHq5S+LQ=', NULL, 0, 'testuser1', 'Test', 'User1', 'user1@example.com', 0, 1, NOW()),
(2, 'pbkdf2_sha256$600000$YVJo98r3n2DP69mcQEMUoo$JRDcOJvHH3GeHQRtQuB3OoRhKmuhwWEqvoNqHq5S+LQ=', NULL, 0, 'testuser2', 'Test', 'User2', 'user2@example.com', 0, 1, NOW()),
(3, 'pbkdf2_sha256$600000$YVJo98r3n2DP69mcQEMUoo$JRDcOJvHH3GeHQRtQuB3OoRhKmuhwWEqvoNqHq5S+LQ=', NULL, 0, 'testuser3', 'Test', 'User3', 'user3@example.com', 0, 1, NOW());

INSERT INTO users_customer (id, user_id, sex, date_of_birth)
VALUES
(1, 1, 'male', '2000-01-01'),
(2, 2, 'female', '2001-05-10'),
(3, 3, 'male', '1999-12-20');


-- ==============
-- 1. TOPICS
-- ==============
INSERT INTO users_topic (id, title, description, created_at)
VALUES
(1, 'Bảng chữ cái ngôn ngữ ký hiệu', 'Học cách biểu diễn từng chữ cái A–Z bằng tay.', NOW()),
(2, 'Số đếm bằng ký hiệu', 'Học cách biểu diễn các số 0–9 bằng tay.', NOW()),
(3, 'Cảm xúc và lời chào', 'Các ký hiệu thể hiện cảm xúc và lời chào cơ bản.', NOW());


INSERT INTO users_topic (id, title, description, created_at)
VALUES
(4, 'Động vật', 'Tên các loài động vật cơ bản bằng ký hiệu.', NOW()),
(5, 'Màu sắc', 'Các màu cơ bản được biểu diễn bằng tay.', NOW()),
(6, 'Đồ vật trong nhà', 'Các vật dụng quen thuộc trong gia đình.', NOW()),
(7, 'Hành động cơ bản', 'Các cử chỉ hành động thường dùng.', NOW());


-- ==============
-- 2. FLASHCARDS
-- ==============
INSERT INTO users_flashcard (id, topic_id, front_text, back_text, media)
VALUES
(1, 1, 'A', 'Ký hiệu chữ A trong ngôn ngữ ký hiệu.', 'https://example.com/sign_a.jpg'),
(2, 1, 'B', 'Ký hiệu chữ B trong ngôn ngữ ký hiệu.', 'https://example.com/sign_b.jpg'),
(3, 2, '1', 'Ký hiệu số 1 – giơ ngón trỏ.', 'https://example.com/sign_1.jpg'),
(4, 2, '5', 'Ký hiệu số 5 – xòe cả bàn tay.', 'https://example.com/sign_5.jpg'),
(5, 3, 'Xin chào', 'Đưa tay từ cằm ra ngoài.', 'https://example.com/sign_hello.jpg'),
(6, 3, 'Cảm ơn', 'Chạm tay vào cằm và đưa ra ngoài.', 'https://example.com/sign_thanks.jpg');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media)
VALUES
(1, 'C', 'Ký hiệu chữ C trong ngôn ngữ ký hiệu.', 'https://example.com/sign_c.jpg'),
(1, 'D', 'Ký hiệu chữ D trong ngôn ngữ ký hiệu.', 'https://example.com/sign_d.jpg'),
(1, 'E', 'Ký hiệu chữ E trong ngôn ngữ ký hiệu.', 'https://example.com/sign_e.jpg');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media)
VALUES
(2, '2', 'Ký hiệu số 2 – giơ hai ngón tay.', 'https://example.com/sign_2.jpg'),
(2, '3', 'Ký hiệu số 3 – giơ ba ngón tay.', 'https://example.com/sign_3.jpg'),
(2, '0', 'Ký hiệu số 0 – khép các ngón tạo vòng tròn.', 'https://example.com/sign_0.jpg');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media)
VALUES
(3, 'Xin lỗi', 'Xoa ngực theo vòng tròn.', 'https://example.com/sign_sorry.jpg'),
(3, 'Tạm biệt', 'Vẫy tay ra phía trước.', 'https://example.com/sign_bye.jpg'),
(3, 'Vui vẻ', 'Hai tay chỉ vào má và cười.', 'https://example.com/sign_happy.jpg');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media)
VALUES
(4, 'Mèo', 'Đưa tay làm động tác ria mèo.', 'https://example.com/sign_cat.jpg'),
(4, 'Chó', 'Vỗ nhẹ vào đùi và búng tay.', 'https://example.com/sign_dog.jpg'),
(4, 'Cá', 'Đưa bàn tay làm động tác bơi.', 'https://example.com/sign_fish.jpg'),
(4, 'Chim', 'Chụm 2 ngón tay làm mỏ chim.', 'https://example.com/sign_bird.jpg');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media)
VALUES
(5, 'Đỏ', 'Chạm lên môi để biểu thị màu đỏ.', 'https://example.com/sign_red.jpg'),
(5, 'Xanh', 'Lắc bàn tay ngang trước vai.', 'https://example.com/sign_blue.jpg'),
(5, 'Vàng', 'Đung đưa bàn tay bên hông.', 'https://example.com/sign_yellow.jpg'),
(5, 'Trắng', 'Chạm tay lên ngực rồi kéo ra.', 'https://example.com/sign_white.jpg');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media)
VALUES
(6, 'Ghế', 'Đưa hai tay mô tả hình ghế.', 'https://example.com/sign_chair.jpg'),
(6, 'Bàn', 'Đặt hai tay ngang mô tả mặt bàn.', 'https://example.com/sign_table.jpg'),
(6, 'Đèn', 'Búng tay ở phía trên đầu.', 'https://example.com/sign_lamp.jpg'),
(6, 'Giường', 'Đặt tay nghiêng mô tả ngủ.', 'https://example.com/sign_bed.jpg');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media)
VALUES
(7, 'Ăn', 'Đưa tay vào miệng.', 'https://example.com/sign_eat.jpg'),
(7, 'Uống', 'Đưa tay làm động tác cầm ly.', 'https://example.com/sign_drink.jpg'),
(7, 'Đi bộ', 'Hai tay mô tả chân bước.', 'https://example.com/sign_walk.jpg'),
(7, 'Ngồi', 'Hai tay mô tả động tác ngồi xuống.', 'https://example.com/sign_sit.jpg');

INSERT INTO users_usertest (user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
(1, 1, 'A', TRUE, NOW()),
(1, 2, 'B', TRUE, NOW()),
(1, 3, 'C', TRUE, NOW()),
(1, 4, 'D', TRUE, NOW()),
(1, 5, 'E', TRUE, NOW()),

(1, 6, '1', TRUE, NOW()),
(1, 7, '5', TRUE, NOW()),
(1, 8, '2', TRUE, NOW()),
(1, 9, '3', TRUE, NOW()),
(1,10, '0', TRUE, NOW());

INSERT INTO users_usertest (user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
(2, 1, 'B', FALSE, NOW()),
(2, 1, 'C', FALSE, NOW()),
(2, 1, 'D', FALSE, NOW()),   -- test 1 sai 3 lần!

(2, 2, 'A', FALSE, NOW()),
(2, 3, 'B', FALSE, NOW()),
(2, 3, 'D', FALSE, NOW()),   -- test 3 sai 2 lần

(2, 4, 'A', FALSE, NOW()),
(2, 5, 'B', FALSE, NOW()),
(2, 6, '2', FALSE, NOW());



INSERT INTO users_usertest (user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
(3, 1, 'A', TRUE, NOW()),
(3, 2, 'C', FALSE, NOW()),
(3, 3, 'C', TRUE, NOW());


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
-- INSERT INTO users_testquestion (id, topic_id, question, option_a, option_b, option_c, option_d, correct_option)
-- VALUES
-- (1, 1, 'Ký hiệu nào thể hiện chữ A?', 'Nắm tay lại', 'Giơ hai ngón tay', 'Đưa tay ra', 'Bẻ cong ngón cái', 'A'),
-- (2, 2, 'Ký hiệu nào thể hiện số 5?', 'Giơ ngón trỏ', 'Giơ cả bàn tay', 'Nắm tay lại', 'Giơ hai ngón', 'B'),
-- (3, 3, 'Ký hiệu "Cảm ơn" được thực hiện như thế nào?', 'Giơ tay lên cao', 'Đưa tay từ cằm ra ngoài', 'Vỗ tay', 'Chạm mũi', 'B');

INSERT INTO users_testquestion 
(flashcard_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(1, 'Đây là ký hiệu nào?', 'A', 'B', 'C', 'D', 'A'),
(2, 'Đây là ký hiệu nào?', 'B', 'A', 'C', 'E', 'A'),
(7, 'Đây là ký hiệu nào?', 'E', 'D', 'C', 'A', 'C'),
(8, 'Đây là ký hiệu nào?', 'D', 'A', 'C', 'E', 'A'),
(9, 'Đây là ký hiệu nào?', 'E', 'B', 'C', 'D', 'A');


INSERT INTO users_testquestion 
(flashcard_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(3,  'Đây là số nào?', '1', '0', '2', '5', 'A'),
(4,  'Đây là số nào?', '5', '3', '1', '0', 'A'),
(10, 'Đây là số nào?', '2', '1', '5', '3', 'A'),
(11, 'Đây là số nào?', '3', '1', '2', '0', 'A'),
(12, 'Đây là số nào?', '0', '1', '5', '3', 'A');


INSERT INTO users_testquestion 
(flashcard_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(5,  'Đây là ký hiệu nào?', 'Xin chào', 'Cảm ơn', 'Xin lỗi', 'Tạm biệt', 'A'),
(6,  'Đây là ký hiệu nào?', 'Cảm ơn', 'Xin chào', 'Xin lỗi', 'Vui vẻ', 'A'),
(13, 'Đây là ký hiệu nào?', 'Xin lỗi', 'Tạm biệt', 'Xin chào', 'Cảm ơn', 'A'),
(14, 'Đây là ký hiệu nào?', 'Tạm biệt', 'Xin lỗi', 'Vui vẻ', 'Xin chào', 'A'),
(15, 'Đây là ký hiệu nào?', 'Vui vẻ', 'Xin chào', 'Cảm ơn', 'Tạm biệt', 'A');

INSERT INTO users_testquestion 
(flashcard_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(16, 'Đây là ký hiệu nào?', 'Mèo', 'Chó', 'Cá', 'Chim', 'A'),
(17, 'Đây là ký hiệu nào?', 'Chó', 'Cá', 'Mèo', 'Chim', 'A'),
(18, 'Đây là ký hiệu nào?', 'Cá', 'Chó', 'Mèo', 'Chim', 'A'),
(19, 'Đây là ký hiệu nào?', 'Chim', 'Cá', 'Chó', 'Mèo', 'A');


INSERT INTO users_testquestion 
(flashcard_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(20, 'Đây là màu gì?', 'Đỏ', 'Xanh', 'Vàng', 'Trắng', 'A'),
(21, 'Đây là màu gì?', 'Xanh', 'Đỏ', 'Vàng', 'Trắng', 'A'),
(22, 'Đây là màu gì?', 'Vàng', 'Đỏ', 'Xanh', 'Trắng', 'A'),
(23, 'Đây là màu gì?', 'Trắng', 'Vàng', 'Xanh', 'Đỏ', 'A');


INSERT INTO users_testquestion 
(flashcard_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(24, 'Đây là đồ vật nào?', 'Ghế', 'Bàn', 'Đèn', 'Giường', 'A'),
(25, 'Đây là đồ vật nào?', 'Bàn', 'Ghế', 'Đèn', 'Giường', 'A'),
(26, 'Đây là đồ vật nào?', 'Đèn', 'Bàn', 'Ghế', 'Giường', 'A'),
(27, 'Đây là đồ vật nào?', 'Giường', 'Ghế', 'Bàn', 'Đèn', 'A');


INSERT INTO users_testquestion 
(flashcard_id, question, option_a, option_b, option_c, option_d, correct_option)
VALUES
(28, 'Đây là hành động nào?', 'Ăn', 'Uống', 'Đi bộ', 'Ngồi', 'A'),
(29, 'Đây là hành động nào?', 'Uống', 'Ăn', 'Đi bộ', 'Ngồi', 'A'),
(30, 'Đây là hành động nào?', 'Đi bộ', 'Ăn', 'Uống', 'Ngồi', 'A'),
(31, 'Đây là hành động nào?', 'Ngồi', 'Ăn', 'Đi bộ', 'Uống', 'A');



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
