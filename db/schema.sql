DROP TABLE IF EXISTS courses, classrooms, allocations, allocation_students, users CASCADE;

-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for grouping allocations (from ML models or manual logic)
CREATE TABLE allocations (
    allocation_id SERIAL PRIMARY KEY,
    name VARCHAR(100),  -- e.g., "GNN-Based Allocation A", "Random Grouping 2"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table linking students to specific allocation groups
CREATE TABLE allocation_students (
    id SERIAL PRIMARY KEY,
    allocation_id INTEGER REFERENCES allocations(allocation_id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(user_id)
);