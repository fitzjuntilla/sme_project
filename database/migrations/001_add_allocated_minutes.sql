USE mila_cafe;

ALTER TABLE computer_sessions
ADD COLUMN allocated_minutes INT DEFAULT 60
AFTER start_time;