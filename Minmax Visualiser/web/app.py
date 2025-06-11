from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import threading
import time
import os

# Get the absolute path to the directory containing app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the templates folder
templates_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=templates_dir)
CORS(app)

# Store minimax tree data
minimax_tree_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/minimax_data', methods=['POST'])
def receive_minimax_data():
    global minimax_tree_data
    data = request.json
    if data:
        minimax_tree_data = data
        print("Received minimax data:", data)  # For debugging
        return jsonify({"status": "success", "message": "Data received"}), 200
    return jsonify({"status": "error", "message": "No data received"}), 400

@app.route('/get_minimax_data', methods=['GET'])
def get_minimax_data():
    return jsonify(minimax_tree_data)

def run_flask_app():
    # Use a specific host and port for Flask to avoid conflicts
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    # Run Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True # Allows the main program to exit even if the thread is running
    flask_thread.start()
    
    print("Flask server running on http://127.0.0.1:5000")
    # Keep the main thread alive to allow Flask thread to run
    while True:
        time.sleep(1) 