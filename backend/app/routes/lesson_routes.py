from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.lesson_service import LessonService
from app import limiter

lesson_bp = Blueprint('lessons', __name__)

@lesson_bp.route('/topics', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_topics():
    result, status = LessonService.get_topics()
    return jsonify(result), status

@lesson_bp.route('/', methods=['GET'])
@jwt_required()
def get_lessons():
    topic_id = request.args.get('topic_id', type=int)
    if topic_id is not None and topic_id < 0:
        return jsonify({'error': 'Некорректный ID темы'}), 400
        
    result, status = LessonService.get_lessons(topic_id)
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
    move = data.get('move')
    
    if not move or not isinstance(move, str):
        return jsonify({'error': 'Ход должен быть строкой'}), 400
        
    result, status = LessonService.check_exercise(user_id, exercise_id, move)
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