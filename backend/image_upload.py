import os
from werkzeug.utils import secure_filename
from flask import jsonify

TEMP_IMAGE_DIR = 'backend/temp/images'
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def handle_image_upload(request):
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "未上传文件"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "未选择文件"}), 400
        
    filename = secure_filename(file.filename)
    file_path = os.path.join(TEMP_IMAGE_DIR, filename)
    file.save(file_path)
    
    return jsonify({
        "status": "success",
        "image_url": f"/temp/images/{filename}"
    })