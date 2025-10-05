"""
Queries SQL predefinidas para el API
"""

PREDEFINED_QUERIES = {
    # ========== VENTAS (MySQL) ==========
    "ventas_resumen": """
        SELECT 
            COUNT(*) as total_ordenes,
            SUM(total_amount) as ventas_totales,
            AVG(total_amount) as ticket_promedio,
            MIN(total_amount) as orden_minima,
            MAX(total_amount) as orden_maxima
        FROM mysql_ms1_orders
    """,
    
    "ventas_por_usuario": """
        SELECT 
            u.username,
            u.email,
            COUNT(o.id) as total_ordenes,
            COALESCE(SUM(o.total_amount), 0) as total_gastado,
            COALESCE(AVG(o.total_amount), 0) as promedio_orden
        FROM mysql_ms1_users u
        LEFT JOIN mysql_ms1_orders o ON u.id = o.user_id
        GROUP BY u.username, u.email
        ORDER BY total_gastado DESC
    """,
    
    "ordenes_por_estado": """
        SELECT 
            status,
            COUNT(*) as cantidad_ordenes,
            SUM(total_amount) as monto_total,
            AVG(total_amount) as promedio_monto
        FROM mysql_ms1_orders
        GROUP BY status
        ORDER BY monto_total DESC
    """,
    
    "productos_top": """
        SELECT 
            name,
            category,
            price,
            stock,
            price * stock as valor_inventario
        FROM mysql_ms1_products
        WHERE stock > 0
        ORDER BY valor_inventario DESC
        LIMIT {limit}
    """,
    
    # ========== CLIENTES B2B (PostgreSQL) ==========
    "clientes_top": """
        SELECT 
            c.name as cliente,
            c.country,
            c.email,
            COUNT(i.id) as total_facturas,
            COALESCE(SUM(i.total), 0) as facturacion_total
        FROM postgres_ms2_customers c
        LEFT JOIN postgres_ms2_invoices i ON c.id = i.customer_id
        GROUP BY c.name, c.country, c.email
        ORDER BY facturacion_total DESC
        LIMIT {limit}
    """,
    
    "facturas_estado": """
        SELECT 
            i.invoice_number,
            c.name as cliente,
            i.total as monto_factura,
            COALESCE(SUM(p.amount), 0) as monto_pagado,
            i.total - COALESCE(SUM(p.amount), 0) as saldo_pendiente,
            i.status as estado_factura
        FROM postgres_ms2_invoices i
        JOIN postgres_ms2_customers c ON i.customer_id = c.id
        LEFT JOIN postgres_ms2_payments p ON i.id = p.invoice_id
        GROUP BY i.invoice_number, c.name, i.total, i.status
        ORDER BY saldo_pendiente DESC
    """,
    
    # ========== INVENTARIO (MongoDB) ==========
    "inventario_bajo_stock": """
        SELECT 
            product_id,
            name,
            quantity,
            warehouse_location,
            supplier
        FROM mongo_ms3_inventory
        WHERE CAST(quantity AS INTEGER) < {threshold}
        ORDER BY CAST(quantity AS INTEGER) ASC
    """,
    
    "envios_estado": """
        SELECT 
            status,
            carrier,
            COUNT(*) as total_envios
        FROM mongo_ms3_shipments
        GROUP BY status, carrier
        ORDER BY total_envios DESC
    """,
    
    # ========== DASHBOARD EJECUTIVO ==========
    "dashboard_ejecutivo": """
        SELECT 
            'Total Usuarios' as metrica,
            CAST(COUNT(*) AS VARCHAR) as valor,
            'users' as fuente
        FROM mysql_ms1_users
        
        UNION ALL
        
        SELECT 
            'Total Órdenes' as metrica,
            CAST(COUNT(*) AS VARCHAR) as valor,
            'orders' as fuente
        FROM mysql_ms1_orders
        
        UNION ALL
        
        SELECT 
            'Ingresos Totales' as metrica,
            CAST(ROUND(SUM(total_amount), 2) AS VARCHAR) as valor,
            'orders' as fuente
        FROM mysql_ms1_orders
        
        UNION ALL
        
        SELECT 
            'Total Clientes B2B' as metrica,
            CAST(COUNT(*) AS VARCHAR) as valor,
            'customers' as fuente
        FROM postgres_ms2_customers
        
        UNION ALL
        
        SELECT 
            'Productos en Inventario' as metrica,
            CAST(COUNT(*) AS VARCHAR) as valor,
            'inventory' as fuente
        FROM mongo_ms3_inventory
        
        UNION ALL
        
        SELECT 
            'Unidades en Stock' as metrica,
            CAST(SUM(CAST(quantity AS INTEGER)) AS VARCHAR) as valor,
            'inventory' as fuente
        FROM mongo_ms3_inventory
    """
}