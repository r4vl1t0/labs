CREATE DATABASE shop;

USE shop;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price INT
);

INSERT INTO products(name, price) VALUES
('Laptop Dell Inspiron', 899),
('Mechanical Keyboard', 120),
('Gaming Mouse', 49),
('USB-C Dock', 89),
('27 inch Monitor', 320);

CREATE TABLE flags (
    id INT PRIMARY KEY,
    flag VARCHAR(100)
);

INSERT INTO flags VALUES
(1, 'FLAG{BOOLEAN_BASED_SHOP_SUCCESS}');
