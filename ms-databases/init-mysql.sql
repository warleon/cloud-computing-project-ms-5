-- Script de inicialización para MySQL (Microservicio 1)

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pedidos
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de prueba en users
INSERT INTO users (username, email) VALUES
('juan_perez', 'juan@example.com'),
('maria_gomez', 'maria@example.com'),
('pedro_rodriguez', 'pedro@example.com'),
('ana_martinez', 'ana@example.com'),
('carlos_lopez', 'carlos@example.com');

-- Insertar datos de prueba en products
INSERT INTO products (name, price, stock, category) VALUES
('Laptop Dell XPS 13', 1299.99, 15, 'Electronics'),
('Mouse Logitech MX', 79.99, 50, 'Accessories'),
('Teclado Mecánico', 149.99, 30, 'Accessories'),
('Monitor LG 27"', 399.99, 20, 'Electronics'),
('Webcam HD', 89.99, 40, 'Electronics'),
('Auriculares Sony', 199.99, 25, 'Accessories');

-- Insertar datos de prueba en orders
INSERT INTO orders (user_id, total_amount, status) VALUES
(1, 1299.99, 'completed'),
(2, 279.98, 'pending'),
(3, 549.98, 'completed'),
(1, 89.99, 'shipped'),
(4, 1699.98, 'completed'),
(5, 149.99, 'pending'),
(2, 399.99, 'shipped'),
(3, 79.99, 'completed');

SELECT 'MySQL inicializado con datos de prueba' AS mensaje;