import os
import uuid
import chess
from flask import current_app
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

from app.recognition.piece_detector import PieceDetector
from app.recognition.fen_generator import FenGenerator
from app.services.chess_service import ChessService

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PhotoService:

    @staticmethod
    def recognize_board(image_file):

        if not _allowed_file(image_file.filename):
            return {'error': 'Допустимые форматы: jpg, png, heic'}, 400

        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(upload_folder, filename)

            img = Image.open(image_file)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            img.save(filepath, "JPEG", quality=90)

            pieces_grid = PieceDetector.detect(filepath)
            fen = FenGenerator.generate(pieces_grid)

            return {
                'fen': fen,
                'image_path': filename,
                'message': 'Позиция распознана',
            }, 200

        except Exception as e:
            return {'error': f'Ошибка обработки: {str(e)}'}, 500

    @staticmethod
    def correct_position(data):
        fen = data.get('fen')
        if not fen:
            return {'error': 'FEN не указан'}, 400

        corrections = data.get('corrections', [])
        turn = data.get('turn', 'w')

        try:
            board = chess.Board(fen)
            piece_symbols = 'KQRBNPkqrbnp'
            
            for corr in corrections:
                sq_name = corr.get('square')
                p_char = corr.get('piece')
                sq = chess.parse_square(sq_name)

                if p_char is None or p_char == "":
                    board.remove_piece_at(sq)
                elif p_char in piece_symbols:
                    board.set_piece_at(sq, chess.Piece.from_symbol(p_char))

            board.turn = chess.WHITE if turn == 'w' else chess.BLACK
            new_fen = board.fen()

            return {
                'fen': new_fen,
                'valid': FenGenerator.validate(new_fen),
            }, 200
        except Exception as e:
            return {'error': f'Ошибка коррекции: {str(e)}'}, 500

    @staticmethod
    def analyze_confirmed_position(data):
        fen = data.get('fen')
        if not fen:
            return {'error': 'FEN не указан'}, 400

        try:
            evaluation = ChessService.evaluate_position(fen)
            best_move = ChessService.get_best_move(fen)
            
            explanation = 'Позиция равна.'
            if evaluation:
                if evaluation > 1.0: explanation = 'Преимущество белых.'
                elif evaluation < -1.0: explanation = 'Преимущество черных.'

            return {
                'fen': fen,
                'evaluation': evaluation,
                'best_move': best_move,
                'explanation': explanation,
                'legal_moves': ChessService.get_legal_moves(fen)
            }, 200
        except Exception as e:
            return {'error': f'Ошибка анализа: {str(e)}'}, 500