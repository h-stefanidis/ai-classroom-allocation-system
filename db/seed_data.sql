INSERT INTO users (email, password_hash, role) VALUES
('admin@classforge.edu', 'hashed_admin_pw', 'admin'),
('alice.lee@classforge.edu', 'hashed_pw1', 'teacher'),
('bob.singh@classforge.edu', 'hashed_pw2', 'teacher');

INSERT INTO classrooms (name, capacity, location) VALUES
('Room A101', 40, 'Block A, Floor 1'),
('Room B201', 30, 'Block B, Floor 2'),
('Room C301', 50, 'Block C, Floor 3');


INSERT INTO courses (code, name, teacher_id, expected_students) VALUES
('COS80027', 'Machine Learning', 2, 35),
('COS60004', 'Operating Systems', 3, 28),
('COS90009', 'Deep Learning', 2, 40);


INSERT INTO allocations (course_id, classroom_id, day, start_time, end_time) VALUES
(1, 1, 'Monday', '09:00', '11:00'),
(2, 2, 'Tuesday', '14:00', '16:00'),
(3, 3, 'Wednesday', '10:00', '12:00');
