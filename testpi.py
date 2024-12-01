from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from the Raspberry Pi!"

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file:
        file.save(f"./uploads/{file.filename}")
        return jsonify({"message": f"File {file.filename} uploaded successfully!"}), 200
    return jsonify({"error": "No file provided!"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
