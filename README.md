# PostgreSQL E-commerce Database Agents

This project provides two SQL database agent implementations for querying a PostgreSQL e-commerce database:
1. **LangChain Agent** - Using LangChain framework with OpenRouter
2. **Pydantic AI Agent** - Using Pydantic AI with SQLAlchemy

## Features

### Common Features
- **PostgreSQL Integration**: Uses PostgreSQL 15+ as the database
- **Readonly Security**: Agents operate with readonly database credentials
- **E-commerce Schema**: Sample database with customers, products, orders, and order items
- **Automated Setup**: Python script to create and populate the database
- **Smart Data Management**: Checks existing data and only inserts if needed
- **Configurable Thresholds**: Adjustable minimum row counts for data population
- **Error Handling**: Comprehensive error handling throughout

### Pydantic AI Agent Features
- **SQLAlchemy 2.0**: Modern ORM integration with context managers
- **Schema Preloading**: Full database schema loaded on startup
- **Token Management**: Automatic schema truncation if exceeds 2000 tokens
- **Type-Safe Results**: Single Pydantic model with type field (query/error/info)
- **Comprehensive Tests**: Test suite covering query patterns and edge cases

## Prerequisites

1. **PostgreSQL 15+**: Install PostgreSQL on your local machine

### PostgreSQL Installation

#### Windows
1. Download PostgreSQL 15+ from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. Default port is 5432 (keep this unless you have a conflict)
5. Add PostgreSQL to your PATH (installer usually does this automatically)

#### macOS
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

2. **Python 3.8+**: Ensure Python is installed
3. **Dependencies**: Install required Python packages

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install langchain langchain-openai langchain-community psycopg2-binary python-dotenv pydantic-ai sqlalchemy tiktoken pytest
```

## Setup Instructions

### 1. Configure Environment Variables

Edit the `.env` file and update the database credentials:

```env
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432

# Admin credentials (for database setup)
DB_ADMIN_USER=postgres
DB_ADMIN_PASSWORD=your_actual_postgres_password

# Readonly credentials (for agent queries)
DB_READONLY_USER=ecommerce_readonly
DB_READONLY_PASSWORD=readonly_secure_password_123
```

**Important**: Replace `your_actual_postgres_password` with the password you set during PostgreSQL installation.

### 2. Create and Populate the Database

Run the setup script to create the database, tables, and sample data:

```bash
python setup_database.py
```

This script will:
- Create the `ecommerce` database
- Create tables: `customers`, `products`, `orders`, `order_items`
- Populate tables with sample data (if row counts are below thresholds)
- Create a readonly user with appropriate permissions

#### Configuration

You can adjust the minimum row counts in `setup_database.py`:

```python
MIN_CUSTOMERS = 50      # Minimum customers to maintain
MIN_PRODUCTS = 30       # Minimum products to maintain
MIN_ORDERS = 100        # Minimum orders to maintain
MIN_ORDER_ITEMS = 150   # Minimum order items to maintain
```

### 3. Run the SQL Agents

#### LangChain Agent
Start the interactive LangChain SQL agent:

```bash
python sql_agent.py
```

#### Pydantic AI Agent
Start the interactive Pydantic AI SQL agent:

```bash
python pydantic_sql_agent.py
```

The Pydantic AI agent includes:
- SQLAlchemy 2.0 with context managers for connection handling
- Full schema preloading with automatic token monitoring
- Type-safe results with a single QueryResult model
- Better structured error handling

### 4. Run Tests (Pydantic AI Agent)

Run the comprehensive test suite:

```bash
pytest test_pydantic_agent.py -v
```

Test categories:
- **Basic Queries**: Testing the 5 example patterns from sql_agent.py
- **Complex Joins**: Multi-table joins with 2-3 tables
- **Subqueries**: WHERE, SELECT, and correlated subqueries
- **NULL Handling**: IS NULL, COALESCE, and NULL filtering
- **Aggregations**: GROUP BY, HAVING, multiple aggregation functions
- **Edge Cases**: Security (rejecting INSERT/UPDATE/DELETE), empty results, complex filters
- **Data Types**: DECIMAL, TIMESTAMP, string pattern matching
- **Sorting**: ORDER BY with multiple columns, LIMIT clauses

### 5. Remove the Database (Optional)

If you need to completely remove the database and start fresh, run:

```bash
python remove_database.py
```

This script will:
- Prompt for confirmation (type `yes` to proceed)
- Terminate all active connections to the database
- Drop the `ecommerce` database
- Drop the readonly user

**Warning**: This permanently deletes all data and cannot be undone. You can recreate the database by running `setup_database.py` again.

## Usage Examples

Once the agent is running, you can ask natural language questions:

```
Question: How many customers do we have?
Question: What are the top 5 best-selling products?
Question: Show me the total revenue by order status
Question: Which customer has placed the most orders?
Question: What is the average order value?
Question: List all products in the Electronics category
Question: How many orders were completed in the last month?
```

## Database Schema

### Customers
- `customer_id` (PK)
- `first_name`
- `last_name`
- `email` (unique)
- `created_at`

### Products
- `product_id` (PK)
- `name`
- `description`
- `price`
- `stock_quantity`
- `category`
- `created_at`

### Orders
- `order_id` (PK)
- `customer_id` (FK)
- `order_date`
- `total_amount`
- `status`

### Order Items
- `order_item_id` (PK)
- `order_id` (FK)
- `product_id` (FK)
- `quantity`
- `price`

## Security

- The agent uses **readonly credentials** and cannot modify data
- Database credentials are stored in `.env` (never commit this file!)
- Separate admin and readonly users for security

## Troubleshooting

### Connection Error
If you get a connection error:
1. Verify PostgreSQL is running: `psql -U postgres -c "SELECT version();"`
2. Check credentials in `.env` match your PostgreSQL setup
3. Ensure the `ecommerce` database exists (run `setup_database.py`)

### Authentication Failed
- Verify the admin password in `.env` is correct
- Try connecting manually: `psql -U postgres -d ecommerce`

### Permission Denied
- Run `setup_database.py` again to recreate the readonly user
- Ensure the readonly user has SELECT privileges

## Files

### Agent Implementations
- `sql_agent.py` - LangChain SQL agent application
- `pydantic_sql_agent.py` - Pydantic AI SQL agent with SQLAlchemy

### Database Scripts
- `setup_database.py` - Database creation and population script
- `remove_database.py` - Database removal and cleanup script

### Testing
- `test_pydantic_agent.py` - Comprehensive test suite for Pydantic AI agent

### Other
- `opentouter_test.py` - Original OpenRouter test script
- `.env` - Environment variables (credentials)
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Implementation Comparison

| Feature | LangChain Agent | Pydantic AI Agent |
|---------|----------------|-------------------|
| Framework | LangChain | Pydantic AI |
| Database Access | SQLDatabase utility | SQLAlchemy 2.0 |
| Connection Management | Automatic | Context manager |
| Schema Loading | On-demand | Preloaded on startup |
| Token Monitoring | No | Yes (with auto-truncation) |
| Result Type | String/dict | Type-safe Pydantic model |
| Tool Structure | Built-in toolkit | Single custom tool |
| Test Coverage | None | Comprehensive (90+ tests) |
| Error Handling | Built-in | Structured with type field |

## Pydantic AI Agent Architecture

### DatabaseContext Class
- **Purpose**: Manages database connections and schema loading
- **Context Manager**: `get_session()` provides automatic transaction handling
- **Schema Preloading**: Loads full schema on initialization
- **Token Management**: Monitors and truncates schema if needed
- **Query Execution**: `execute_query()` handles SQL execution with result formatting

### QueryResult Model
Single Pydantic model with type field:
- `type: "query"` - Successful query with results
- `type: "error"` - Error occurred (with message)
- `type: "info"` - Informational message or clarification
- `content: str` - Main content (results, error, or info)
- `details: str | None` - Additional details (SQL query, etc.)

### Agent Tool
- `execute_sql_query()` - Single tool for SQL execution
- Security validation (SELECT only)
- Structured error handling
- Result formatting with row limits

## Notes

- Both implementations use Claude Opus 4.5 via OpenRouter by default
- The setup script is idempotent - safe to run multiple times
- Data insertion only occurs when row counts are below thresholds
- Pydantic AI agent monitors token usage and truncates schema if > 2000 tokens
- Both agents are read-only for security (SELECT queries only)
