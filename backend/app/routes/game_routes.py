from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.game_service import GameService
from app import limiter

game_bp = Blueprint('games', __name__)

@game_bp.route('/', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute") 
def create_game():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    if not data:
        return jsonify({'error': 'Данные для создания игры не переданы'}), 400
        
    result, status = GameService.create_game(user_id, data)
    return jsonify(result), status

@game_bp.route('/<int:game_id>', methods=['GET'])
@jwt_required()
def get_game(game_id):
    result, status = GameService.get_game(game_id)
    return jsonify(result), status

@game_bp.route('/<int:game_id>/move', methods=['POST'])
@jwt_required()
@limiter.limit("120 per minute") 
def make_move(game_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    is_bot_move = data.get('is_bot_opening') is True or data.get('is_bot_move') is True
    move = data.get('move')

    if not is_bot_move:
        if not move or not isinstance(move, str) or len(move) < 4:
            return jsonify({'error': 'Некорректный формат хода'}), 400
        
    result, status = GameService.make_move(user_id, game_id, data)
    return jsonify(result), status

@game_bp.route('/<int:game_id>/resign', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def resign(game_id):
    user_id = get_jwt_identity()
    result, status = GameService.resign(user_id, game_id)
    return jsonify(result), status

@game_bp.route('/history', methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_history():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    
    if page < 1:
        page = 1
        
    result, status = GameService.get_user_games(user_id, page)
    return jsonify(result), status

@game_bp.route('/<int:game_id>/moves', methods=['GET'])
@jwt_required()
def get_moves(game_id):
    result, status = GameService.get_game_moves(game_id)
    return jsonify(result), status

@game_bp.route('/<int:game_id>/pgn', methods=['GET'])
@jwt_required()
@limiter.limit("5 per minute") 
def export_pgn(game_id):
    result, status = GameService.export_pgn(game_id)
    return jsonify(result), status