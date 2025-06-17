# import sqlite3
import argparse
import psycopg2
from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from typing import List, Dict
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

mcp = FastMCP('defect_detection')

def init_db():
    # Connect to PostgreSQL running in Docker
    conn = psycopg2.connect(
        host="localhost",     
        port=5432,              
        database="app",  
        user="admin",           
        password="root"  
    )
    
    cursor = conn.cursor()
    conn.commit()
    return conn, cursor


# Same model used for indexing
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Qdrant
qdrant = QdrantClient(host="localhost", port=6333)


# @mcp.tool()
# def add_data(query: str) -> bool:
#     """Add new data to the people table using a SQL INSERT query.

#     Args:
#         query (str): SQL INSERT query following this format:
#             INSERT INTO people (name, age, profession)
#             VALUES ('John Doe', 30, 'Engineer')
        
#     Schema:
#         - name: Text field (required)
#         - age: Integer field (required)
#         - profession: Text field (required)
#         Note: 'id' field is auto-generated
    
#     Returns:
#         bool: True if data was added successfully, False otherwise
    
#     Example:
#         >>> query = '''
#         ... INSERT INTO people (name, age, profession)
#         ... VALUES ('Alice Smith', 25, 'Developer')
#         ... '''
#         >>> add_data(query)
#         True
#     """
#     conn, cursor = init_db()
#     try:
#         cursor.execute(query)
#         conn.commit()
#         return True
#     except sqlite3.Error as e:
#         print(f"Error adding data: {e}")
#         return False
#     finally:
#         conn.close()

# @mcp.tool()
# def read_data(query: str = '''SELECT 
#     u.username,
#     o.id AS order_id,
#     o.date AS order_date,
#     o.status AS order_status,
#     oi.id AS item_id,
#     oi.name AS item_name,
#     oi.quantity,
#     oi.price
# FROM orders o
# JOIN users u ON o.user_id = u.id
# JOIN order_items oi ON o.id = oi.order_id
# ORDER BY o.date DESC;''') -> list:
#     """Read data from the users table using a SQL SELECT query.

#     Args:
#         query (str, optional): SQL SELECT query. Defaults to "SELECT u.username, o.id AS order_id, o.date AS order_date, o.status AS order_status, oi.id AS item_id, oi.name AS item_name, oi.quantity, oi.price FROM orders o JOIN users u ON o.user_id = u.id JOIN order_items oi ON o.id = oi.order_id ORDER BY o.date DESC;
# ".
    
#     Returns:
#         list: List of tuples containing the query results.
#     """
#     conn, cursor = init_db()
#     try:
#         cursor.execute(query)
#         return cursor.fetchall()
#     except sqlite3.Error as e:
#         print(f"Error reading data: {e}")
#         return []
#     finally:
#         conn.close()


@mcp.tool()
def search_orders_tool(query: str, user_id: int = None) -> List[Dict]:
    """Search through user's order history. Returns a list of orders with their details.
    
    Args:
        query: String to search for in orders
        user_id: Required user ID to filter results. If not provided, returns empty list.
        
    Returns:
        List of dictionaries containing order details including:
        - order_id: The order ID
        - status: Order status (pending/completed)
        - date: Order date
        - items: List of items with name, quantity, and price
        - score: Search relevance score
        
    Security:
        - Requires user_id parameter
        - Only returns orders for the specified user_id
        - Returns empty list if user_id is not provided
    """
    try:
        # Security check: Require user_id
        if user_id is None:
            print("Security: search_orders_tool called without user_id")
            return []
            
        # Initialize Qdrant client
        qdrant = QdrantClient("localhost", port=6333)
        
        # Initialize sentence transformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Generate query embedding
        query_vector = model.encode(query).tolist()
        
        # Create strict user filter
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )
            ]
        )
        
        # Search in Qdrant with strict user filter
        search_result = qdrant.search(
            collection_name="user_orders",
            query_vector=query_vector,
            limit=5,
            query_filter=search_filter
        )
        
        # Format results
        formatted_results = []
        for result in search_result:
            payload = result.payload
            # Double-check user_id in payload matches requested user_id
            if payload.get("user_id") != user_id:
                continue
                
            formatted_results.append({
                "order_id": payload["order_id"],
                "status": payload["status"],
                "date": payload["date"],
                "items": payload["items"],
                "score": result.score
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error in search_orders_tool: {str(e)}")
        return []



if __name__ == "__main__":
    # Start the server
    print("🚀Starting server... ")

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run mcp_server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)



