from config import app, api
from models import User, Note


if __name__ == "__main__":
    app.run(port=5555, debug=True)
