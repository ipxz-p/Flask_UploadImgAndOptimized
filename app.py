from flask import Flask, request, render_template, redirect
import pyrebase
import uuid
import mimetypes
from PIL import Image
import io

app = Flask(__name__)

firebase_config = {
    "apiKey": "AIzaSyBUz9CPPOSdb3hVeCiQy52YN0W-rqZeT3s",
    "authDomain": "sopuplaodimage.firebaseapp.com",
    "projectId": "sopuplaodimage",
    "storageBucket": "sopuplaodimage.appspot.com",
    "messagingSenderId": "648645348024",
    "appId": "1:648645348024:web:5f4e32d254350297b2024d",
    "measurementId": "G-PK7QGS4KKD",
    "serviceAccount": "serviceAccount.json",
    "databaseURL": "https://sopuplaodimage-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file:
            # Determine the file type based on the extension
            file_extension = file.filename.split('.')[-1].lower()
            # Generate a unique filename for the file 
            # Generate a unique filename for the file
            filename = f"{str(uuid.uuid4())}.{file_extension}"
            # Determine the content type based on the file extension
            content_type, _ = mimetypes.guess_type(filename)
            # Check the file type and optimize accordingly
            if file_extension in ["png", "jpg", "jpeg"]:
                # Open and optimize images
                img = Image.open(file)
                img.thumbnail((800, 800))
                img = img.convert("RGB")
                # Save the optimized image as bytes
                optimized_image = io.BytesIO()
                img.save(optimized_image, "JPEG", optimize=True)
                # Upload the optimized image to Firebase Cloud Storage with the specified content type
                storage.child("uploads/" + filename).put(optimized_image.getvalue(), content_type=content_type)
            elif file_extension == "pdf":
                # Read PDF files as bytes and upload to Firebase Cloud Storage
                pdf_contents = file.read()
                storage.child("uploads/" + filename).put(pdf_contents, content_type=content_type)
            else:
                return "Unsupported file type."
            return "File uploaded and optimized successfully!"
    return "No file uploaded."

@app.route('/images/<image_filename>')
def get_image(image_filename):
    try:
        # Construct the URL of the image in Firebase Cloud Storage
        image_url = storage.child("uploads/" + image_filename).get_url(None)
        # Return a redirect response to the image URL
        return redirect(image_url)
    except Exception as e:
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=True)
