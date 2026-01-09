from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents.agent_types import AgentType
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM
model_name = "anthropic/claude-opus-4.5"
llm = ChatOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model=model_name,
)

# Connect to PostgreSQL database with readonly credentials
db_uri = f"postgresql://{getenv('DB_READONLY_USER')}:{getenv('DB_READONLY_PASSWORD')}@{getenv('DB_HOST', 'localhost')}:{getenv('DB_PORT', '5432')}/ecommerce"

try:
    db = SQLDatabase.from_uri(db_uri)
    print("✓ Connected to database successfully")
    print(f"✓ Available tables: {db.get_usable_table_names()}")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    print("\nMake sure you have:")
    print("1. Set up the database by running: python setup_database.py")
    print("2. Configured your .env file with database credentials")
    exit(1)

# Create SQL agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# Example queries
print("\n" + "=" * 60)
print("SQL Agent Ready - Example Queries")
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
            response = agent_executor.invoke({"input": question})
            print(f"\nAnswer: {response['output']}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("-" * 60)
