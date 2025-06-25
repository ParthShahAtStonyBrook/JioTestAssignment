# import time
# start = time.time()
# from qdrant_client import QdrantClient
# from qdrant_client.models import PointStruct
# from qdrant_client.models import VectorParams, Distance
# from sentence_transformers import SentenceTransformer
# import fitz
# import PyPDF2
# import re
# from typing import List
# import uuid
# print(f"Step import took {time.time() - start:.2f} seconds")


# embed_model = SentenceTransformer('./local_models/mpnet_model')
# qdrant = QdrantClient("localhost", port=6333)  

# print(f"Step model took {time.time() - start:.2f} seconds")


# def create_faq_collection():
#     try:
#         # Drop existing collection if it exists
#         collections = qdrant.get_collections()
#         collection_names = [col.name for col in collections.collections]
        
#         if "faq_data" in collection_names:
#             qdrant.delete_collection("faq_data")
#             print("Deleted existing FAQ collection")
        
#         # Create a fresh collection
#         qdrant.create_collection(
#             collection_name="faq_data",
#             vectors_config=VectorParams(
#                 size=768,  # embedding dimension for all-mpnet-base-v2
#                 distance=Distance.COSINE
#             )
#         )
#         print("Created new FAQ collection")
        
#     except Exception as e:
#         print(f"Error creating collection: {e}")

# def extract_text_from_pdf(pdf_path: str) -> str:
#     """Extract text from PDF file"""
#     try:
#         # Method 1: Using PyMuPDF (fitz)
#         doc = fitz.open(pdf_path)
#         text = ""
#         for page_num in range(len(doc)):
#             page = doc.load_page(page_num)
#             text += page.get_text()
#         doc.close()
#         return text
#     except:
#         # Method 2: Fallback to PyPDF2
#         try:
#             with open(pdf_path, 'rb') as file:
#                 reader = PyPDF2.PdfReader(file)
#                 text = ""
#                 for page in reader.pages:
#                     text += page.extract_text()
#             return text
#         except Exception as e:
#             print(f"Error extracting PDF text: {e}")
#             return ""

# def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
#     """Split text into overlapping chunks"""
#     # Clean text
#     # text = re.sub(r'\s+', ' ', text.strip())
    
#     # chunks = []
#     # start = 0
    
#     # while start < len(text):
#     #     end = start + chunk_size
        
#     #     # If not at the end, try to break at sentence or word boundary
#     #     if end < len(text):
#     #         # Look for sentence ending
#     #         sentence_end = text.rfind('.', start, end)
#     #         if sentence_end > start + chunk_size // 2:
#     #             end = sentence_end + 1
#     #         else:
#     #             # Look for word boundary
#     #             word_end = text.rfind(' ', start, end)
#     #             if word_end > start + chunk_size // 2:
#     #                 end = word_end
        
#     #     chunk = text[start:end].strip()
#     #     if chunk:
#     #         chunks.append(chunk)
        
#     #     # Move start position with overlap
#     #     start = end - overlap
#     #     if start >= len(text):
#     #         break
    
#     # return chunks


#     pattern = r'(\d+\..*?\?[\s]*Ans\..*?)(?=\d+\.\s|\Z)'
#     chunks = re.findall(pattern, text, flags=re.DOTALL)
#     # Clean chunks
#     chunks = [chunk.strip().replace('\n', ' ') for chunk in chunks if chunk.strip()]
#     return chunks

# def process_and_store_faq_pdf(pdf_path: str, source_name: str = "FAQ Document"):
#     """Process PDF and store chunks in Qdrant"""
#     try:
#         # Extract text from PDF
#         print(f"Extracting text from {pdf_path}...")
#         text = extract_text_from_pdf(pdf_path)
#         # print(text[900:1500])
        
#         if not text:
#             print("No text extracted from PDF")
#             return False
        
#         # Chunk the text
#         print("Chunking text...")
#         chunks = chunk_text(text, chunk_size=800, overlap=150)
#         print(f"Created {len(chunks)} chunks")
        
#         # Create embeddings and store in Qdrant
#         print("Creating embeddings and storing in Qdrant...")
#         points = []
        
#         for i, chunk in enumerate(chunks):
#             # Create embedding
#             embedding = embed_model.encode(chunk).tolist()
            
#             # Create point for Qdrant
#             point = PointStruct(
#                 id=str(uuid.uuid4()),
#                 vector=embedding,
#                 payload={
#                     "text": chunk,
#                     "source": source_name,
#                     "chunk_id": i,
#                     "chunk_count": len(chunks)
#                 }
#             )
#             points.append(point)
        
#         # Upload to Qdrant in batches
#         batch_size = 100
#         for i in range(0, len(points), batch_size):
#             batch = points[i:i + batch_size]
#             qdrant.upsert(
#                 collection_name="faq_data",
#                 points=batch
#             )
#             print(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        
#         print(f"Successfully stored {len(chunks)} FAQ chunks in Qdrant")
#         return True
        
#     except Exception as e:
#         print(f"Error processing FAQ PDF: {e}")
#         return False
    

# def setup_faq_system(pdf_path: str, source_name: str = "FAQ Document"):
#     """
#     Complete setup for FAQ system
#     """
#     print("Setting up FAQ system...")
    
#     # Step 1: Create collection
#     create_faq_collection()
    
#     # Step 2: Process and store PDF
#     success = process_and_store_faq_pdf(pdf_path, source_name)
    
#     if success:
#         print("FAQ system setup complete!")

#     else:
#         print("FAQ system setup failed!")



# if __name__ == "__main__":
#     # Setup the FAQ system with your PDF
#     print("Staring Process")
#     pdf_file_path = "/Users/parthshah/JioTestAssignment/FAQ_Data/FAQ_Data.pdf"  # Replace with your PDF path
#     setup_faq_system(pdf_file_path, "Company FAQ Document")
#     print(f"Step end took {time.time() - start:.2f} seconds")









import time
import uuid
import re
import fitz  # PyMuPDF
import PyPDF2
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer

# Config
COLLECTION_NAME = "faq_data"
PDF_PATH = "/Users/parthshah/JioTestAssignment/FAQ_Data/FAQ_Data.pdf"  

# Start timing
start = time.time()
print("Loading model...")
model= SentenceTransformer('./local_models/mpnet_model')  
vector_size = model.get_sentence_embedding_dimension()
print(f"Model loaded in {time.time() - start:.2f}s")

qdrant = QdrantClient("localhost", port=6333)

def extract_text(pdf_path: str) -> str:
    """Extract text using PyMuPDF, fallback to PyPDF2."""
    try:
        doc = fitz.open(pdf_path)
        return " ".join(page.get_text() for page in doc)
    except Exception:
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return " ".join(page.extract_text() for page in reader.pages if page.extract_text())
        except Exception as e:
            print(f"PDF extraction failed: {e}")
            return ""

def chunk_text(text: str) -> List[str]:
    """Chunk text using Q&A pattern."""
    pattern = r'(\d+\..*?\?[\s]*Ans\..*?)(?=\d+\.\s|\Z)'
    return [chunk.strip().replace('\n', ' ') for chunk in re.findall(pattern, text, re.DOTALL)]

def recreate_faq_collection():
    if COLLECTION_NAME in [c.name for c in qdrant.get_collections().collections]:
        qdrant.delete_collection(COLLECTION_NAME)
        print("Deleted existing collection.")

    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    print("Created new collection.")

def process_and_store_pdf(pdf_path: str):
    print("Extracting text...")
    text = extract_text(pdf_path)
    if not text:
        print("No text found.")
        return False

    print("Chunking text...")
    chunks = chunk_text(text)
    print(f"Chunked into {len(chunks)} items.")

    print("Encoding and uploading...")
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=model.encode(chunk).tolist(),
            payload={"text": chunk, "source": "Company FAQ Document", "chunk_id": i}
        )
        for i, chunk in enumerate(chunks)
    ]

    for i in range(0, len(points), 100):
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points[i:i+100])
        print(f"Uploaded batch {i//100 + 1}")

    print(f"Done. {len(chunks)} chunks stored.")
    return True


def search_faq(query: str, top_k: int = 3):
    vector = model.encode(query).tolist()
    results = qdrant.query_points(
        collection_name="faq_data",
        query=vector,
        limit=top_k
    )
    print(f"\n🔍 Query: {query}\n")
    for i, res in enumerate(results):
        print(i,res)




def main():
    recreate_faq_collection()
    success = process_and_store_pdf(PDF_PATH)
    print("✅ Complete" if success else "❌ Failed")
    print(f"Total time: {time.time() - start:.2f}s")
    # Sample questions
    # search_faq("What is a liquid fund?")
    # search_faq("Explain large cap vs mid cap stocks.")
    # search_faq("What is a mutual fund?")


if __name__ == "__main__":
    main()
