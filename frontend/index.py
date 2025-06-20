# index.py - 엔트리 포인트 예시
from .app import app

if __name__ == "__main__":
    app.run_server(debug=True)
