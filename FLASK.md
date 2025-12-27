# LlamaForge Web Interface (Flask)
This version of LlamaForge provides a graphical dashboard for managing your LLM workflows.

##Features
Model Management: View and select local models.
Training Dashboard: Configure hyperparameters via a web form.
Real-time Logs: Stream console output to the browser using SocketIO.
Chat Interface: Test your forged models immediately.

##Installation (MacOS/Linux)
Create a Virtual Environment:
python3 -m venv venv
source venv/bin/activate


## Install Dependencies:
pip install -r requirements.txt


## Run the Server:
python app.py


Access the Dashboard: Open http://127.0.0.1:5000 in your browser.
## MacOS Note
If you are on Apple Silicon (M1/M2/M3), the application automatically attempts to use the Metal Performance Shaders (MPS) backend for acceleration.
