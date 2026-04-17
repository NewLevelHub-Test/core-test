from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.lesson_service import LessonService
from app import limiter

lesson_bp = Blueprint('lessons', __name__)

@lesson_bp.route('/topics', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_topics():
    page = request.args.get('page', 1, type=int)
    result, status = LessonService.get_topics(page=page)
    return jsonify(result), status

@lesson_bp.route('/', methods=['GET'])
@jwt_required()
def get_lessons():
    topic_id = request.args.get('topic_id', type=int)
    page = request.args.get('page', 1, type=int)
    
    if topic_id is not None and topic_id < 0:
        return jsonify({'error': 'Некорректный ID темы'}), 400
        
    result, status = LessonService.get_lessons(topic_id=topic_id, page=page)
    return jsonify(result), status

@lesson_bp.route('/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson(lesson_id):
    result, status = LessonService.get_lesson_full(lesson_id)
    return jsonify(result), status

@lesson_bp.route('/<int:lesson_id>/exercises', methods=['GET'])
@jwt_required()
def get_exercises(lesson_id):
    result, status = LessonService.get_exercises(lesson_id)
    return jsonify(result), status

@lesson_bp.route('/<int:lesson_id>/exercises/<int:exercise_id>/check', methods=['POST'])
@jwt_required()
@limiter.limit("60 per minute")
def check_exercise(lesson_id, exercise_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    move = data.get('move', '')
    uci = data.get('uci', '')
    from_sq = data.get('from', '')
    to_sq = data.get('to', '')

    if not move and not uci and not (from_sq and to_sq):
        return jsonify({'error': 'Ход должен быть строкой'}), 400

    result, status = LessonService.check_exercise(
        user_id, exercise_id, move, uci=uci, from_sq=from_sq, to_sq=to_sq
    )
    return jsonify(result), status

@lesson_bp.route('/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def complete_lesson(lesson_id):
    user_id = get_jwt_identity()
    result, status = LessonService.complete_lesson(user_id, lesson_id)
    return jsonify(result), status

@lesson_bp.route('/topics/<int:topic_id>', methods=['GET'])
@jwt_required()
def get_topic_details(topic_id):
    user_id = get_jwt_identity()
    result, status = LessonService.get_topic_lessons(user_id, topic_id)
    return jsonify(result), status