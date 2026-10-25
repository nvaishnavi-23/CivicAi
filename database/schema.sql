-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'citizen',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Complaints table
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    title TEXT,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT DEFAULT 'Medium',
    priority_reason TEXT,
    department TEXT,
    latitude REAL,
    longitude REAL,
    address TEXT,
    image_path TEXT,
    status TEXT DEFAULT 'Submitted',
    admin_remarks TEXT,
    resolution_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       resolved_at TIMESTAMP,

    duplicate_of TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_complaint_user_id ON complaints(user_id);
CREATE INDEX IF NOT EXISTS idx_complaint_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaint_category ON complaints(category);
CREATE INDEX IF NOT EXISTS idx_complaint_department ON complaints(department);
CREATE INDEX IF NOT EXISTS idx_complaint_created_at ON complaints(created_at);
