import os
import uuid
import subprocess

from flask import current_app
from werkzeug.utils import secure_filename

from app.recognition.board_detector import BoardDetector
from app.recognition.piece_detector import PieceDetector
from app.recognition.fen_generator import FenGenerator
from app.services.chess_service import ChessService
from app.models.topic import Topic


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _convert_heic(filepath):
    """Convert HEIC to JPG using sips (macOS) or ImageMagick."""
    jpg_path = filepath.rsplit('.', 1)[0] + '.jpg'
    try:
        subprocess.run(['sips', '-s', 'format', 'jpeg', filepath, '--out', jpg_path],
                       check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        from PIL import Image
        img = Image.open(filepath)
        img.save(jpg_path, 'JPEG')
    return jpg_path


class PhotoService:

    @staticmethod
    def recognize_board(image_file):
        if not _allowed_file(image_file.filename):
            return {'error': 'Допустимые форматы: jpg, png, heic'}, 400

        filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)

        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'heic':
            filepath = _convert_heic(filepath)

        try:
            board_img = BoardDetector.detect(filepath)
            pieces = PieceDetector.detect(board_img)
            fen = FenGenerator.generate(pieces)

            return {
                'fen': fen,
                'image_path': filename,
                'message': 'Проверьте позицию и при необходимости скорректируйте',
            }, 200
        except Exception as e:
            return {'error': f'Ошибка распознавания: {str(e)}'}, 500

    @staticmethod
    def correct_position(data):
        """
        Manual correction: add/remove/replace pieces, set turn.
        data = {
            "fen": "current_fen",
            "corrections": [
                {"square": "e4", "piece": "P"},   # set piece
                {"square": "d5", "piece": null},   # remove piece
            ],
            "turn": "w"  # or "b"
        }
        """
        fen = data.get('fen')
        if not fen:
            return {'error': 'FEN не указан'}, 400

        corrections = data.get('corrections', [])
        turn = data.get('turn')

        import chess
        board = chess.Board(fen)

        piece_map = {
            'K': chess.Piece(chess.KING, chess.WHITE),
            'Q': chess.Piece(chess.QUEEN, chess.WHITE),
            'R': chess.Piece(chess.ROOK, chess.WHITE),
            'B': chess.Piece(chess.BISHOP, chess.WHITE),
            'N': chess.Piece(chess.KNIGHT, chess.WHITE),
            'P': chess.Piece(chess.PAWN, chess.WHITE),
            'k': chess.Piece(chess.KING, chess.BLACK),
            'q': chess.Piece(chess.QUEEN, chess.BLACK),
            'r': chess.Piece(chess.ROOK, chess.BLACK),
            'b': chess.Piece(chess.BISHOP, chess.BLACK),
            'n': chess.Piece(chess.KNIGHT, chess.BLACK),
            'p': chess.Piece(chess.PAWN, chess.BLACK),
        }

        for corr in corrections:
            sq_name = corr.get('square')
            piece_char = corr.get('piece')

            sq = chess.parse_square(sq_name)

            if piece_char is None:
                board.remove_piece_at(sq)
            else:
                piece = piece_map.get(piece_char)
                if piece:
                    board.set_piece_at(sq, piece)

        if turn:
            board.turn = chess.WHITE if turn == 'w' else chess.BLACK

        new_fen = board.fen()
        valid = FenGenerator.validate(new_fen)

        return {
            'fen': new_fen,
            'valid': valid,
        }, 200

    @staticmethod
    def analyze_confirmed_position(data):
        fen = data.get('fen')
        if not fen:
            return {'error': 'FEN не указан'}, 400

        evaluation = ChessService.evaluate_position(fen)
        best_move = ChessService.get_best_move(fen)
        legal_moves = ChessService.get_legal_moves(fen)

        explanation = 'Позиция равна.'
        if evaluation is not None:
            if evaluation > 1.5:
                explanation = 'У белых значительное преимущество.'
            elif evaluation > 0.5:
                explanation = 'У белых небольшое преимущество.'
            elif evaluation < -1.5:
                explanation = 'У чёрных значительное преимущество.'
            elif evaluation < -0.5:
                explanation = 'У чёрных небольшое преимущество.'

        topic_recommendations = []
        if evaluation is not None and abs(evaluation) > 2:
            topics = Topic.query.filter(
                Topic.name.ilike('%тактик%') | Topic.name.ilike('%tactic%')
            ).all()
            topic_recommendations = [t.to_dict() for t in topics]

        return {
            'fen': fen,
            'evaluation': evaluation,
            'best_move': best_move,
            'explanation': explanation,
            'legal_moves': legal_moves,
            'recommended_topics': topic_recommendations,
        }, 200
