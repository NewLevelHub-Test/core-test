import numpy as np
import os
from roboflow import Roboflow

class PieceDetector:
    API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")
    PROJECT_NAME = os.environ.get("ROBOFLOW_PROJECT", "ctv")
    VERSION = int(os.environ.get("ROBOFLOW_VERSION", "1"))

    @staticmethod
    def detect(image_path):
        if not PieceDetector.API_KEY:
            raise RuntimeError("ROBOFLOW_API_KEY is not configured")
        rf = Roboflow(api_key=PieceDetector.API_KEY)
        # Указываем воркспейс из твоей ссылки
        project = rf.workspace("chess-nypgo").project(PieceDetector.PROJECT_NAME)
        model = project.version(PieceDetector.VERSION).model
        
        result = model.predict(image_path, confidence=30).json()
        predictions = result.get('predictions', [])
        
        grid = [['.' for _ in range(8)] for _ in range(8)]
        if not predictions:
            return grid

        coords = np.array([[p['x'], p['y']] for p in predictions])
        x_min, y_min = coords.min(axis=0)
        x_max, y_max = coords.max(axis=0)
        
        width = x_max - x_min
        height = y_max - y_min

        predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)

        for p in predictions:
            rel_x = (p['x'] - x_min) / width if width > 0 else 0
            rel_y = (p['y'] - y_min) / height if height > 0 else 0

            col = int(rel_x * 7.99)
            row = int(rel_y * 7.99)
            
            if grid[row][col] == '.':
                grid[row][col] = PieceDetector._label_to_fen(p['class'])

        return grid

    @staticmethod
    def _label_to_fen(label):
        label = label.upper().strip()
        # Маппинг строго по твоим тегам: WKN/BKN для коней
        mapping = {
            'WK': 'K', 'WQ': 'Q', 'WR': 'R', 'WB': 'B', 'WKN': 'N', 'WP': 'P',
            'BK': 'k', 'BQ': 'q', 'BR': 'r', 'BB': 'b', 'BKN': 'n', 'BP': 'p'
        }
        return mapping.get(label, '.')