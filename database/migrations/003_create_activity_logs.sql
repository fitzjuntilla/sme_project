USE mila_cafe;

CREATE TABLE activity_logs (
    log_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id INT(11) NOT NULL,
    action VARCHAR(100) NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id),

    KEY fk_activity_logs_user (user_id),

    CONSTRAINT fk_activity_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;