CREATE DATABASE corporativo;
CREATE DATABASE desarrollo;

USE corporativo;

CREATE TABLE usuarios (

identificador INT PRIMARY KEY AUTO_INCREMENT,

usuario VARCHAR(50),

contrasena VARCHAR(100),

rol VARCHAR(50)

);

INSERT INTO usuarios(usuario,contrasena,rol)
VALUES
('admin','Admin2026!','administrador'),
('jgarcia','verano123','empleado'),
('mlopez','qwerty2025','empleado'),
('soporte','HelpDesk01','soporte'),
('auditor','Audit2026','auditor');

CREATE TABLE tarjetas(

id INT PRIMARY KEY AUTO_INCREMENT,

usuario VARCHAR(50),

numero_tarjeta VARCHAR(16)

);

INSERT INTO tarjetas(usuario,numero_tarjeta)
VALUES
('admin','4532819458712634'),
('jgarcia','5274913826419047'),
('mlopez','4119827361548201'),
('soporte','5501938472615482'),
('auditor','6011458726391045');


USE desarrollo;

CREATE TABLE usuarios(

identificador INT PRIMARY KEY AUTO_INCREMENT,

usuario VARCHAR(50),

contrasena VARCHAR(100),

rol VARCHAR(30)

);

INSERT INTO usuarios(usuario,contrasena,rol)
VALUES
('devadmin','DevAdmin123','admin'),
('backend','Spring2026','developer'),
('frontend','Vue2026','developer');

CREATE TABLE flags(

id INT PRIMARY KEY,

flag VARCHAR(100)

);

INSERT INTO flags
VALUES
(
1,
'FLAG{8f14e45fceea167a5a36dedd4bea2543}'
);
