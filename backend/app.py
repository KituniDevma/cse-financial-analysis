# app.py: Flask API for LLM queries

from flask import Flask, request, jsonify
from flask_cors import CORS
from scripts.llm_query import agent

app = Flask(__name__)
CORS(app)  # Allow React frontend

@app.route('/query', methods=['POST'])
def query():
    question = request.json.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    try:
        response = agent.invoke(question)
        return jsonify({'answer': response['output']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)