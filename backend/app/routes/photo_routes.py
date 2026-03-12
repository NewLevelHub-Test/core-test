from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.photo_service import PhotoService

photo_bp = Blueprint('photo', __name__)


@photo_bp.route('/recognize', methods=['POST'])
@jwt_required()
def recognize_board():
    if 'image' not in request.files:
        return jsonify({'error': 'Изображение не загружено'}), 400

    image = request.files['image']
    result, status = PhotoService.recognize_board(image)
    return jsonify(result), status


@photo_bp.route('/correct', methods=['POST'])
@jwt_required()
def correct_position():
    data = request.get_json()
    result, status = PhotoService.correct_position(data)
    return jsonify(result), status


@photo_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_confirmed():
    data = request.get_json()
    result, status = PhotoService.analyze_confirmed_position(data)
    return jsonify(result), status
