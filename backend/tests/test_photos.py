import io
import os
import pytest
import uuid
from PIL import Image
from pillow_heif import register_heif_opener
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db

register_heif_opener()

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        unique_id = uuid.uuid4().hex[:8]
        user = User(
            username=f"testuser_{unique_id}", 
            email=f"test_{unique_id}@test.com",
            phone=f"707{unique_id}"
        )
        user.set_password("password123")
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        return {
            'Authorization': f'Bearer {access_token}',
        }

@pytest.mark.parametrize("extension, pillow_format", [
    ("heic", "HEIF"), 
    ("jpg", "JPEG"),
    ("png", "PNG")
])
def test_recognize_board_all_devices(client, auth_headers, app, extension, pillow_format):
    img = Image.new('RGB', (100, 100), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=pillow_format)
    img_byte_arr.seek(0)

    data = {
        'image': (img_byte_arr, f'test_photo.{extension}')
    }
    
    response = client.post(
        '/api/photo/recognize', 
        data=data, 
        content_type='multipart/form-data',
        headers=auth_headers
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert 'image_path' in json_data
    assert 'fen' in json_data
    
    assert json_data['image_path'].lower().endswith('.jpg')

    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    full_path = os.path.join(upload_folder, json_data['image_path'])
    if os.path.exists(full_path):
        os.remove(full_path)