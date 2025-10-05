// Script de inicialización para MongoDB (Microservicio 3)

db = db.getSiblingDB('microservicio3');

// Colección: inventory (inventario)
db.inventory.insertMany([
    {
        product_id: "PROD-001",
        name: "Smartphone Samsung Galaxy",
        sku: "SAM-GAL-S23",
        quantity: 150,
        warehouse_location: "Warehouse A - Section 12",
        last_updated: new Date(),
        supplier: "Samsung Electronics"
    },
    {
        product_id: "PROD-002",
        name: "Laptop Apple MacBook Pro",
        sku: "APL-MBP-M3",
        quantity: 75,
        warehouse_location: "Warehouse B - Section 5",
        last_updated: new Date(),
        supplier: "Apple Inc"
    },
    {
        product_id: "PROD-003",
        name: "Smart Watch Garmin",
        sku: "GAR-SW-FX6",
        quantity: 200,
        warehouse_location: "Warehouse A - Section 8",
        last_updated: new Date(),
        supplier: "Garmin Ltd"
    },
    {
        product_id: "PROD-004",
        name: "Tablet Microsoft Surface",
        sku: "MS-SUR-PRO9",
        quantity: 100,
        warehouse_location: "Warehouse C - Section 3",
        last_updated: new Date(),
        supplier: "Microsoft Corporation"
    },
    {
        product_id: "PROD-005",
        name: "Headphones Sony WH-1000XM5",
        sku: "SNY-WH-1000",
        quantity: 300,
        warehouse_location: "Warehouse A - Section 15",
        last_updated: new Date(),
        supplier: "Sony Corporation"
    }
]);

// Colección: shipments (envíos)
db.shipments.insertMany([
    {
        shipment_id: "SHIP-2025-001",
        order_id: "ORD-2025-1234",
        carrier: "FedEx",
        tracking_number: "FDX123456789",
        origin: "New York, NY",
        destination: "Los Angeles, CA",
        status: "in_transit",
        shipped_date: new Date("2025-10-01"),
        estimated_delivery: new Date("2025-10-05"),
        items: [
            { product_id: "PROD-001", quantity: 2 },
            { product_id: "PROD-003", quantity: 1 }
        ]
    },
    {
        shipment_id: "SHIP-2025-002",
        order_id: "ORD-2025-1235",
        carrier: "UPS",
        tracking_number: "UPS987654321",
        origin: "Chicago, IL",
        destination: "Miami, FL",
        status: "delivered",
        shipped_date: new Date("2025-09-28"),
        estimated_delivery: new Date("2025-10-02"),
        actual_delivery: new Date("2025-10-02"),
        items: [
            { product_id: "PROD-002", quantity: 1 }
        ]
    },
    {
        shipment_id: "SHIP-2025-003",
        order_id: "ORD-2025-1236",
        carrier: "DHL",
        tracking_number: "DHL456789123",
        origin: "San Francisco, CA",
        destination: "Seattle, WA",
        status: "pending",
        items: [
            { product_id: "PROD-004", quantity: 3 },
            { product_id: "PROD-005", quantity: 2 }
        ]
    }
]);

// Colección: suppliers (proveedores)
db.suppliers.insertMany([
    {
        supplier_id: "SUP-001",
        name: "Samsung Electronics",
        contact_person: "John Kim",
        email: "john.kim@samsung.com",
        phone: "+82-2-2053-3000",
        address: {
            street: "129 Samsung-ro",
            city: "Seoul",
            country: "South Korea",
            postal_code: "06765"
        },
        products_supplied: ["PROD-001"],
        rating: 4.8,
        active: true
    },
    {
        supplier_id: "SUP-002",
        name: "Apple Inc",
        contact_person: "Sarah Johnson",
        email: "sarah.j@apple.com",
        phone: "+1-408-996-1010",
        address: {
            street: "One Apple Park Way",
            city: "Cupertino",
            state: "CA",
            country: "USA",
            postal_code: "95014"
        },
        products_supplied: ["PROD-002"],
        rating: 4.9,
        active: true
    },
    {
        supplier_id: "SUP-003",
        name: "Garmin Ltd",
        contact_person: "Michael Chen",
        email: "m.chen@garmin.com",
        phone: "+1-913-397-8200",
        address: {
            street: "1200 East 151st Street",
            city: "Olathe",
            state: "KS",
            country: "USA",
            postal_code: "66062"
        },
        products_supplied: ["PROD-003"],
        rating: 4.6,
        active: true
    },
    {
        supplier_id: "SUP-004",
        name: "Microsoft Corporation",
        contact_person: "Emily Davis",
        email: "emily.davis@microsoft.com",
        phone: "+1-425-882-8080",
        address: {
            street: "One Microsoft Way",
            city: "Redmond",
            state: "WA",
            country: "USA",
            postal_code: "98052"
        },
        products_supplied: ["PROD-004"],
        rating: 4.7,
        active: true
    },
    {
        supplier_id: "SUP-005",
        name: "Sony Corporation",
        contact_person: "Takeshi Yamamoto",
        email: "t.yamamoto@sony.com",
        phone: "+81-3-6748-2111",
        address: {
            street: "1-7-1 Konan",
            city: "Tokyo",
            country: "Japan",
            postal_code: "108-0075"
        },
        products_supplied: ["PROD-005"],
        rating: 4.5,
        active: true
    }
]);

print('MongoDB inicializado con datos de prueba');
print('Colecciones creadas: inventory, shipments, suppliers');