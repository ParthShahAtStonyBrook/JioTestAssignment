import sqlite3
import argparse
import psycopg2
from mcp.server.fastmcp import FastMCP

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

@mcp.tool()
def read_data(query: str = '''SELECT 
    u.username,
    o.id AS order_id,
    o.date AS order_date,
    o.status AS order_status,
    oi.id AS item_id,
    oi.name AS item_name,
    oi.quantity,
    oi.price
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON o.id = oi.order_id
ORDER BY o.date DESC;''') -> list:
    """Read data from the users table using a SQL SELECT query.

    Args:
        query (str, optional): SQL SELECT query. Defaults to "SELECT u.username, o.id AS order_id, o.date AS order_date, o.status AS order_status, oi.id AS item_id, oi.name AS item_name, oi.quantity, oi.price FROM orders o JOIN users u ON o.user_id = u.id JOIN order_items oi ON o.id = oi.order_id ORDER BY o.date DESC;
".
    
    Returns:
        list: List of tuples containing the query results.
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        conn.close()



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



