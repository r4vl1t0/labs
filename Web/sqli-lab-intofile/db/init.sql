USE labdb;

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    description VARCHAR(255)
);

INSERT INTO products (name, description) VALUES
('Teclado mecanico', 'Switches azules, retroiluminado'),
('Mouse gamer', 'Sensor optico 16000 DPI'),
('Monitor 27"', 'Panel IPS, 144Hz'),
('Silla ergonomica', 'Soporte lumbar ajustable'),
('Webcam HD', '1080p con microfono integrado');

GRANT ALL PRIVILEGES ON *.* TO 'labuser'@'%';
GRANT FILE ON *.* TO 'labuser'@'%';
FLUSH PRIVILEGES;
