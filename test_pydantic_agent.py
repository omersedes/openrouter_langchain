"""
Test suite for Pydantic AI SQL Agent
Focuses on query patterns from sql_agent.py and edge cases
"""
import pytest
from pydantic_sql_agent import agent, db_context, QueryResult
from dotenv import load_dotenv

load_dotenv()


class TestBasicQueries:
    """Test basic query patterns from sql_agent.py examples"""
    
    def test_count_customers(self):
        """Test: How many customers do we have?"""
        result = agent.run_sync("How many customers do we have?", deps=db_context)
        
        assert result.data.type in ["query", "info"]
        assert result.data.content is not None
        if result.data.type == "query":
            assert "50" in result.data.content or "customer" in result.data.content.lower()
    
    def test_top_selling_products(self):
        """Test: What are the top 5 best-selling products?"""
        result = agent.run_sync("What are the top 5 best-selling products?", deps=db_context)
        
        assert result.data.type in ["query", "info"]
        assert result.data.content is not None
        if result.data.type == "query":
            # Should contain product information
            assert result.data.details is not None  # SQL query should be included
            assert "SELECT" in result.data.details.upper()
    
    def test_revenue_by_status(self):
        """Test: Show me the total revenue by order status"""
        result = agent.run_sync("Show me the total revenue by order status", deps=db_context)
        
        assert result.data.type in ["query", "info"]
        assert result.data.content is not None
        if result.data.type == "query":
            # Should have status categories
            content_lower = result.data.content.lower()
            assert any(status in content_lower for status in ["completed", "pending", "shipped", "cancelled"])
    
    def test_customer_most_orders(self):
        """Test: Which customer has placed the most orders?"""
        result = agent.run_sync("Which customer has placed the most orders?", deps=db_context)
        
        assert result.data.type in ["query", "info"]
        assert result.data.content is not None
        if result.data.type == "query":
            assert result.data.details is not None
            # Should involve joins or subqueries
            assert "customer" in result.data.details.lower()
    
    def test_average_order_value(self):
        """Test: What is the average order value?"""
        result = agent.run_sync("What is the average order value?", deps=db_context)
        
        assert result.data.type in ["query", "info"]
        assert result.data.content is not None
        if result.data.type == "query":
            # Should contain AVG function
            assert "AVG" in result.data.details.upper() or "average" in result.data.content.lower()


class TestComplexJoins:
    """Test complex multi-table joins"""
    
    def test_customer_order_details(self):
        """Test joining customers, orders, and order_items"""
        result = agent.run_sync(
            "Show me customer names with their total spending and number of orders",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            # Should join multiple tables
            assert "JOIN" in query_upper
            assert "customers" in result.data.details.lower()
    
    def test_product_order_relationship(self):
        """Test complex join across products, order_items, and orders"""
        result = agent.run_sync(
            "Which products have never been ordered?",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            # Should use LEFT JOIN or NOT EXISTS
            query_upper = result.data.details.upper()
            assert "LEFT" in query_upper or "NOT EXISTS" in query_upper or "NOT IN" in query_upper
    
    def test_three_table_join(self):
        """Test joining customers, orders, and products through order_items"""
        result = agent.run_sync(
            "Show me all customers who bought laptops",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            # Should join multiple tables
            query_lower = result.data.details.lower()
            assert query_lower.count("join") >= 2  # At least 2 joins needed


class TestSubqueries:
    """Test queries with subqueries"""
    
    def test_subquery_in_where(self):
        """Test subquery in WHERE clause"""
        result = agent.run_sync(
            "Show me customers who have placed orders with total amount above the average",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            # Should contain subquery with AVG
            assert "(" in result.data.details  # Subquery indicator
    
    def test_correlated_subquery(self):
        """Test correlated subquery"""
        result = agent.run_sync(
            "Find products that are priced above the average price in their category",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
    
    def test_subquery_in_select(self):
        """Test subquery in SELECT clause"""
        result = agent.run_sync(
            "Show each customer with their total number of orders",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            # Could use subquery or JOIN with GROUP BY
            assert "COUNT" in query_upper or "GROUP BY" in query_upper


class TestNullHandling:
    """Test NULL value handling"""
    
    def test_null_filter(self):
        """Test filtering NULL values"""
        result = agent.run_sync(
            "Show me products without a description",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "IS NULL" in query_upper or "IS NOT NULL" in query_upper
    
    def test_coalesce_usage(self):
        """Test COALESCE for NULL handling"""
        result = agent.run_sync(
            "List all products with their descriptions, showing 'No description' if empty",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            # May use COALESCE or CASE
            query_upper = result.data.details.upper()
            assert "COALESCE" in query_upper or "CASE" in query_upper or "IS NULL" in query_upper


class TestAggregations:
    """Test various aggregation functions"""
    
    def test_multiple_aggregations(self):
        """Test multiple aggregate functions in one query"""
        result = agent.run_sync(
            "Show me the min, max, and average product prices by category",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "GROUP BY" in query_upper
            # Should have multiple aggregations
            agg_count = sum(1 for func in ["MIN", "MAX", "AVG", "SUM", "COUNT"] if func in query_upper)
            assert agg_count >= 2
    
    def test_having_clause(self):
        """Test HAVING clause with aggregation"""
        result = agent.run_sync(
            "Show me customers who have placed more than 5 orders",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "GROUP BY" in query_upper
            assert "HAVING" in query_upper or "WHERE" in query_upper


class TestEdgeCases:
    """Test edge cases and security"""
    
    def test_security_no_insert(self):
        """Test that INSERT queries are rejected"""
        result = agent.run_sync(
            "INSERT INTO customers (first_name, last_name, email) VALUES ('Test', 'User', 'test@test.com')",
            deps=db_context
        )
        
        assert result.data.type == "error"
        assert "not allowed" in result.data.content.lower() or "only select" in result.data.content.lower()
    
    def test_security_no_update(self):
        """Test that UPDATE queries are rejected"""
        result = agent.run_sync(
            "UPDATE customers SET email = 'new@email.com' WHERE customer_id = 1",
            deps=db_context
        )
        
        assert result.data.type == "error"
        assert "not allowed" in result.data.content.lower() or "only select" in result.data.content.lower()
    
    def test_security_no_delete(self):
        """Test that DELETE queries are rejected"""
        result = agent.run_sync(
            "DELETE FROM customers WHERE customer_id = 1",
            deps=db_context
        )
        
        assert result.data.type == "error"
        assert "not allowed" in result.data.content.lower() or "only select" in result.data.content.lower()
    
    def test_security_no_drop(self):
        """Test that DROP queries are rejected"""
        result = agent.run_sync(
            "DROP TABLE customers",
            deps=db_context
        )
        
        assert result.data.type == "error"
        assert "not allowed" in result.data.content.lower() or "only select" in result.data.content.lower()
    
    def test_empty_result(self):
        """Test query that returns no rows"""
        result = agent.run_sync(
            "Show me customers with first name 'ZZZNonexistent'",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        # Should handle empty results gracefully
    
    def test_complex_filter(self):
        """Test complex WHERE clause with multiple conditions"""
        result = agent.run_sync(
            "Show me orders placed by customers whose last name starts with 'S' and have a total amount over 500",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "WHERE" in query_upper
            assert "AND" in query_upper or "OR" in query_upper


class TestDataTypes:
    """Test handling of different data types"""
    
    def test_decimal_handling(self):
        """Test queries with DECIMAL types (prices, amounts)"""
        result = agent.run_sync(
            "Show me products priced between 100 and 500",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "BETWEEN" in query_upper or (">" in result.data.details and "<" in result.data.details)
    
    def test_timestamp_handling(self):
        """Test queries with TIMESTAMP types"""
        result = agent.run_sync(
            "Show me orders placed in the last 30 days",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            # Should use date functions
            query_upper = result.data.details.upper()
            assert any(keyword in query_upper for keyword in ["NOW()", "CURRENT_", "INTERVAL", "DATE"])
    
    def test_string_pattern_matching(self):
        """Test string pattern matching with LIKE"""
        result = agent.run_sync(
            "Find all customers whose email contains 'gmail'",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "LIKE" in query_upper or "ILIKE" in query_upper


class TestSorting:
    """Test ORDER BY and LIMIT clauses"""
    
    def test_order_by_desc(self):
        """Test descending order"""
        result = agent.run_sync(
            "Show me the 10 most expensive products",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "ORDER BY" in query_upper
            assert "DESC" in query_upper
            assert "LIMIT" in query_upper or "TOP" in query_upper
    
    def test_multiple_order_columns(self):
        """Test ordering by multiple columns"""
        result = agent.run_sync(
            "List customers ordered by last name and then first name",
            deps=db_context
        )
        
        assert result.data.type in ["query", "info"]
        if result.data.type == "query":
            assert result.data.details is not None
            query_upper = result.data.details.upper()
            assert "ORDER BY" in query_upper
            # Should have comma in ORDER BY clause
            order_by_index = query_upper.find("ORDER BY")
            if order_by_index != -1:
                after_order_by = result.data.details[order_by_index:]
                assert "," in after_order_by


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
