from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.photo_service import PhotoService
from app import limiter

photo_bp = Blueprint('photo', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@photo_bp.route('/recognize', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def recognize_board():
    if 'image' not in request.files:
        return jsonify({'error': 'Изображение не загружено'}), 400

    image = request.files['image']

    if image.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    if not allowed_file(image.filename):
        return jsonify({'error': 'Разрешены только форматы JPG и PNG'}), 400
        
    result, status = PhotoService.recognize_board(image)
    return jsonify(result), status

@photo_bp.route('/correct', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def correct_position():
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Данные отсутствуют'}), 400
        
    result, status = PhotoService.correct_position(data)
    return jsonify(result), status

@photo_bp.route('/analyze', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def analyze_confirmed():
    data = request.get_json() or {}
    fen = data.get('fen')
    
    if not fen or not isinstance(fen, str) or len(fen) < 15:
        return jsonify({'error': 'Некорректная позиция'}), 400
        
    result, status = PhotoService.analyze_confirmed_position(data)
    return jsonify(result), status