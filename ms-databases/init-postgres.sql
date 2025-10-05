-- Script de inicialización para PostgreSQL (Microservicio 2)

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de facturas
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Tabla de pagos
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);

-- Insertar datos de prueba en customers
INSERT INTO customers (name, email, phone, country) VALUES
('Acme Corporation', 'contact@acme.com', '+1-555-0101', 'USA'),
('Global Tech Inc', 'info@globaltech.com', '+1-555-0102', 'USA'),
('Innovate Solutions', 'hello@innovate.com', '+44-20-1234', 'UK'),
('Digital Dynamics', 'sales@digitaldynamics.com', '+49-30-5678', 'Germany'),
('Tech Ventures Ltd', 'contact@techventures.com', '+81-3-9012', 'Japan');

-- Insertar datos de prueba en invoices
INSERT INTO invoices (customer_id, invoice_number, amount, tax, total, status) VALUES
(1, 'INV-2025-001', 5000.00, 500.00, 5500.00, 'paid'),
(2, 'INV-2025-002', 3200.00, 320.00, 3520.00, 'pending'),
(3, 'INV-2025-003', 7500.00, 750.00, 8250.00, 'paid'),
(1, 'INV-2025-004', 2100.00, 210.00, 2310.00, 'paid'),
(4, 'INV-2025-005', 4800.00, 480.00, 5280.00, 'overdue'),
(5, 'INV-2025-006', 6200.00, 620.00, 6820.00, 'pending');

-- Insertar datos de prueba en payments
INSERT INTO payments (invoice_id, payment_method, amount, status) VALUES
(1, 'credit_card', 5500.00, 'completed'),
(3, 'bank_transfer', 8250.00, 'completed'),
(4, 'paypal', 2310.00, 'completed'),
(2, 'credit_card', 1760.00, 'partial'),
(6, 'bank_transfer', 3410.00, 'partial');

SELECT 'PostgreSQL inicializado con datos de prueba' AS mensaje;