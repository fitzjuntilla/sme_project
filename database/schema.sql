CREATE DATABASE mila_cafe;

USE mila_cafe;


-- =========================================================
-- USERS
-- =========================================================

CREATE TABLE users (
    user_id INT(11) NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('Owner','Attendant') NOT NULL,
    status ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    UNIQUE KEY username (username)
);


-- =========================================================
-- CUSTOMERS
-- =========================================================

CREATE TABLE customers (
    customer_id INT(11) NOT NULL AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    contact_number VARCHAR(20) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (customer_id)
);


-- =========================================================
-- COMPUTERS
-- =========================================================

CREATE TABLE computers (
    computer_id INT(11) NOT NULL AUTO_INCREMENT,
    computer_number VARCHAR(20) NOT NULL,
    computer_name VARCHAR(100) DEFAULT NULL,

    status ENUM(
        'Available',
        'Occupied',
        'Maintenance'
    ) NOT NULL DEFAULT 'Available',

    hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 20.00,

    -- Operating cost of the computer per hour
    operating_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (computer_id),
    UNIQUE KEY computer_number (computer_number)
);


-- =========================================================
-- COMPUTER SESSIONS
-- =========================================================

CREATE TABLE computer_sessions (
    session_id INT(11) NOT NULL AUTO_INCREMENT,

    computer_id INT(11) NOT NULL,
    customer_id INT(11) DEFAULT NULL,

    start_time DATETIME NOT NULL,

    allocated_minutes INT(11) DEFAULT 60,

    end_time DATETIME DEFAULT NULL,

    duration_minutes INT(11) DEFAULT 0,

    total_amount DECIMAL(10,2) DEFAULT 0.00,

    status ENUM(
        'Active',
        'Completed',
        'Cancelled'
    ) NOT NULL DEFAULT 'Active',

    PRIMARY KEY (session_id),

    KEY computer_id (computer_id),
    KEY customer_id (customer_id),

    CONSTRAINT computer_sessions_ibfk_1
        FOREIGN KEY (computer_id)
        REFERENCES computers (computer_id),

    CONSTRAINT computer_sessions_ibfk_2
        FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id)
);


-- =========================================================
-- SERVICES
-- =========================================================

CREATE TABLE services (
    service_id INT(11) NOT NULL AUTO_INCREMENT,

    service_name VARCHAR(100) NOT NULL,

    description VARCHAR(255) DEFAULT NULL,

    service_type ENUM(
        'Printing',
        'Scanning',
        'Photocopying',
        'Other'
    ) NOT NULL,

    price DECIMAL(10,2) NOT NULL,

    status ENUM(
        'Available',
        'Unavailable'
    ) NOT NULL DEFAULT 'Available',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (service_id)
);


-- =========================================================
-- INVENTORY
-- =========================================================

CREATE TABLE inventory (
    inventory_id INT(11) NOT NULL AUTO_INCREMENT,

    item_name VARCHAR(100) NOT NULL,

    description VARCHAR(255) DEFAULT NULL,

    quantity DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    -- Original/purchase cost per unit from supplier
    unit_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    unit VARCHAR(30) NOT NULL,

    minimum_stock DECIMAL(10,2) NOT NULL DEFAULT 5.00,

    status ENUM(
        'Available',
        'Low Stock',
        'Out of Stock'
    ) NOT NULL DEFAULT 'Available',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (inventory_id)
);


-- =========================================================
-- INVENTORY TRANSACTIONS
-- =========================================================

CREATE TABLE inventory_transactions (
    inventory_transaction_id INT(11) NOT NULL AUTO_INCREMENT,

    inventory_id INT(11) NOT NULL,

    user_id INT(11) NOT NULL,

    transaction_type ENUM(
        'Stock In',
        'Stock Out'
    ) NOT NULL,

    quantity DECIMAL(10,2) NOT NULL,

    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    remarks VARCHAR(255) DEFAULT NULL,

    PRIMARY KEY (inventory_transaction_id),

    KEY inventory_id (inventory_id),
    KEY user_id (user_id),

    CONSTRAINT inventory_transactions_ibfk_1
        FOREIGN KEY (inventory_id)
        REFERENCES inventory (inventory_id),

    CONSTRAINT inventory_transactions_ibfk_2
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
);


-- =========================================================
-- SERVICE MATERIALS
-- =========================================================
--
-- Defines which inventory materials are consumed by
-- each service and how much material is required.
--
-- Example:
-- Black & White Printing
--   1 sheet of bond paper
--   0.001 bottle of black ink
--
-- =========================================================

CREATE TABLE service_materials (
    service_material_id INT(11) NOT NULL AUTO_INCREMENT,

    service_id INT(11) NOT NULL,

    inventory_id INT(11) NOT NULL,

    quantity_required DECIMAL(10,4) NOT NULL DEFAULT 0.0000,

    PRIMARY KEY (service_material_id),

    KEY service_id (service_id),
    KEY inventory_id (inventory_id),

    CONSTRAINT service_materials_ibfk_1
        FOREIGN KEY (service_id)
        REFERENCES services (service_id),

    CONSTRAINT service_materials_ibfk_2
        FOREIGN KEY (inventory_id)
        REFERENCES inventory (inventory_id)
);


-- =========================================================
-- TRANSACTIONS
-- =========================================================

CREATE TABLE transactions (
    transaction_id INT(11) NOT NULL AUTO_INCREMENT,

    customer_id INT(11) DEFAULT NULL,

    user_id INT(11) NOT NULL,

    session_id INT(11) DEFAULT NULL,

    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    cash_received DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    change_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    payment_status ENUM(
        'Paid',
        'Pending',
        'Cancelled'
    ) NOT NULL DEFAULT 'Paid',

    PRIMARY KEY (transaction_id),

    KEY customer_id (customer_id),
    KEY user_id (user_id),
    KEY session_id (session_id),

    CONSTRAINT transactions_ibfk_1
        FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id),

    CONSTRAINT transactions_ibfk_2
        FOREIGN KEY (user_id)
        REFERENCES users (user_id),

    CONSTRAINT transactions_ibfk_3
        FOREIGN KEY (session_id)
        REFERENCES computer_sessions (session_id)
);


-- =========================================================
-- TRANSACTION ITEMS
-- =========================================================

CREATE TABLE transaction_items (
    transaction_item_id INT(11) NOT NULL AUTO_INCREMENT,

    transaction_id INT(11) NOT NULL,

    service_id INT(11) NOT NULL,

    quantity INT(11) NOT NULL DEFAULT 1,

    unit_price DECIMAL(10,2) NOT NULL,

    subtotal DECIMAL(10,2) NOT NULL,

    -- Material cost used for this transaction item
    material_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    PRIMARY KEY (transaction_item_id),

    KEY transaction_id (transaction_id),
    KEY service_id (service_id),

    CONSTRAINT transaction_items_ibfk_1
        FOREIGN KEY (transaction_id)
        REFERENCES transactions (transaction_id),

    CONSTRAINT transaction_items_ibfk_2
        FOREIGN KEY (service_id)
        REFERENCES services (service_id)
);


-- =========================================================
-- ACTIVITY LOGS
-- =========================================================

CREATE TABLE activity_logs (
    log_id INT(11) NOT NULL AUTO_INCREMENT,

    user_id INT(11) NOT NULL,

    action VARCHAR(100) NOT NULL,

    description VARCHAR(255) DEFAULT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id),

    KEY user_id (user_id),

    CONSTRAINT fk_activity_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
);


-- =========================================================
-- END OF DATABASE SCHEMA
-- =========================================================