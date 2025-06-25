import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from llama_index.core import Settings
from decimal import Decimal
import json
import asyncio,nest_asyncio
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.agent.workflow import (
    FunctionAgent, 
    ToolCallResult, 
    ToolCall)
from llama_index.core.workflow import Context
import re

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

# Configure CORS to accept requests from the frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# JWT Configuration
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Change this in production!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# Basic configuration
OLLAMA_URL = "http://localhost:11434"

# Database configuration
DB_CONFIG = {
    'dbname': 'app',
    'user': 'admin',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def call_ollama(prompt, image_path=None, model="qwen2.5vl:3b"):
    """Send a prompt to Ollama and get response"""
    url = f"{OLLAMA_URL}/api/generate"
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    if image_path:
        image_base64 = encode_image_to_base64(image_path)
        data["images"] = [image_base64]
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['response']
        
    except requests.exceptions.RequestException as e:
        return f"Error calling Ollama: {e}"

nest_asyncio.apply()

# Initialize LLM and MCP client globally (these are safe to reuse)
llm = Ollama(model="qwen2.5:3b", request_timeout=120.0)
Settings.llm = llm

mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
mcp_tools = McpToolSpec(client=mcp_client)

SYSTEM_PROMPT = """You are a helpful e-commerce assistant that helps users track their orders and provides information about their purchases and solve user questions based on mutual fund. You have access to the user's order history through the search_orders_tool.

CRITICAL SECURITY RULES:
1. NEVER access or reveal order information for any user other than the current user.
2. NEVER make assumptions about user IDs or try to guess them.
3. NEVER combine or compare data across different users.
4. If asked about other user id's data, respond with "I can only access your own order information."
5. Do not change or override user_id. Always trust the user_id passed to you.

ORDER INFORMATION RULES:
1. When showing order details, ALWAYS include:
   - Complete item details (name, quantity, price)
   - Order status (pending/completed)
   - Order date
2. Format prices with 2 decimal places (e.g., $99.99)
3. For pending orders, clearly indicate the status
4. For completed orders, show the completion date
5. Do not ask the user for their user_id

SEARCH CAPABILITIES:
1. You can search orders by:
   - Order status (pending/completed)
   - Item names
   - Dates
   - Any combination of the above
2. Always use the search_orders_tool with the current user's ID
3. Never search order history without a user ID
4. When answering questions about Mutual funds use the search_faq_tool and provide a short reply.


USER INTERACTION:
1. Be clear and concise in responses
2. If asked about other users' data, firmly decline and explain you can only access the current user's data
3. If no user ID is provided, ask for it before proceeding
4. Format responses in a clear, readable way
5. Always verify the user ID before showing any order information
6. Do not reveal your sources for the response that you provide
7. Do not give out similarity scores in response
8. Do not say that where the information you are using is coming from

Remember: Data privacy is critical. Never access or reveal information about other users' orders."""

async def get_agent(tools: McpToolSpec):
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with Our Database software.",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent

def clean_agent_output(output: str) -> str:
    # Remove similarity scores
    output = re.sub(r'\(Similarity Score:.*?\)', '', output)
    # Remove source markers like "FAQ Document:"
    output = re.sub(r'- \*\*FAQ Document\*\*:\s*', '', output)
    # Remove JSON fields like "source": "...", or "similarity_score": ...
    output = re.sub(r'"(source|similarity_score)"\s*:\s*".*?",?', '', output)
    # Clean up leftover commas or whitespace
    output = re.sub(r',\s*}', '}', output)
    return output.strip()

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    user_id: int,
    verbose: bool = False,
):
    content_with_id = f"[USER_ID: {user_id}] {message_content}"
    handler = agent.run(content_with_id, ctx=agent_context)

    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            event.tool_kwargs['user_id'] = user_id
            print(event.tool_kwargs['user_id'])
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    cleaned = clean_agent_output(str(response))
    return cleaned

def handle_text_command(text, user_id=None):
    """Handle text commands and return appropriate responses"""
    async def process_request():
        # Create fresh agent and context for each request
        agent = await get_agent(mcp_tools)
        agent_context = Context(agent)


        return await handle_user_message(text, agent, agent_context, verbose=True,user_id= user_id)
    
    response = asyncio.run(process_request())
    return {
        'type': 'text',
        'content': response
    }


@app.route('/chat', methods=['POST'])
@jwt_required()
def chat_endpoint():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data['message']
        user_id = int(get_jwt_identity())
        print("User id is ", user_id)
        response = handle_text_command(message, user_id)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/')
def home():
    return jsonify({"status": "API is running"})

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Hash the password
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if username or email already exists
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            return jsonify({'error': 'Username or email already exists'}), 409

        # Insert new user
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (username, email, password_hash)
        )
        user_id = cur.fetchone()['id']
        conn.commit()

        # Create access token
        access_token = create_access_token(identity=str(user_id))
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({'error': 'Missing username or password'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Get user by username
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Create access token
        access_token = create_access_token(identity=str(user['id']))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/auth/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        user_id = int(get_jwt_identity())
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, username, email, created_at FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Protect all routes that require authentication
@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    try:
        user_id = int(get_jwt_identity())
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all orders for the current user
        cur.execute("""
            SELECT id, date, status 
            FROM orders 
            WHERE user_id = %s
            ORDER BY date DESC
        """, (user_id,))
        orders = cur.fetchall()
        
        # Get items for each order
        for order in orders:
            cur.execute("""
                SELECT id, name, quantity, price 
                FROM order_items 
                WHERE order_id = %s
            """, (order['id'],))
            order['items'] = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify(orders)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if not file:
            return jsonify({'error': 'Empty file provided'}), 400
        
        # Save the uploaded file temporarily
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        # Create the prompt
        prompt = "Reply in exactly 2 lines. First line describing the image. Second line should say '1' if there is any defect or is product is broken else '0'"

        
        # Call Ollama for analysis
        response = call_ollama(prompt, file_path)

        list_response = response.split('.')
        
        result = {
            'analysis': list_response[0],
            'status': list_response[1],
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 