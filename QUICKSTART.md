# Quick Start Guide

## Get Running in 5 Minutes

### 1. Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### 2. Configure Database (1 min)
Edit `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_ADMIN_USER=postgres
DB_ADMIN_PASSWORD=your_postgres_password
DB_READONLY_USER=ecommerce_readonly
DB_READONLY_PASSWORD=readonly_secure_password_123
```

### 3. Setup Database (2 min)
```bash
python setup_database.py
```

Expected output:
```
✓ Database 'ecommerce' created successfully
✓ Tables created successfully
✓ Customers inserted
✓ Products inserted
✓ Orders inserted
✓ Order items inserted
✓ Readonly permissions granted
```

### 4. Run the Agent (1 min)

#### Option A: Pydantic AI Agent (Recommended)
```bash
python pydantic_sql_agent.py
```

#### Option B: LangChain Agent
```bash
python sql_agent.py
```

### 5. Try Example Queries

```
Question: How many customers do we have?
Question: What are the top 5 best-selling products?
Question: Show me the total revenue by order status
```

Type `quit` to exit.

## Run Tests

```bash
pytest test_pydantic_agent.py -v
```

## Key Differences

| Feature | LangChain Agent | Pydantic AI Agent |
|---------|----------------|-------------------|
| **Connection** | Built-in utility | SQLAlchemy with context manager |
| **Schema** | On-demand | Preloaded (faster) |
| **Results** | String/dict | Type-safe Pydantic model |
| **Token Mgmt** | No | Yes (auto-truncate if > 2000) |
| **Tests** | None | 90+ comprehensive tests |

## Troubleshooting

**Connection Error?**
- Verify PostgreSQL is running
- Check `.env` credentials
- Run `setup_database.py`

**Import Error?**
- Run `pip install -r requirements.txt`
- Ensure Python 3.8+

**Permission Denied?**
- Run `setup_database.py` to create readonly user

## Next Steps

1. ✅ Read `IMPLEMENTATION_SUMMARY.md` for architecture details
2. ✅ Check `README.md` for full documentation
3. ✅ Explore `test_pydantic_agent.py` for query examples
4. ✅ Modify queries to explore the database schema
