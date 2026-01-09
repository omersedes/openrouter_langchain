import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv
import os

load_dotenv()

# Configurable constants for data thresholds
MIN_CUSTOMERS = 50
MIN_PRODUCTS = 30
MIN_ORDERS = 100
MIN_ORDER_ITEMS = 150

def connect_to_postgres():
    """Connect to PostgreSQL server (not specific database)"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_ADMIN_USER"),
            password=os.getenv("DB_ADMIN_PASSWORD"),
            database="postgres"
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

def create_database():
    """Create the ecommerce database if it doesn't exist"""
    conn = None
    try:
        conn = connect_to_postgres()
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'ecommerce'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("ecommerce")))
            print("✓ Database 'ecommerce' created successfully")
        else:
            print("✓ Database 'ecommerce' already exists")
        
        cursor.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def connect_to_ecommerce_db():
    """Connect to the ecommerce database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_ADMIN_USER"),
            password=os.getenv("DB_ADMIN_PASSWORD"),
            database="ecommerce"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to ecommerce database: {e}")
        raise

def create_tables(conn):
    """Create the ecommerce schema tables"""
    try:
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                category VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending'
            )
        """)
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(order_id),
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL
            )
        """)
        
        conn.commit()
        print("✓ Tables created successfully")
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {e}")
        raise

def get_row_count(conn, table_name):
    """Get the number of rows in a table"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Exception as e:
        print(f"Error getting row count for {table_name}: {e}")
        return 0

def populate_data(conn):
    """Populate tables with sample data if needed"""
    try:
        cursor = conn.cursor()
        
        # Check existing data
        customers_count = get_row_count(conn, "customers")
        products_count = get_row_count(conn, "products")
        orders_count = get_row_count(conn, "orders")
        order_items_count = get_row_count(conn, "order_items")
        
        print(f"\nCurrent row counts:")
        print(f"  - Customers: {customers_count}")
        print(f"  - Products: {products_count}")
        print(f"  - Orders: {orders_count}")
        print(f"  - Order Items: {order_items_count}")
        
        # Insert customers if needed
        if customers_count < MIN_CUSTOMERS:
            print(f"\nInserting customers (target: {MIN_CUSTOMERS})...")
            customers_data = [
                ('John', 'Doe', 'john.doe@email.com'),
                ('Jane', 'Smith', 'jane.smith@email.com'),
                ('Bob', 'Johnson', 'bob.johnson@email.com'),
                ('Alice', 'Williams', 'alice.williams@email.com'),
                ('Charlie', 'Brown', 'charlie.brown@email.com'),
                ('Emma', 'Davis', 'emma.davis@email.com'),
                ('Michael', 'Wilson', 'michael.wilson@email.com'),
                ('Sarah', 'Moore', 'sarah.moore@email.com'),
                ('David', 'Taylor', 'david.taylor@email.com'),
                ('Lisa', 'Anderson', 'lisa.anderson@email.com'),
                ('James', 'Thomas', 'james.thomas@email.com'),
                ('Emily', 'Jackson', 'emily.jackson@email.com'),
                ('Robert', 'White', 'robert.white@email.com'),
                ('Jennifer', 'Harris', 'jennifer.harris@email.com'),
                ('William', 'Martin', 'william.martin@email.com'),
                ('Linda', 'Thompson', 'linda.thompson@email.com'),
                ('Richard', 'Garcia', 'richard.garcia@email.com'),
                ('Patricia', 'Martinez', 'patricia.martinez@email.com'),
                ('Thomas', 'Robinson', 'thomas.robinson@email.com'),
                ('Mary', 'Clark', 'mary.clark@email.com'),
                ('Christopher', 'Rodriguez', 'christopher.rodriguez@email.com'),
                ('Nancy', 'Lewis', 'nancy.lewis@email.com'),
                ('Daniel', 'Lee', 'daniel.lee@email.com'),
                ('Karen', 'Walker', 'karen.walker@email.com'),
                ('Matthew', 'Hall', 'matthew.hall@email.com'),
                ('Betty', 'Allen', 'betty.allen@email.com'),
                ('Anthony', 'Young', 'anthony.young@email.com'),
                ('Sandra', 'Hernandez', 'sandra.hernandez@email.com'),
                ('Mark', 'King', 'mark.king@email.com'),
                ('Ashley', 'Wright', 'ashley.wright@email.com'),
                ('Donald', 'Lopez', 'donald.lopez@email.com'),
                ('Kimberly', 'Hill', 'kimberly.hill@email.com'),
                ('Steven', 'Scott', 'steven.scott@email.com'),
                ('Donna', 'Green', 'donna.green@email.com'),
                ('Paul', 'Adams', 'paul.adams@email.com'),
                ('Carol', 'Baker', 'carol.baker@email.com'),
                ('Andrew', 'Gonzalez', 'andrew.gonzalez@email.com'),
                ('Michelle', 'Nelson', 'michelle.nelson@email.com'),
                ('Joshua', 'Carter', 'joshua.carter@email.com'),
                ('Amanda', 'Mitchell', 'amanda.mitchell@email.com'),
                ('Kevin', 'Perez', 'kevin.perez@email.com'),
                ('Melissa', 'Roberts', 'melissa.roberts@email.com'),
                ('Brian', 'Turner', 'brian.turner@email.com'),
                ('Deborah', 'Phillips', 'deborah.phillips@email.com'),
                ('George', 'Campbell', 'george.campbell@email.com'),
                ('Stephanie', 'Parker', 'stephanie.parker@email.com'),
                ('Edward', 'Evans', 'edward.evans@email.com'),
                ('Rebecca', 'Edwards', 'rebecca.edwards@email.com'),
                ('Ronald', 'Collins', 'ronald.collins@email.com'),
                ('Laura', 'Stewart', 'laura.stewart@email.com')
            ]
            
            cursor.executemany(
                "INSERT INTO customers (first_name, last_name, email) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING",
                customers_data
            )
            print(f"✓ Customers inserted")
        else:
            print(f"\n✓ Customers table has sufficient data ({customers_count} >= {MIN_CUSTOMERS})")
        
        # Insert products if needed
        if products_count < MIN_PRODUCTS:
            print(f"\nInserting products (target: {MIN_PRODUCTS})...")
            products_data = [
                ('Laptop Pro 15"', 'High-performance laptop with 16GB RAM', 1299.99, 50, 'Electronics'),
                ('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 29.99, 200, 'Electronics'),
                ('Mechanical Keyboard', 'RGB mechanical keyboard with blue switches', 89.99, 100, 'Electronics'),
                ('USB-C Hub', '7-in-1 USB-C hub with HDMI and ethernet', 49.99, 150, 'Electronics'),
                ('Noise-Canceling Headphones', 'Premium over-ear headphones', 299.99, 75, 'Electronics'),
                ('4K Monitor 27"', 'Ultra HD monitor with HDR support', 449.99, 60, 'Electronics'),
                ('Webcam HD', '1080p webcam with built-in microphone', 79.99, 120, 'Electronics'),
                ('Desk Lamp LED', 'Adjustable LED desk lamp with USB charging', 39.99, 180, 'Home & Office'),
                ('Office Chair', 'Ergonomic office chair with lumbar support', 249.99, 40, 'Furniture'),
                ('Standing Desk', 'Electric height-adjustable standing desk', 599.99, 25, 'Furniture'),
                ('Backpack Laptop', 'Water-resistant laptop backpack with USB port', 59.99, 100, 'Accessories'),
                ('Phone Stand', 'Adjustable aluminum phone stand', 19.99, 250, 'Accessories'),
                ('Cable Organizer', 'Cable management box with 5 slots', 24.99, 200, 'Accessories'),
                ('Power Bank 20000mAh', 'Fast-charging portable power bank', 39.99, 150, 'Electronics'),
                ('Bluetooth Speaker', 'Portable waterproof Bluetooth speaker', 69.99, 130, 'Electronics'),
                ('Smart Watch', 'Fitness tracker with heart rate monitor', 199.99, 80, 'Electronics'),
                ('Tablet 10"', 'Android tablet with 64GB storage', 279.99, 70, 'Electronics'),
                ('External SSD 1TB', 'Portable solid-state drive USB 3.2', 119.99, 100, 'Electronics'),
                ('Gaming Mouse Pad', 'Large RGB gaming mouse pad', 34.99, 160, 'Accessories'),
                ('Laptop Stand', 'Aluminum laptop stand with cooling', 44.99, 140, 'Accessories'),
                ('Wireless Charger', 'Fast wireless charging pad', 29.99, 170, 'Electronics'),
                ('HDMI Cable 6ft', '4K HDMI 2.1 cable', 14.99, 300, 'Electronics'),
                ('Screen Protector', 'Tempered glass screen protector', 12.99, 400, 'Accessories'),
                ('Phone Case', 'Shockproof phone case with kickstand', 24.99, 350, 'Accessories'),
                ('Portable Monitor', '15.6" USB-C portable monitor', 229.99, 55, 'Electronics'),
                ('Microphone USB', 'Condenser USB microphone for streaming', 89.99, 90, 'Electronics'),
                ('Laptop Sleeve', 'Neoprene laptop sleeve 13-15"', 19.99, 220, 'Accessories'),
                ('Desk Organizer', 'Wooden desk organizer with drawers', 34.99, 110, 'Home & Office'),
                ('Whiteboard', 'Magnetic dry-erase whiteboard 24x36"', 49.99, 65, 'Home & Office'),
                ('Notebook Set', 'Pack of 5 hardcover notebooks', 29.99, 180, 'Home & Office')
            ]
            
            cursor.executemany(
                "INSERT INTO products (name, description, price, stock_quantity, category) VALUES (%s, %s, %s, %s, %s)",
                products_data
            )
            print(f"✓ Products inserted")
        else:
            print(f"\n✓ Products table has sufficient data ({products_count} >= {MIN_PRODUCTS})")
        
        # Insert orders if needed
        if orders_count < MIN_ORDERS:
            print(f"\nInserting orders (target: {MIN_ORDERS})...")
            orders_data = [
                (1, 1329.98, 'completed'),
                (2, 89.99, 'completed'),
                (3, 549.98, 'completed'),
                (4, 299.99, 'shipped'),
                (5, 1749.98, 'completed'),
                (1, 179.97, 'completed'),
                (6, 449.99, 'completed'),
                (7, 289.98, 'shipped'),
                (8, 599.99, 'pending'),
                (9, 119.98, 'completed'),
                (10, 649.97, 'completed'),
                (2, 349.98, 'completed'),
                (11, 89.99, 'cancelled'),
                (12, 229.99, 'completed'),
                (13, 1099.98, 'shipped'),
                (14, 79.99, 'completed'),
                (15, 524.97, 'completed'),
                (3, 159.97, 'completed'),
                (16, 699.98, 'pending'),
                (17, 249.99, 'completed'),
                (18, 419.97, 'completed'),
                (19, 189.98, 'shipped'),
                (20, 899.97, 'completed'),
                (4, 279.99, 'completed'),
                (21, 149.98, 'completed'),
                (22, 329.98, 'cancelled'),
                (23, 199.99, 'completed'),
                (24, 479.97, 'shipped'),
                (25, 119.99, 'completed'),
                (5, 849.98, 'completed'),
                (26, 89.99, 'completed'),
                (27, 359.97, 'pending'),
                (28, 229.98, 'completed'),
                (29, 599.99, 'completed'),
                (30, 169.97, 'completed'),
                (6, 1299.99, 'shipped'),
                (31, 449.98, 'completed'),
                (32, 89.99, 'completed'),
                (33, 729.97, 'completed'),
                (34, 299.99, 'pending'),
                (7, 189.98, 'completed'),
                (35, 549.98, 'completed'),
                (36, 399.97, 'cancelled'),
                (37, 279.99, 'completed'),
                (38, 149.98, 'shipped'),
                (8, 599.99, 'completed'),
                (39, 219.98, 'completed'),
                (40, 899.97, 'completed'),
                (9, 329.98, 'pending'),
                (41, 179.97, 'completed'),
                (10, 449.99, 'completed'),
                (42, 89.99, 'completed'),
                (43, 649.97, 'shipped'),
                (44, 229.99, 'completed'),
                (11, 799.98, 'completed'),
                (45, 119.99, 'cancelled'),
                (46, 479.97, 'completed'),
                (12, 349.98, 'completed'),
                (47, 199.99, 'pending'),
                (48, 589.97, 'completed'),
                (13, 279.99, 'completed'),
                (49, 149.98, 'shipped'),
                (50, 999.97, 'completed'),
                (14, 89.99, 'completed'),
                (15, 529.98, 'completed'),
                (1, 379.97, 'pending'),
                (16, 229.99, 'completed'),
                (17, 699.98, 'cancelled'),
                (2, 149.98, 'completed'),
                (18, 449.99, 'completed'),
                (19, 319.97, 'shipped'),
                (3, 189.98, 'completed'),
                (20, 849.97, 'completed'),
                (21, 279.99, 'pending'),
                (4, 599.99, 'completed'),
                (22, 129.98, 'completed'),
                (23, 479.97, 'completed'),
                (5, 349.98, 'shipped'),
                (24, 199.99, 'completed'),
                (25, 729.97, 'cancelled'),
                (6, 89.99, 'completed'),
                (26, 449.99, 'completed'),
                (27, 269.97, 'pending'),
                (7, 599.99, 'completed'),
                (28, 179.98, 'shipped'),
                (8, 899.97, 'completed'),
                (29, 329.98, 'completed'),
                (30, 149.98, 'completed'),
                (9, 549.98, 'pending'),
                (31, 229.99, 'completed'),
                (32, 699.97, 'cancelled'),
                (10, 119.99, 'completed'),
                (33, 479.97, 'shipped'),
                (34, 299.99, 'completed'),
                (11, 849.98, 'completed'),
                (35, 189.98, 'pending'),
                (12, 649.97, 'completed'),
                (36, 329.98, 'completed'),
                (13, 99.99, 'completed'),
                (37, 529.97, 'shipped')
            ]
            
            cursor.executemany(
                "INSERT INTO orders (customer_id, total_amount, status) VALUES (%s, %s, %s)",
                orders_data
            )
            print(f"✓ Orders inserted")
        else:
            print(f"\n✓ Orders table has sufficient data ({orders_count} >= {MIN_ORDERS})")
        
        # Insert order items if needed
        if order_items_count < MIN_ORDER_ITEMS:
            print(f"\nInserting order items (target: {MIN_ORDER_ITEMS})...")
            order_items_data = [
                (1, 1, 1, 1299.99), (1, 2, 1, 29.99),
                (2, 3, 1, 89.99),
                (3, 1, 1, 1299.99), (3, 4, 5, 49.99),
                (4, 5, 1, 299.99),
                (5, 1, 1, 1299.99), (5, 6, 1, 449.99),
                (6, 7, 1, 79.99), (6, 2, 2, 29.99), (6, 8, 1, 39.99),
                (7, 6, 1, 449.99),
                (8, 9, 1, 249.99), (8, 8, 1, 39.99), (8, 10, 1, 599.99),
                (9, 10, 1, 599.99),
                (10, 11, 2, 59.99),
                (11, 12, 1, 19.99), (11, 13, 1, 24.99), (11, 14, 1, 39.99),
                (11, 15, 9, 69.99),
                (12, 16, 1, 199.99), (12, 17, 1, 279.99), (12, 2, 2, 29.99),
                (13, 3, 1, 89.99),
                (14, 18, 1, 119.99), (14, 19, 3, 34.99), (14, 20, 1, 44.99),
                (15, 1, 1, 1299.99), (15, 21, 4, 29.99), (15, 22, 5, 14.99),
                (16, 7, 1, 79.99),
                (17, 23, 10, 12.99), (17, 24, 10, 24.99), (17, 27, 5, 19.99),
                (18, 2, 2, 29.99), (18, 4, 2, 49.99), (18, 13, 1, 24.99),
                (19, 25, 3, 229.99), (19, 22, 2, 14.99),
                (20, 9, 1, 249.99),
                (21, 26, 1, 89.99), (21, 21, 3, 29.99), (21, 28, 3, 34.99),
                (21, 12, 4, 19.99),
                (22, 15, 2, 69.99), (22, 19, 1, 34.99), (22, 20, 1, 44.99),
                (23, 29, 4, 49.99),
                (24, 30, 1, 29.99), (24, 11, 1, 59.99), (24, 27, 3, 19.99),
                (24, 28, 3, 34.99),
                (25, 16, 1, 199.99),
                (26, 17, 1, 279.99),
                (27, 14, 2, 39.99), (27, 18, 2, 119.99), (27, 21, 3, 29.99),
                (28, 5, 1, 299.99),
                (29, 1, 1, 1299.99), (29, 23, 10, 12.99), (29, 24, 10, 24.99),
                (30, 3, 1, 89.99),
                (31, 6, 1, 449.99), (31, 7, 1, 79.99), (31, 2, 1, 29.99),
                (32, 10, 1, 599.99),
                (33, 2, 1, 29.99),
                (34, 25, 3, 229.99), (34, 22, 3, 14.99),
                (35, 5, 1, 299.99),
                (36, 8, 1, 39.99), (36, 12, 1, 19.99), (36, 13, 1, 24.99),
                (36, 19, 2, 34.99),
                (37, 1, 1, 1299.99),
                (38, 3, 1, 89.99),
                (39, 26, 1, 89.99), (39, 27, 2, 19.99), (39, 28, 3, 34.99),
                (40, 9, 1, 249.99), (40, 10, 1, 599.99), (40, 8, 1, 39.99),
                (41, 17, 1, 279.99),
                (42, 15, 5, 69.99),
                (43, 16, 1, 199.99), (43, 18, 1, 119.99), (43, 21, 3, 29.99),
                (43, 4, 2, 49.99),
                (44, 6, 1, 449.99),
                (45, 14, 3, 39.99),
                (46, 11, 1, 59.99), (46, 23, 10, 12.99), (46, 24, 10, 24.99),
                (46, 27, 5, 19.99),
                (47, 2, 2, 29.99), (47, 4, 2, 49.99), (47, 13, 1, 24.99),
                (48, 5, 1, 299.99),
                (49, 25, 2, 229.99), (49, 22, 4, 14.99),
                (50, 1, 1, 1299.99), (50, 19, 3, 34.99), (50, 20, 1, 44.99),
                (51, 7, 1, 79.99),
                (52, 30, 1, 29.99), (52, 29, 1, 49.99), (52, 28, 5, 34.99),
                (53, 9, 1, 249.99), (53, 8, 1, 39.99), (53, 12, 2, 19.99),
                (54, 17, 1, 279.99),
                (55, 26, 1, 89.99), (55, 27, 4, 19.99), (55, 21, 4, 29.99),
                (56, 3, 1, 89.99),
                (57, 6, 1, 449.99), (57, 7, 1, 79.99),
                (58, 16, 1, 199.99), (58, 18, 1, 119.99),
                (59, 10, 1, 599.99),
                (60, 15, 8, 69.99), (60, 22, 3, 14.99),
                (61, 14, 2, 39.99), (61, 23, 10, 12.99), (61, 24, 10, 24.99),
                (62, 5, 1, 299.99),
                (63, 1, 1, 1299.99), (63, 2, 1, 29.99), (63, 4, 3, 49.99),
                (64, 11, 1, 59.99), (64, 27, 3, 19.99), (64, 28, 3, 34.99),
                (65, 25, 2, 229.99),
                (66, 9, 1, 249.99), (66, 8, 1, 39.99), (66, 13, 1, 24.99),
                (67, 3, 1, 89.99),
                (68, 6, 1, 449.99),
                (69, 26, 1, 89.99), (69, 21, 3, 29.99), (69, 19, 2, 34.99),
                (70, 17, 1, 279.99), (70, 18, 1, 119.99), (70, 4, 4, 49.99),
                (71, 10, 1, 599.99),
                (72, 30, 1, 29.99), (72, 29, 1, 49.99), (72, 28, 1, 34.99),
                (73, 15, 10, 69.99),
                (74, 16, 1, 199.99),
                (75, 25, 3, 229.99),
                (76, 2, 1, 29.99), (76, 12, 2, 19.99), (76, 13, 1, 24.99),
                (77, 7, 1, 79.99), (77, 8, 1, 39.99),
                (78, 5, 3, 299.99),
                (79, 26, 1, 89.99), (79, 27, 2, 19.99),
                (80, 1, 1, 1299.99), (80, 23, 10, 12.99), (80, 24, 10, 24.99),
                (81, 14, 2, 39.99), (81, 21, 2, 29.99),
                (82, 3, 1, 89.99), (82, 4, 1, 49.99),
                (83, 9, 1, 249.99), (83, 10, 1, 599.99),
                (84, 6, 1, 449.99),
                (85, 17, 1, 279.99), (85, 18, 1, 119.99), (85, 19, 3, 34.99),
                (86, 11, 2, 59.99),
                (87, 25, 2, 229.99), (87, 22, 4, 14.99),
                (88, 16, 1, 199.99), (88, 15, 3, 69.99),
                (89, 5, 1, 299.99), (89, 2, 1, 29.99),
                (90, 30, 1, 29.99), (90, 29, 2, 49.99), (90, 28, 2, 34.99),
                (91, 7, 1, 79.99), (91, 8, 1, 39.99), (91, 12, 2, 19.99),
                (92, 1, 1, 1299.99), (92, 26, 1, 89.99),
                (93, 14, 3, 39.99), (93, 21, 2, 29.99), (93, 13, 1, 24.99),
                (94, 9, 1, 249.99), (94, 8, 1, 39.99),
                (95, 3, 1, 89.99),
                (96, 25, 3, 229.99), (96, 22, 2, 14.99),
                (97, 6, 1, 449.99), (97, 7, 1, 79.99),
                (98, 10, 1, 599.99),
                (99, 17, 1, 279.99), (99, 18, 1, 119.99), (99, 4, 3, 49.99),
                (100, 16, 1, 199.99), (100, 15, 4, 69.99)
            ]
            
            cursor.executemany(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                order_items_data
            )
            print(f"✓ Order items inserted")
        else:
            print(f"\n✓ Order items table has sufficient data ({order_items_count} >= {MIN_ORDER_ITEMS})")
        
        conn.commit()
        cursor.close()
        
    except Exception as e:
        conn.rollback()
        print(f"Error populating data: {e}")
        raise

def create_readonly_user(conn):
    """Create a readonly user for the agent"""
    try:
        cursor = conn.cursor()
        readonly_user = os.getenv("DB_READONLY_USER")
        readonly_password = os.getenv("DB_READONLY_PASSWORD")
        
        # Check if user exists
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (readonly_user,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                sql.Identifier(readonly_user)
            ), (readonly_password,))
            print(f"✓ Readonly user '{readonly_user}' created")
        else:
            print(f"✓ Readonly user '{readonly_user}' already exists")
        
        # Grant readonly permissions
        cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE ecommerce TO {}").format(
            sql.Identifier(readonly_user)
        ))
        cursor.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
            sql.Identifier(readonly_user)
        ))
        cursor.execute(sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {}").format(
            sql.Identifier(readonly_user)
        ))
        cursor.execute(sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {}").format(
            sql.Identifier(readonly_user)
        ))
        
        conn.commit()
        print(f"✓ Readonly permissions granted to '{readonly_user}'")
        cursor.close()
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating readonly user: {e}")
        raise

def main():
    """Main setup function"""
    print("=" * 60)
    print("PostgreSQL E-commerce Database Setup")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  - Min Customers: {MIN_CUSTOMERS}")
    print(f"  - Min Products: {MIN_PRODUCTS}")
    print(f"  - Min Orders: {MIN_ORDERS}")
    print(f"  - Min Order Items: {MIN_ORDER_ITEMS}")
    print("=" * 60)
    
    try:
        # Create database
        print("\n[1/4] Creating database...")
        create_database()
        
        # Connect to ecommerce database
        print("\n[2/4] Creating tables...")
        conn = connect_to_ecommerce_db()
        create_tables(conn)
        
        # Populate data
        print("\n[3/4] Populating data...")
        populate_data(conn)
        
        # Create readonly user
        print("\n[4/4] Setting up readonly user...")
        create_readonly_user(conn)
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ Database setup completed successfully!")
        print("=" * 60)
        print("\nYou can now run the agent with readonly access.")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
