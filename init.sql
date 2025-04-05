DROP DATABASE IF EXISTS log_monitoring;
CREATE DATABASE log_monitoring;
USE log_monitoring;

CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INT NOT NULL,
    response INT NOT NULL,
    response_time FLOAT NOT NULL,
    error VARCHAR(255),
    log_level VARCHAR(50) NOT NULL,
    metadata JSON DEFAULT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
