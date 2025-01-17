from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/adminupload')
def adminUploadPage():
    return render_template('admin_upload.html')

# Folder to save uploads
UPLOAD_FOLDER = './prototypev3/uploads' # change this after completion
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video_file' not in request.files or 'product_name' not in request.form:
        return jsonify({"error": "Missing file or product name"}), 400

    video_file = request.files['video_file']
    product_name = request.form['product_name']

    # Save video file
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(video_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video_file.save(file_path)

    # Simulate database update
    # Here, you can replace this part with your actual database logic
    print(f"Product Name: {product_name}")
    print(f"Video saved at: {file_path}")

    return jsonify({"message": "File uploaded successfully", "product_name": product_name}), 200

if __name__ == '__main__':
    app.run()
