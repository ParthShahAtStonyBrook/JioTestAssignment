import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Configure CORS to accept requests from the frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Basic configuration
OLLAMA_URL = "http://localhost:11434"

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def call_ollama(prompt, image_path, model="qwen2.5vl:3b"):
    """Send a prompt to Ollama and get response"""
    url = f"{OLLAMA_URL}/api/generate"

    image_base64 = encode_image_to_base64(image_path)
    
    data = {
        "model": model,
        "prompt": prompt,
        "images": [image_base64],
        "stream": False  # Set to True for streaming responses
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['response']
        
    except requests.exceptions.RequestException as e:
        return f"Error calling Ollama: {e}"

@app.route('/')
def home():
    return jsonify({"status": "API is running"})

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