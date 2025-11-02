CREATE DATABASE IF NOT EXISTS expensetracker;
USE expensetracker;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(100) UNIQUE,
  password VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS expenses (
  expense_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  category VARCHAR(50),
  amount DECIMAL(10,2),
  exp_date DATE,
  description VARCHAR(255),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

INSERT INTO users (name, email, password) VALUES ('Vivek','vivek@example.com','1234') ON DUPLICATE KEY UPDATE email=email;
