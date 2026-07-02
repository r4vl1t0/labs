CREATE DATABASE shop;

USE shop;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price INT
);

INSERT INTO products(name, price) VALUES
('Laptop Dell', 900),
('Keyboard', 120),
('Mouse', 50),
('Monitor', 300);

CREATE TABLE flags (
    id INT PRIMARY KEY,
    flag VARCHAR(100)
);

INSERT INTO flags VALUES
(1, 'FLAG{TIME_BASED_SQLI_SUCCESS}');
