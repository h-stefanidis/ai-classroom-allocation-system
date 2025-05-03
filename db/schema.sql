DROP TABLE IF EXISTS allocations, courses, classrooms, users CASCADE;

-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classrooms table
CREATE TABLE classrooms (
    classroom_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    location TEXT
);

-- Courses table
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    teacher_id INTEGER REFERENCES users(user_id),
    expected_students INTEGER
);

-- Allocations table
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(course_id),
    classroom_id INTEGER REFERENCES classrooms(classroom_id),
    day VARCHAR(10),
    start_time TIME,
    end_time TIME
);