import os
from app.main import create_app


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))


if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=True, use_reloader=False)
