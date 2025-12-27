import os
import subprocess
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'llamaforge_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
MODELS_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# State management for background tasks
training_process = None

def stream_logs(process):
    """Streams stdout from the subprocess to the web client."""
    for line in iter(process.stdout.readline, ''):
        socketio.emit('log_update', {'data': line.strip()})
    process.stdout.close()
    process.wait()
    socketio.emit('log_update', {'data': '--- Process Finished ---'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models', methods=['GET'])
def list_models():
    models = [d for d in os.listdir(MODELS_DIR) if os.path.isdir(os.path.join(MODELS_DIR, d))]
    return jsonify({"models": models})

@app.route('/api/train', methods=['POST'])
def start_training():
    global training_process
    data = request.json
    
    if training_process and training_process.poll() is None:
        return jsonify({"error": "A training process is already running."}), 400

    # Map web form to LlamaForge CLI arguments
    model_name = data.get('model')
    epochs = data.get('epochs', 3)
    lr = data.get('lr', '2e-4')

    # CMD construction (Adjust main.py to your repository's entry point)
    cmd = [
        "python3", "main.py", 
        "--model", model_name,
        "--epochs", str(epochs),
        "--learning_rate", lr,
        "--output_dir", os.path.join(MODELS_DIR, f"{model_name}-forged")
    ]

    try:
        training_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={**os.environ, "PYTORCH_ENABLE_MPS_FALLBACK": "1"}
        )
        
        thread = threading.Thread(target=stream_logs, args=(training_process,))
        thread.start()
        
        return jsonify({"status": "Training started", "pid": training_process.pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_training():
    global training_process
    if training_process and training_process.poll() is None:
        training_process.terminate()
        return jsonify({"status": "Process terminated"})
    return jsonify({"error": "No process running"}), 400

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)

