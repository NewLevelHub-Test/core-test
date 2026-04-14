import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "5000"))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host='0.0.0.0', port=port, threaded=False)