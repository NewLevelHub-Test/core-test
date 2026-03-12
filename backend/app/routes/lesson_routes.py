from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.lesson_service import LessonService

lesson_bp = Blueprint('lessons', __name__)


@lesson_bp.route('/topics', methods=['GET'])
@jwt_required()
def get_topics():
    result, status = LessonService.get_topics()
    return jsonify(result), status


@lesson_bp.route('/', methods=['GET'])
@jwt_required()
def get_lessons():
    topic_id = request.args.get('topic_id', type=int)
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
def check_exercise(lesson_id, exercise_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status = LessonService.check_exercise(user_id, exercise_id, data.get('move'))
    return jsonify(result), status


@lesson_bp.route('/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
def complete_lesson(lesson_id):
    user_id = get_jwt_identity()
    result, status = LessonService.complete_lesson(user_id, lesson_id)
    return jsonify(result), status
