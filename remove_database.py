import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv
import os

load_dotenv()

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

def confirm_removal():
    """Prompt user for confirmation before removing database"""
    database_name = "ecommerce"
    readonly_user = os.getenv("DB_READONLY_USER", "ecommerce_readonly")
    
    print("\n" + "="*60)
    print("⚠️  WARNING: DATABASE REMOVAL")
    print("="*60)
    print(f"\nThis will permanently delete:")
    print(f"  • Database: {database_name}")
    print(f"  • User: {readonly_user}")
    print(f"  • All data in the database (customers, products, orders, etc.)")
    print("\n⚠️  THIS OPERATION CANNOT BE UNDONE!")
    print("="*60)
    
    response = input("\nAre you sure you want to proceed? (yes/no): ").strip().lower()
    
    if response == "yes":
        return True
    else:
        print("\n✓ Operation cancelled. Database was not removed.")
        return False

def terminate_connections(conn, database_name):
    """Terminate all active connections to the database"""
    try:
        cursor = conn.cursor()
        
        # Terminate all connections to the database (except our own)
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
              AND pid <> pg_backend_pid()
        """, (database_name,))
        
        terminated_count = cursor.rowcount
        if terminated_count > 0:
            print(f"✓ Terminated {terminated_count} active connection(s) to '{database_name}'")
        
        cursor.close()
    except Exception as e:
        print(f"Warning: Error terminating connections: {e}")
        # Continue anyway - database might not exist

def drop_database(conn, database_name):
    """Drop the database if it exists"""
    try:
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))
            print(f"✓ Database '{database_name}' has been removed")
        else:
            print(f"✓ Database '{database_name}' does not exist (nothing to remove)")
        
        cursor.close()
    except Exception as e:
        print(f"Error dropping database: {e}")
        raise

def drop_user(conn, username):
    """Drop the readonly user if it exists"""
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(sql.SQL("DROP USER {}").format(sql.Identifier(username)))
            print(f"✓ User '{username}' has been removed")
        else:
            print(f"✓ User '{username}' does not exist (nothing to remove)")
        
        cursor.close()
    except Exception as e:
        print(f"Error dropping user: {e}")
        raise

def main():
    """Main function to remove the database and user"""
    database_name = "ecommerce"
    readonly_user = os.getenv("DB_READONLY_USER", "ecommerce_readonly")
    
    # Get user confirmation
    if not confirm_removal():
        return
    
    conn = None
    try:
        print("\n" + "-"*60)
        print("Starting database removal process...")
        print("-"*60 + "\n")
        
        # Connect to PostgreSQL
        conn = connect_to_postgres()
        
        # Terminate active connections
        terminate_connections(conn, database_name)
        
        # Drop the database
        drop_database(conn, database_name)
        
        # Drop the readonly user
        drop_user(conn, readonly_user)
        
        print("\n" + "="*60)
        print("✓ Database removal completed successfully")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ Error during removal process: {e}")
        print("="*60)
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
