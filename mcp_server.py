# import sqlite3
import argparse
import psycopg2
from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
# from typing import List, Dict
# from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import sqlite3
import logging
logging.basicConfig(level=logging.INFO)

# Initialize Qdrant client
qdrant = QdrantClient("localhost", port=6333)

# Initialize sentence transformer
model = SentenceTransformer("all-MiniLM-L6-v2")
model_faq = SentenceTransformer('./local_models/mpnet_model')  


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


# Connect to Qdrant
qdrant = QdrantClient(host="localhost", port=6333)


@mcp.tool()
def search_orders_tool(query: str, user_id : int = None) -> list:
    """ Search through user's order history using a SELECT postgres sql query. Returns a list of orders with their details.

    Args:
        query (str): Postgres SQL SELECT query. Modify the query to fetch required data from the database.

    Returns:
        list: List of tuples containing the query results.

    Note : Do not add additional parameters to the query.


    Examples:

    user: Fetch all orders
    query : SELECT * FROM order_items WHERE user_id = `user_id`;

    user : Fetch order which was ordered on `DATE`
    query : SELECT * FROM order_items WHERE date = `DATE` AND user_id=`user_id`;
    Note: If date is 18th June 2025, then query should have date as '06-18-2025'

    user : What is the most expensive thing I have bought
    query :
    WITH most_expensive_item AS (
        SELECT order_id
        FROM order_items
        WHERE user_id = `user_id`
        ORDER BY total DESC
        LIMIT 1
    )
    SELECT *
    FROM order_items
    WHERE order_id = (SELECT order_id FROM most_expensive_item);

    user : What is the least expensive thing I have bought
    query :
    WITH least_expensive_item AS (
        SELECT order_id
        FROM order_items
        WHERE user_id = `user_id`
        ORDER BY total ASC
        LIMIT 1
    )
    SELECT *
    FROM order_items
    WHERE order_id = (SELECT order_id FROM least_expensive_item);

    user : Show orders with status as `STATUS`
    query : 
    SELECT * FROM order_items
    WHERE status = `STATUS`
    AND user_id = `user_id`;

    user: Show order details for order_id = `order_id`
    query:
    SELECT * FROM order_items
    WHERE order_id = `order_id`
    AND user_id = `user_id`;

    There might be times where you would have to combine different queries to form a new one.

    """
    logging.info("User id is : %s",str(user_id))
    logging.info("Query is : %s",str(query))
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        order_details = cursor.fetchall()
        logging.info("Fetched order details: %s", order_details)
        return order_details
    except Exception as e:
        logging.error("Error reading data: %s", e)
        return []
    finally:
        conn.close()



@mcp.tool()
def search_faq_tool(query: str, top_k: int = 3) -> list:
    """
    Perform semantic search over Mutual Fund FAQ data stored in Qdrant.

    This function uses dense embeddings to retrieve the most relevant FAQ chunks
    based on the user's query. The FAQ data contains question-answer pairs related
    to mutual funds.

    Args:
        query (str): The user's natural language question about mutual funds.
        top_k (int): The number of most relevant FAQ entries to return (default: 3).

    Returns:
        List[dict]: A list of matching FAQ chunks, each with the following keys:
            - 'text': The matching text chunk from the FAQ.
            - 'source': Source label (e.g. 'FAQ Document').
            - 'chunk_id': Index of the chunk within the source.
            - 'chunk_count': Total number of chunks in the source.
            - 'score': Similarity score (higher means more relevant).

    Remember: Do not give out the source of the information. Reply like you know all of this and you are not fetching the data from somewhere.
    """

    try:
        if not query or query.strip() == "":
            return [{"error": "Query cannot be empty"}]
        
        
        # Create embedding for the query
        vector = model_faq.encode(query).tolist()
        
        # Search in Qdrant
        results = qdrant.query_points(
            collection_name="faq_data",
            query=vector,
            limit=top_k
        )

        
        # Format results
        faq_results = []
        
        for res in results:
            faq_results += [res]
        
        return faq_results
        
    except Exception as e:
        logging.error(f"FAQ search failed: {str(e)}")
        return [{"error": f"FAQ search failed: {str(e)}"}]


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



