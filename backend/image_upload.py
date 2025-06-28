import os
import base64
from werkzeug.utils import secure_filename
from models import ImageUploadRequestPayload, ImageUploadResponsePayload

TEMP_IMAGE_DIR = 'backend/temp/images'
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def handle_image_upload(filename: str, image_data: str) -> ImageUploadResponsePayload:
    try:
        if not filename or not image_data:
            return ImageUploadResponsePayload(status="error", message="文件名或图片数据缺失")

        # 解码Base64图片数据
        # image_data 应该是 "data:image/png;base64,..." 这样的格式
        # 我们需要提取出 base64 编码的部分
        if "," in image_data:
            header, encoded_data = image_data.split(",", 1)
        else:
            encoded_data = image_data

        decoded_image = base64.b64decode(encoded_data)

        secured_filename = secure_filename(filename)
        file_path = os.path.join(TEMP_IMAGE_DIR, secured_filename)
        
        with open(file_path, 'wb') as f:
            f.write(decoded_image)
        
        return ImageUploadResponsePayload(
            status="success",
            message="图片上传成功",
            image_path=f"/temp/images/{secured_filename}"
        )
    except Exception as e:
        return ImageUploadResponsePayload(status="error", message=f"图片上传失败: {str(e)}")