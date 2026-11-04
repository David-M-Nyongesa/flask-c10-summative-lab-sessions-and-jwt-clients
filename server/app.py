from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, Note
from schemas import user_schema


@app.before_request
def check_if_logged_in():
    """Block every route except the public auth routes unless a user is logged in."""
    open_routes = ["signup", "login", "check_session"]

    if request.endpoint not in open_routes and not session.get("user_id"):
        return {"errors": ["Unauthorized. Please log in."]}, 401


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = data.get("password")
        password_confirmation = data.get("password_confirmation")

        errors = []
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")
        if password != password_confirmation:
            errors.append("Password and password confirmation do not match.")
        if username and User.query.filter_by(username=username).first():
            errors.append("Username is already taken.")

        if errors:
            return {"errors": errors}, 422

        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        return user_schema.dump(user), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password") or ""

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user_schema.dump(user), 200

        return {"errors": ["Invalid username or password."]}, 401


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None

        if user:
            return user_schema.dump(user), 200

        return {}, 401


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Logout, "/logout", endpoint="logout")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
