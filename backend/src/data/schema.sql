
CREATE DATABASE IF NOT EXISTS analytics_db;
USE analytics_db;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_status (status),
    INDEX idx_users_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS activity_events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    event_type VARCHAR(60) NOT NULL,
    page VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    CONSTRAINT fk_activity_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    INDEX idx_events_created_at (created_at),
    INDEX idx_events_user_created (user_id, created_at),
    INDEX idx_events_type_created (event_type, created_at)
);
