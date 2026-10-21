USE mila_cafe;

ALTER TABLE users
ADD COLUMN status ENUM('Active', 'Inactive')
NOT NULL DEFAULT 'Active'
AFTER role;