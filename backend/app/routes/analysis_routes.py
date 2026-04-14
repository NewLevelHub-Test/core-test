from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.analysis_service import AnalysisService
from app import limiter

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/game/<int:game_id>', methods=['GET'])
@jwt_required()
@limiter.limit("10 per minute") 
def analyze_game(game_id):
    user_id = get_jwt_identity()
    result, status = AnalysisService.analyze_game(user_id, game_id)
    return jsonify(result), status

@analysis_bp.route('/position', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute") 
def analyze_position():
    data = request.get_json() or {}
    fen = data.get('fen')
    
    if not fen or not isinstance(fen, str) or len(fen) < 15:
        return jsonify({'error': 'Некорректная FEN-строка'}), 400
        
    result, status = AnalysisService.analyze_position(fen)
    return jsonify(result), status

@analysis_bp.route('/mistakes', methods=['GET'])
@jwt_required()
def get_mistakes():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    
    result, status = AnalysisService.get_user_mistakes(user_id, page=page)
    return jsonify(result), status

@analysis_bp.route('/mistakes/<int:mistake_id>/exercises', methods=['GET'])
@jwt_required()
def get_mistake_exercises(mistake_id):
    user_id = get_jwt_identity()
    result, status = AnalysisService.get_exercises_for_mistake(user_id, mistake_id)
    return jsonify(result), status

@analysis_bp.route('/pgn', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def analyze_pgn():
    data = request.get_json() or {}
    pgn_text = data.get('pgn')
    result, status = AnalysisService.analyze_pgn_text(pgn_text)
    return jsonify(result), status

@analysis_bp.route('/pgn-photo', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def analyze_pgn_photo():
    if 'image' not in request.files:
        return jsonify({'error': 'Ключ "image" не найден в FormData'}), 400
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    extracted, status = AnalysisService.extract_pgn_from_handwritten_image(image)
    if status != 200:
        return jsonify(extracted), status

    analyzed, a_status = AnalysisService.analyze_pgn_text(extracted.get('pgn'))
    return jsonify({
        'extracted_pgn': extracted.get('pgn'),
        **analyzed
    }), a_status