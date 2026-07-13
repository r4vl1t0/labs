-- portal-clientes (SQLi)
CREATE DATABASE IF NOT EXISTS portal_clientes;
USE portal_clientes;

CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  nombre VARCHAR(100)
);
INSERT INTO usuarios (usuario, password, nombre) VALUES
  ('demo', SHA2('demo123',256), 'Cliente Demo S.A.');

CREATE TABLE facturas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT,
  numero VARCHAR(20),
  concepto VARCHAR(200),
  monto DECIMAL(10,2),
  fecha DATE
);
INSERT INTO facturas (usuario_id, numero, concepto, monto, fecha) VALUES
  (1, 'F-10021', 'Servicio de hosting mensual', 49.90, '2024-05-01'),
  (1, 'F-10022', 'Licencia de software de facturacion', 120.00, '2024-06-01'),
  (1, 'F-10023', 'Soporte tecnico premium', 75.50, '2024-06-15');

CREATE TABLE sistema_config (
  id INT AUTO_INCREMENT PRIMARY KEY,
  clave VARCHAR(50),
  valor VARCHAR(200)
);
INSERT INTO sistema_config (clave, valor) VALUES
  ('smtp_host', 'mail.portal-clientes.local'),
  ('version', '2.3.1'),
  ('flag', 'LAB{union_based_sqli_en_buscador_facturas}');

-- intranet (IDOR)
CREATE DATABASE IF NOT EXISTS intranet;
USE intranet;

CREATE TABLE empleados (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  nombre_completo VARCHAR(120),
  puesto VARCHAR(80),
  salario DECIMAL(10,2),
  nota_confidencial VARCHAR(200)
);
INSERT INTO empleados (usuario, password, nombre_completo, puesto, salario, nota_confidencial) VALUES
  ('rrhh.admin', SHA2('temporal_2024',256), 'Coordinacion de RRHH', 'Jefatura de Recursos Humanos', 4800.00, 'LAB{idor_legajo_sin_control_de_acceso}');

-- weakcreds (credenciales debiles) - no requiere base de datos, tabla simple igual para consistencia
CREATE DATABASE IF NOT EXISTS gestion_interna;
USE gestion_interna;
CREATE TABLE panel (
  id INT AUTO_INCREMENT PRIMARY KEY,
  flag VARCHAR(200)
);
INSERT INTO panel (flag) VALUES ('LAB{admin_admin_credenciales_por_defecto}');

-- soporte (mesa de ayuda, XSS almacenado)
CREATE DATABASE IF NOT EXISTS soporte;
USE soporte;

CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  nombre VARCHAR(100)
);

CREATE TABLE administradores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL
);
INSERT INTO administradores (usuario, password) VALUES
  ('soporte.admin', SHA2('R3visionM3sa2024!',256));

CREATE TABLE tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT,
  asunto VARCHAR(150),
  mensaje TEXT,
  estado VARCHAR(20) DEFAULT 'pendiente',
  revisado TINYINT DEFAULT 0,
  fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);
