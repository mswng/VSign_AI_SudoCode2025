-- drop database signLanguage;
-- create database signLanguage;
-- use signLanguage;


-- ==========================================================
-- RESET DATABASE: SIGN LANGUAGE LEARNING PLATFORM
-- ==========================================================
-- Tắt kiểm tra foreign key (MySQL)
SET FOREIGN_KEY_CHECKS = 0;

-- Xóa dữ liệu bảng con trước
-- DELETE FROM users_aisessionlog;
-- DELETE FROM users_usertest;
-- DELETE FROM users_userflashcard;
-- DELETE FROM users_aisession;
-- DELETE FROM users_reminder;

-- -- Xóa dữ liệu bảng chính
-- DELETE FROM users_testquestion;
-- DELETE FROM users_flashcard;
-- DELETE FROM users_topic;

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

INSERT INTO `auth_user` VALUES 
    (1,'pbkdf2_sha256$1000000$tHdwLwehkOz0jTDgVAaVcI$KAFUkv0xtdIUm8sIZuH4xdCM2owwWx7Piq9tji0YoY4=','2025-11-06 15:04:46.261764',0,'ConLan','','','suongdtt1139@ut.edu.vn',0,1,'2025-11-06 15:04:33.589207'),
    (2,'pbkdf2_sha256$1000000$ds5AgywURUQCQqZbYxzlON$YK0c9sY93CDKVSj++0rQCmptyrIQcArfTnWUIetcxdk=','2025-11-13 12:44:26.254826',0,'Haha','','','thanhsuongdoan756@gmail.com',0,1,'2025-11-06 15:33:11.240330'),
    (3,'pbkdf2_sha256$1000000$kOYkEHKylhLsKwNyncAbPX$wAOIvZV8+M01KTFK+qujorsC+6by6d19+QlfZIAlNRU=',NULL,1,'Mswng','','','msuong1265@gmail.com',1,1,'2025-11-06 15:42:38.819773'),
    (4,'!GsvSQ3ClaZVFqlDqDx4g3go78LQ63Km8ulW7kIXZ','2025-11-08 16:16:04.717580',0,'suong','Sương','Thanh','',0,1,'2025-11-08 16:13:23.165269'),
    (5,'',NULL,0,'anonymous_user','','','',0,1,'2025-11-14 08:05:20.510158');
    
INSERT INTO users_customer (customer_id, email, sex, date_of_birth, joined_date, is_activated, user_id) VALUES 
    ('2NJj1','suongdtt1139@ut.edu.vn','Nữ','2005-12-06','2025-11-06 15:04:34.684653', 1, 1),
    ('aFH57','thanhsuongdoan756@gmail.com','male','2005-12-08','2025-11-06 15:33:12.174224', 1, 2),
    ('fPxOK',NULL,'Khác',NULL,'2025-11-08 16:13:23.637455', 1, 4),
    ('MEzHh',NULL,'Khác',NULL,'2025-11-14 08:05:20.515677', 1, 5),
    ('vo20H',NULL,'Khác',NULL,'2025-11-06 15:42:39.380784', 1, 3);


--  TOPICS

INSERT INTO users_topic (id, title, description, created_at)
VALUES
(1, 'Bảng chữ cái', 'Video hướng dẫn các ký hiệu chữ cái.', NOW()),
(2, 'Cảm xúc', 'Video mô tả các cảm xúc trong ngôn ngữ ký hiệu.', NOW()),
(3, 'Đồ ăn', 'Các hành động và danh từ về đồ ăn.', NOW()),
(4, 'Động vật', 'Tên các loài động vật trong ký hiệu.', NOW()),
(5, 'Gia đình', 'Các thành viên trong gia đình bằng ký hiệu.', NOW()),
(6, 'Sức khỏe', 'Từ vựng về sức khỏe và nghề y.', NOW());


INSERT INTO users_flashcard (topic_id, front_text, back_text, media) VALUES
(1, 'a', 'Video hướng dẫn ký hiệu "a".', 'https://youtu.be/NomiGmVc4MQ'),
(1, 'ă', 'Video hướng dẫn ký hiệu "ă".', 'https://youtu.be/usCxkLlN0ts'),
(1, 'â', 'Video hướng dẫn ký hiệu "â".', 'https://youtu.be/O3nSyPvLeJg'),
(1, 'b', 'Video hướng dẫn ký hiệu "b".', 'https://youtu.be/M5cAidaMJ9c'),
(1, 'c', 'Video hướng dẫn ký hiệu "c".', 'https://youtu.be/hAASqHb-0kk');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media) VALUES
(2, 'bực bội', 'Video hướng dẫn ký hiệu "bực bội".', 'https://youtu.be/n8dYykrGIBo'),
(2, 'cảm ơn', 'Video hướng dẫn ký hiệu "cảm ơn".', 'https://youtu.be/SGq3z87G8B8');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media) VALUES
(3, 'ăn', 'Video hướng dẫn ký hiệu "ăn".', 'https://youtu.be/_bPOGUZpgvs'),
(3, 'ăn sáng', 'Video hướng dẫn ký hiệu "ăn sáng".', 'https://youtu.be/cAhgjaaQLUA');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media) VALUES
(4, 'cá sấu', 'Video hướng dẫn ký hiệu "cá sấu".', 'https://youtu.be/peRzaZl2tK0'),
(4, 'con báo', 'Video hướng dẫn ký hiệu "con báo".', 'https://youtu.be/RcDcS-OmQzI'),
(4, 'con cọp', 'Video hướng dẫn ký hiệu "con cọp".', 'https://youtu.be/IsNioqe9G_w'),
(4, 'con dơi', 'Video hướng dẫn ký hiệu "con dơi".', 'https://youtu.be/N0ED5so2aAA'),
(4, 'con gấu', 'Video hướng dẫn ký hiệu "con gấu".', 'https://youtu.be/K6IUHA-TyA4'),
(4, 'con nai', 'Video hướng dẫn ký hiệu "con nai".', 'https://youtu.be/cv9daofHqPM');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media) VALUES
(5, 'anh trai', 'Video hướng dẫn ký hiệu "anh trai".', 'https://youtu.be/ZK0-GRNLPlc'),
(5, 'bà', 'Video hướng dẫn ký hiệu "bà".', 'https://youtu.be/pqH8Oy67v6c'),
(5, 'bố', 'Video hướng dẫn ký hiệu "bố".', 'https://youtu.be/xHfdXJE3f1k'),
(5, 'buồn', 'Video hướng dẫn ký hiệu "buồn".', 'https://youtu.be/SxdB5z3TJRE'),
(5, 'con', 'Video hướng dẫn ký hiệu "con".', 'https://youtu.be/59lwLUCJK4s');

INSERT INTO users_flashcard (topic_id, front_text, back_text, media) VALUES
(6, 'bệnh nhân', 'Video hướng dẫn ký hiệu "bệnh nhân".', 'https://youtu.be/r4bVRFR-GE0');
















-- ==============
-- 4. TEST_QUESTIONS
-- ==============
INSERT INTO users_testquestion
(question, option_a, option_b, option_c, option_d, correct_option, flashcard_id)
VALUES
('Đây là ký hiệu nào?', 'a', 'ă', 'â', 'b', 'A', 1),
('Đây là ký hiệu nào?', 'â', 'ă', 'a', 'c', 'B', 2),
('Đây là ký hiệu nào?', 'ă', 'c', 'â', 'b', 'C', 3),
('Đây là ký hiệu nào?', 'c', 'b', 'â', 'a', 'B', 4),
('Đây là ký hiệu nào?', 'b', 'ă', 'c', 'â', 'C', 5);


INSERT INTO users_testquestion
(question, option_a, option_b, option_c, option_d, correct_option, flashcard_id)
VALUES
('Đây là ký hiệu nào?', 'cảm ơn', 'bực bội', 'a', 'â', 'B', 6),
('Đây là ký hiệu nào?', 'bực bội', 'c', 'cảm ơn', 'ăn', 'C',7);

INSERT INTO users_testquestion
(question, option_a, option_b, option_c, option_d, correct_option, flashcard_id)
VALUES
('Đây là ký hiệu nào?', 'ăn sáng', 'b', 'c', 'ăn', 'D', 8),
('Đây là ký hiệu nào?', 'ăn', 'ăn sáng', 'c', 'd', 'B', 9);


INSERT INTO users_testquestion
(question, option_a, option_b, option_c, option_d, correct_option, flashcard_id)
VALUES
('Đây là ký hiệu nào?', 'con báo', 'cá sấu', 'con nai', 'con dơi', 'B', 10),
('Đây là ký hiệu nào?', 'cá sấu', 'con gấu', 'con báo', 'con cọp', 'C', 11),
('Đây là ký hiệu nào?', 'con dơi', 'con nai', 'con báo', 'con cọp', 'D', 12),
('Đây là ký hiệu nào?', 'con dơi', 'cá sấu', 'con báo', 'con gấu', 'A', 13),
('Đây là ký hiệu nào?', 'con nai', 'con báo', 'con gấu', 'cá sấu', 'C', 14),
('Đây là ký hiệu nào?', 'con gấu', 'con nai', 'con cọp', 'con dơi', 'B', 15);

INSERT INTO users_testquestion
(question, option_a, option_b, option_c, option_d, correct_option, flashcard_id)
VALUES
('Đây là ký hiệu nào?', 'bà', 'anh trai', 'buồn', 'con', 'B', 16),
('Đây là ký hiệu nào?', 'anh trai', 'con', 'bà', 'bố', 'C', 17),
('Đây là ký hiệu nào?', 'con', 'bà', 'bố', 'buồn', 'C', 18),
('Đây là ký hiệu nào?', 'bà', 'anh trai', 'con', 'buồn', 'D', 19),
('Đây là ký hiệu nào?', 'buồn', 'con', 'bố', 'anh trai', 'B', 20);


INSERT INTO users_testquestion
(question, option_a, option_b, option_c, option_d, correct_option, flashcard_id)
VALUES
('Đây là ký hiệu nào?', 'bệnh nhân', 'ăn', 'con gấu', 'bố', 'A', 21);






INSERT INTO users_usertest (user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
("2NJj1", 1, 'A', TRUE, NOW()),
("2NJj1", 2, 'B', TRUE, NOW()),
("2NJj1", 3, 'C', TRUE, NOW()),
("2NJj1", 4, 'B', TRUE, NOW()),
("2NJj1", 5, 'C', TRUE, NOW()),

("2NJj1", 6, 'B', TRUE, NOW()),
("2NJj1", 7, 'C', TRUE, NOW()),
("2NJj1", 8, '2', TRUE, NOW()),
("2NJj1", 9, '3', TRUE, NOW()),
("2NJj1",10, '0', TRUE, NOW());

INSERT INTO users_usertest (user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
("aFH57", 1, 'B', FALSE, NOW()),
("aFH57", 1, 'C', FALSE, NOW()),
("aFH57", 1, 'D', FALSE, NOW()),   -- test 1 sai 3 lần!

("aFH57", 2, 'A', FALSE, NOW()),
("aFH57", 3, 'B', FALSE, NOW()),
("aFH57", 3, 'D', FALSE, NOW()),   -- test 3 sai 2 lần

("aFH57", 4, 'A', FALSE, NOW()),
("aFH57", 5, 'B', FALSE, NOW()),
("aFH57", 6, 'C', FALSE, NOW());



INSERT INTO users_usertest (user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
("MEzHh", 1, 'A', TRUE, NOW()),
("MEzHh", 2, 'C', FALSE, NOW()),
("MEzHh", 3, 'C', TRUE, NOW());



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
-- 5. USER_TESTS
-- ==============
INSERT INTO users_usertest (user_id, test_id, user_answer, is_correct, attempted_at)
VALUES
('aFH57', 1, 'A', TRUE, NOW()),
('aFH57', 2, 'A', FALSE, NOW()),
('2NJj1', 3, 'C', TRUE, NOW());

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
