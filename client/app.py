from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import clientResnet
import time
import logging


app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', title="Early Exit Demo")

@app.route('/upload', methods=['POST'])
def upload_files():
    start_time = time.time()
    
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the directory exists
        file.save(filepath)
        
        try:
            # Process the image using clientResnet.py
            result = clientResnet.process_image(filepath)
        except Exception as e:
            # Ensure file is deleted in case of an exception
            logger.error(f"Error processing image: {e}")

            os.remove(filepath)
            return jsonify({'error': str(e)}), 500
        
        # Delete the file after processing
        os.remove(filepath)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return jsonify({'result': result, 'processing_time': processing_time})
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
