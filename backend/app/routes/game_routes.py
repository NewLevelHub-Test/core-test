from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.game_service import GameService

game_bp = Blueprint('games', __name__)


@game_bp.route('/', methods=['POST'])
@jwt_required()
def create_game():
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status = GameService.create_game(user_id, data)
    return jsonify(result), status


@game_bp.route('/<int:game_id>', methods=['GET'])
@jwt_required()
def get_game(game_id):
    result, status = GameService.get_game(game_id)
    return jsonify(result), status


@game_bp.route('/<int:game_id>/move', methods=['POST'])
@jwt_required()
def make_move(game_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status = GameService.make_move(user_id, game_id, data)
    return jsonify(result), status


@game_bp.route('/<int:game_id>/resign', methods=['POST'])
@jwt_required()
def resign(game_id):
    user_id = get_jwt_identity()
    result, status = GameService.resign(user_id, game_id)
    return jsonify(result), status


@game_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    result, status = GameService.get_user_games(user_id, page)
    return jsonify(result), status


@game_bp.route('/<int:game_id>/moves', methods=['GET'])
@jwt_required()
def get_moves(game_id):
    result, status = GameService.get_game_moves(game_id)
    return jsonify(result), status


@game_bp.route('/<int:game_id>/pgn', methods=['GET'])
@jwt_required()
def export_pgn(game_id):
    result, status = GameService.export_pgn(game_id)
    return jsonify(result), status
