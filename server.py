from flask import Flask, request
import os

app = Flask(__name__)
UPLOAD_DIR = "uploads"

# Create the uploads directory if it doesn’t exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return "No file part in the request", 400
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        file.save(filepath)
        return "File uploaded successfully", 200
    except Exception as e:
        return f"Error uploading file: {str(e)}", 500

if __name__ == "__main__":
    print("Starting server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)