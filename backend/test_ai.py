from app.recognition.piece_detector import PieceDetector
import os

# Замени на путь к любой картинке шахмат у тебя на диске
IMAGE = r"C:\Users\Darya\Pictures\Screenshots\Снимок экрана 2026-03-25 201421.png"

if os.path.exists(IMAGE):
    print("Запрос к Roboflow...")
    grid = PieceDetector.detect(IMAGE)
    for row in grid:
        print(" ".join(row))
else:
    print(f"Файл {IMAGE} не найден. Положи картинку в папку uploads.")