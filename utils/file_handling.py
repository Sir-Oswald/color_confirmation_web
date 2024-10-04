import os
import zipfile
from werkzeug.utils import secure_filename

def save_uploaded_files(files, upload_folder):
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def create_download_file(upload_folder):
    zip_file_path = os.path.join(upload_folder, 'color_confirmation_results.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                if file.endswith('_data.json'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, upload_folder)
                    zipf.write(file_path, arcname)
    return zip_file_path

def get_images_in_folder(folder_path):
    return [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]