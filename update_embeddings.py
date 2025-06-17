import psycopg2
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams, Distance
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_or_create_collection(qdrant_client, collection_name, vector_size):
    """Check if collection exists, if not create it"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if collection_name not in collection_names:
            logger.info(f"Creating collection {collection_name}")
            qdrant_client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
        else:
            logger.info(f"Collection {collection_name} already exists")
    except Exception as e:
        logger.error(f"Error managing collection: {str(e)}")
        raise

def get_db_connection():
    """Create database connection with error handling"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="app",
            user="admin",
            password="root"
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

def fetch_all_orders(cursor):
    """Fetch all orders with their items"""
    try:
        cursor.execute("""
            SELECT 
                o.id AS order_id,
                o.user_id,
                o.date,
                o.status,
                json_agg(json_build_object(
                    'name', oi.name,
                    'quantity', oi.quantity,
                    'price', oi.price
                )) AS items
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            GROUP BY o.id, o.user_id, o.date, o.status
            ORDER BY o.date DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        raise

def main():
    try:
        # Initialize models and clients
        logger.info("Initializing models and clients")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        vector_size = model.get_sentence_embedding_dimension()
        qdrant = QdrantClient("localhost", port=6333)

        # Ensure collection exists
        get_or_create_collection(qdrant, "user_orders", vector_size)

        # Connect to PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all orders
        logger.info("Fetching orders from database")
        rows = fetch_all_orders(cursor)
        
        points = []
        for row in rows:
            order_id, user_id, date, status, items = row
            # Format items with prices
            item_descriptions = ", ".join(
                f"{item['quantity']}× {item['name']} (${item['price']:.2f})" for item in items
            )
            date_str = date.strftime("%B %d, %Y")

            # Natural language summary with prices
            text = f"On {date_str}, user {user_id} ordered {item_descriptions}. The order status was {status}."
            logger.debug(f"Processing order {order_id}: {text}")

            # Generate embedding
            vector = model.encode(text)

            # Create Qdrant point with complete item details
            points.append(
                PointStruct(
                    id=int(order_id),
                    vector=vector.tolist(),
                    payload={
                        "user_id": user_id,
                        "order_id": order_id,
                        "summary": text,
                        "status": status,
                        "date": date.isoformat(),
                        "items": [
                            {
                                "name": item["name"],
                                "quantity": item["quantity"],
                                "price": float(item["price"])  # Ensure price is float
                            }
                            for item in items
                        ]
                    }
                )
            )

        # Upload to Qdrant in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            logger.info(f"Uploading batch {i//batch_size + 1} of {(len(points) + batch_size - 1)//batch_size}")
            qdrant.upsert(
                collection_name="user_orders",
                points=batch
            )

        logger.info(f"Successfully indexed {len(points)} orders into Qdrant")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        logger.info("Database connections closed")

if __name__ == "__main__":
    main()
