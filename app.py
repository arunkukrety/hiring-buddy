"""Simple Web UI for GitHub Portia Resume Analysis System."""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, request, jsonify, Response, stream_template
from werkzeug.utils import secure_filename
import queue

# configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app = Flask(__name__)
app.secret_key = 'portia-ai-secret-key-2024'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# global variables for streaming
output_queue = queue.Queue()
chat_messages = []
input_queue = queue.Queue()
waiting_for_input = False
current_input_prompt = ""

# global function for web output (to avoid circular imports)
def global_add_output(message):
    """Global function to add output to queue."""
    output_queue.put(message)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def stream_output():
    """Generator for streaming output."""
    while True:
        try:
            message = output_queue.get(timeout=0.5)
            if message == "END":
                yield f"data: {json.dumps({'message': 'END'})}\n\n"
                break
            yield f"data: {json.dumps({'message': message})}\n\n"
        except queue.Empty:
            # reduce keepalive frequency
            yield f"data: {json.dumps({'keepalive': True})}\n\n"

def add_output(message):
    """Add message to output queue."""
    global_add_output(message)

def wait_for_input(prompt):
    """Wait for user input from web UI."""
    global waiting_for_input, current_input_prompt
    
    # clear any old input from queue
    while not input_queue.empty():
        try:
            input_queue.get_nowait()
        except queue.Empty:
            break
    
    waiting_for_input = True
    current_input_prompt = prompt
    add_output(f"🔔 WAITING FOR INPUT: {prompt}")
    
    # wait for input from web UI
    while waiting_for_input:
        try:
            user_input = input_queue.get(timeout=1.0)
            waiting_for_input = False
            current_input_prompt = ""
            
            # ensure we return a string
            if user_input is None:
                user_input = ""
            else:
                user_input = str(user_input).strip()
            
            # small delay to prevent race conditions
            import time
            time.sleep(0.1)
            
            return user_input
        except queue.Empty:
            continue
    
    # fallback if something goes wrong
    return ""

@app.route('/')
def index():
    """Main page with file upload."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    try:
        if 'resume' not in request.files or 'job_description' not in request.files:
            return jsonify({'error': 'Both resume and job description files are required'}), 400
        
        resume_file = request.files['resume']
        job_file = request.files['job_description']
        
        if resume_file.filename == '' or job_file.filename == '':
            return jsonify({'error': 'Please select both files'}), 400
        
        if not allowed_file(resume_file.filename) or not allowed_file(job_file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF, TXT, or DOCX files'}), 400
        
        # save files
        resume_filename = secure_filename(resume_file.filename)
        job_filename = secure_filename(job_file.filename)
        
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        job_path = os.path.join(app.config['UPLOAD_FOLDER'], job_filename)
        
        resume_file.save(resume_path)
        job_file.save(job_path)
        
        return jsonify({
            'success': True,
            'resume_path': resume_path,
            'job_path': job_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream')
def stream():
    """Stream output to client."""
    return Response(stream_output(), mimetype='text/event-stream')

@app.route('/start_analysis', methods=['POST'])
def start_analysis():
    """Start the analysis process."""
    try:
        data = request.get_json()
        resume_path = data.get('resume_path')
        job_path = data.get('job_path')
        
        if not resume_path or not job_path:
            return jsonify({'error': 'File paths not provided'}), 400
        
        # clear previous output
        while not output_queue.empty():
            output_queue.get()
        
        # start analysis in background thread
        def run_analysis():
            try:
                # create a simple analysis function
                from agents import PlannerAgent
                from portia import Portia, Config, LLMProvider, PortiaToolRegistry, LogLevel
                from dotenv import load_dotenv
                import os
                
                load_dotenv()
                
                # initialize portia
                config = Config.from_default(
                    llm_provider=LLMProvider.GOOGLE,
                    default_model="google/gemini-2.0-flash",
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    portia_api_key=os.getenv("PORTIA_API_KEY"),
                    default_log_level=LogLevel.ERROR  # Suppress INFO messages
                )
                portia = Portia(config, tools=PortiaToolRegistry(config))
                
                # create planner agent
                planner = PlannerAgent(portia)
                
                # redirect print to web output and replace input function
                import sys
                from io import StringIO
                
                class WebOutput:
                    def __init__(self):
                        self.buffer = StringIO()
                    
                    def write(self, text):
                        if text.strip():
                            add_output(text.rstrip())
                    
                    def flush(self):
                        pass
                
                # redirect stdout and replace input function
                original_stdout = sys.stdout
                original_input = __builtins__.input
                sys.stdout = WebOutput()
                
                # replace input function with web-based input
                def web_input(prompt=""):
                    result = wait_for_input(prompt)
                    return result
                
                __builtins__.input = web_input
                
                try:
                    # run the complete workflow (not just analysis)
                    add_output("Starting complete workflow...")
                    
                    # import the main workflow function
                    from main import main_workflow
                    result = main_workflow(resume_path, job_path)
                    
                    add_output("Complete workflow finished!")
                finally:
                    # restore stdout and input function
                    sys.stdout = original_stdout
                    __builtins__.input = original_input
                
                add_output("END")
            except Exception as e:
                add_output(f"ERROR: {str(e)}")
                add_output("END")
        
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and workflow input."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_type = data.get('user_type', 'user')
        
        if message:
            # if waiting for input, send to input queue
            if waiting_for_input:
                input_queue.put(message)
                # don't add system response - let the workflow handle it
            else:
                # regular chat message
                chat_messages.append({
                    'message': message,
                    'user_type': user_type,
                    'timestamp': datetime.now().isoformat()
                })
        
        return jsonify({
            'success': True, 
            'messages': chat_messages,
            'waiting_for_input': waiting_for_input,
            'current_prompt': current_input_prompt
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_messages')
def get_messages():
    """Get all chat messages and input status."""
    return jsonify({
        'messages': chat_messages,
        'waiting_for_input': waiting_for_input,
        'current_prompt': current_input_prompt
    })

@app.route('/status')
def status():
    """Get current status."""
    return jsonify({
        'waiting_for_input': waiting_for_input,
        'current_prompt': current_input_prompt,
        'output_queue_size': output_queue.qsize(),
        'input_queue_size': input_queue.qsize()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
