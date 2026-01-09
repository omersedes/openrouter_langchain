from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, inspect, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Literal
from os import getenv
from dotenv import load_dotenv
import tiktoken

load_dotenv()


class QueryResult(BaseModel):
    """Single model for all SQL operations"""
    type: Literal["query", "error", "info"] = Field(description="Type of result")
    content: str = Field(description="Query result, error message, or info")
    details: str | None = Field(default=None, description="Additional details like SQL query")


class DatabaseContext:
    """Context manager for database connections with SQLAlchemy"""
    
    def __init__(self, db_uri: str):
        self.db_uri = db_uri
        self.engine = create_engine(db_uri)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.full_schema = self._load_full_schema()
        
    def _load_full_schema(self) -> str:
        """Preload full database schema on startup"""
        inspector = inspect(self.engine)
        schema_parts = []
        
        for table_name in inspector.get_table_names():
            schema_parts.append(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            
            for col in columns:
                col_type = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col.get('default') else ""
                schema_parts.append(f"  - {col['name']}: {col_type} {nullable}{default}")
            
            # Get primary keys
            pk = inspector.get_pk_constraint(table_name)
            if pk and pk['constrained_columns']:
                schema_parts.append(f"  PRIMARY KEY: {', '.join(pk['constrained_columns'])}")
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                schema_parts.append(
                    f"  FOREIGN KEY: {', '.join(fk['constrained_columns'])} -> "
                    f"{fk['referred_table']}({', '.join(fk['referred_columns'])})"
                )
        
        return "\n".join(schema_parts)
    
    def get_schema_for_prompt(self, max_tokens: int = 2000) -> str:
        """Get schema for system prompt, with truncation if needed"""
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(self.full_schema)
        
        if len(tokens) <= max_tokens:
            return self.full_schema
        
        # Truncate: keep table names and basic column info, remove descriptions
        inspector = inspect(self.engine)
        schema_parts = []
        
        for table_name in inspector.get_table_names():
            schema_parts.append(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            
            # Basic columns only
            for col in columns:
                col_type = str(col['type'])
                schema_parts.append(f"  - {col['name']}: {col_type}")
            
            # Keep primary and foreign keys as they're critical
            pk = inspector.get_pk_constraint(table_name)
            if pk and pk['constrained_columns']:
                schema_parts.append(f"  PK: {', '.join(pk['constrained_columns'])}")
            
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                schema_parts.append(
                    f"  FK: {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}"
                )
        
        truncated_schema = "\n".join(schema_parts)
        truncated_tokens = encoding.encode(truncated_schema)
        
        print(f"⚠️  Schema truncated: {len(tokens)} -> {len(truncated_tokens)} tokens")
        return truncated_schema
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str) -> str:
        """Execute a SQL query and return results"""
        with self.get_session() as session:
            result = session.execute(text(query))
            
            # Handle different result types
            if result.returns_rows:
                rows = result.fetchall()
                if not rows:
                    return "Query executed successfully. No rows returned."
                
                # Format results as a table
                columns = result.keys()
                output = [" | ".join(str(col) for col in columns)]
                output.append("-" * len(output[0]))
                
                for row in rows[:100]:  # Limit to 100 rows
                    output.append(" | ".join(str(val) for val in row))
                
                if len(rows) > 100:
                    output.append(f"\n... ({len(rows) - 100} more rows)")
                
                return "\n".join(output)
            else:
                return "Query executed successfully."


# Initialize database context
db_uri = f"postgresql://{getenv('DB_READONLY_USER')}:{getenv('DB_READONLY_PASSWORD')}@{getenv('DB_HOST', 'localhost')}:{getenv('DB_PORT', '5432')}/ecommerce"

try:
    db_context = DatabaseContext(db_uri)
    schema_for_prompt = db_context.get_schema_for_prompt(max_tokens=2000)
    print("✓ Connected to database successfully")
    print(f"✓ Schema loaded ({len(tiktoken.get_encoding('cl100k_base').encode(schema_for_prompt))} tokens)")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    print("\nMake sure you have:")
    print("1. Set up the database by running: python setup_database.py")
    print("2. Configured your .env file with database credentials")
    exit(1)


# Initialize the agent with OpenRouter
model = OpenAIModel(
    model_name="anthropic/claude-opus-4.5",
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

agent = Agent(
    model=model,
    result_type=QueryResult,
    system_prompt=f"""You are a SQL query assistant for a PostgreSQL e-commerce database.

Database Schema:
{schema_for_prompt}

Rules:
1. Generate ONLY read-only SQL queries (SELECT statements only)
2. Always use proper PostgreSQL syntax
3. Use table and column names exactly as shown in the schema
4. For aggregations, use appropriate GROUP BY clauses
5. Return results in a clear, formatted way
6. If the query is ambiguous, make reasonable assumptions based on the schema

When responding:
- Set type="query" for successful queries with content containing formatted results
- Set type="error" for errors with content containing the error message
- Set type="info" for clarifications or explanations
- Include the SQL query in the details field when applicable
""",
    deps_type=DatabaseContext,
)


@agent.tool
async def execute_sql_query(ctx: RunContext[DatabaseContext], sql_query: str) -> QueryResult:
    """
    Execute a SQL query against the database.
    
    Args:
        ctx: Runtime context with database connection
        sql_query: The SQL SELECT query to execute
    
    Returns:
        QueryResult with query results or error information
    """
    try:
        # Validate it's a SELECT query
        query_upper = sql_query.strip().upper()
        if not query_upper.startswith("SELECT"):
            return QueryResult(
                type="error",
                content="Only SELECT queries are allowed for security reasons.",
                details=sql_query
            )
        
        # Execute query
        result = ctx.deps.execute_query(sql_query)
        
        return QueryResult(
            type="query",
            content=result,
            details=sql_query
        )
        
    except Exception as e:
        return QueryResult(
            type="error",
            content=f"Query execution failed: {str(e)}",
            details=sql_query
        )


# Example queries
print("\n" + "=" * 60)
print("Pydantic AI SQL Agent Ready - Example Queries")
print("=" * 60)

example_queries = [
    "How many customers do we have?",
    "What are the top 5 best-selling products?",
    "Show me the total revenue by order status",
    "Which customer has placed the most orders?",
    "What is the average order value?"
]

print("\nYou can ask questions like:")
for i, query in enumerate(example_queries, 1):
    print(f"{i}. {query}")

print("\n" + "=" * 60)


# Interactive mode
if __name__ == "__main__":
    print("\nEnter your questions (or 'quit' to exit):\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not question:
                continue
            
            print("\nProcessing...\n")
            
            # Run agent synchronously
            result = agent.run_sync(question, deps=db_context)
            
            # Display result
            if result.data.type == "query":
                print(f"\nAnswer:\n{result.data.content}")
                if result.data.details:
                    print(f"\nSQL Query:\n{result.data.details}")
            elif result.data.type == "error":
                print(f"\n❌ Error: {result.data.content}")
                if result.data.details:
                    print(f"Query attempted: {result.data.details}")
            else:
                print(f"\nℹ️  {result.data.content}")
            
            print("\n" + "-" * 60)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("-" * 60)
