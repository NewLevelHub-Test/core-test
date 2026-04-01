set -e

echo "--- Запуск деплоя проекта ChessApp ---"

cd ~/core-test-1

git pull origin main

source venv/bin/activate

pip install -r backend/requirements.txt

export FLASK_APP=backend/run.py
flask db upgrade

sudo systemctl restart chess_backend
sudo systemctl restart nginx

echo "--- Деплой успешно завершен! ---"