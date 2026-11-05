from flask import request, session
from flask_restful import Resource, abort

from config import app, db, api
from models import User, Note
from schemas import user_schema, note_schema, notes_schema


# Every route except these needs a logged-in user
@app.before_request
def check_if_logged_in():
    open_routes = ["signup", "login", "check_session"]

    if request.endpoint not in open_routes and not session.get("user_id"):
        return {"errors": ["Unauthorized. Please log in."]}, 401


def find_note(id):
    note = db.session.get(Note, id)

    if not note:
        abort(404, errors=["Note not found."])
    if note.user_id != session["user_id"]:
        abort(403, errors=["You can only access your own notes."])

    return note


class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"errors": ["Username and password are required."]}, 422

        if password != data.get("password_confirmation"):
            return {"errors": ["Passwords do not match."]}, 422

        if User.query.filter_by(username=username).first():
            return {"errors": ["Username is already taken."]}, 422

        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        return user_schema.dump(user), 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if user and password and user.authenticate(password):
            session["user_id"] = user.id
            return user_schema.dump(user), 200

        return {"errors": ["Invalid username or password."]}, 401


class CheckSession(Resource):
    def get(self):
        user = User.query.filter_by(id=session.get("user_id")).first()

        if user:
            return user_schema.dump(user), 200

        return {}, 401


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


class Notes(Resource):
    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        query = Note.query.filter_by(user_id=session["user_id"]).order_by(Note.id.desc())
        pagination = query.paginate(page=page, per_page=per_page, max_per_page=50, error_out=False)

        return {
            "notes": notes_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        }, 200

    def post(self):
        data = request.get_json()

        try:
            note = Note(title=data.get("title"), content=data.get("content"), user_id=session["user_id"])
        except ValueError as e:
            return {"errors": [str(e)]}, 422

        db.session.add(note)
        db.session.commit()
        return note_schema.dump(note), 201


class NoteById(Resource):
    def get(self, id):
        note = find_note(id)
        return note_schema.dump(note), 200

    def patch(self, id):
        note = find_note(id)
        data = request.get_json()

        try:
            if "title" in data:
                note.title = data["title"]
            if "content" in data:
                note.content = data["content"]
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

        db.session.commit()
        return note_schema.dump(note), 200

    def delete(self, id):
        note = find_note(id)
        db.session.delete(note)
        db.session.commit()
        return {}, 204


api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(Notes, "/notes", endpoint="notes")
api.add_resource(NoteById, "/notes/<int:id>", endpoint="note_by_id")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
