# Notes API

A Flask backend for a simple notes app. Users can sign up, log in and log out, and once logged in they can create, view, edit and delete their own notes. Other users can't see or change your notes.

Login is handled with Flask sessions and passwords are hashed with Flask-Bcrypt. The API works with the `client-with-sessions` React app in this repo.

## Installation

Make sure you have Python 3.8+ and pipenv installed.

```bash
pipenv install
pipenv shell
```

Then set up the database and add some sample data:

```bash
cd server
flask db upgrade
python seed.py
```

The seed file creates 3 users (`alice`, `bob` and `charlie`) with some notes each. They all use the password `password123`.

## Running the App

From the `server` folder:

```bash
python app.py
```

The API runs on http://localhost:5555.

To try it with the frontend, open another terminal and run:

```bash
cd client-with-sessions
npm install
npm start
```

## Running Tests

From the `server` folder:

```bash
pytest
```

## Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Creates a new user and logs them in. Needs `username`, `password` and `password_confirmation`. Returns 201, or 422 if something is missing, the passwords don't match or the username is taken. |
| POST | `/login` | Logs in a user. Needs `username` and `password`. Returns 200, or 401 if the details are wrong. |
| GET | `/check_session` | Returns the logged-in user so they stay logged in after a refresh. Returns 200, or 401 with `{}` if nobody is logged in. |
| DELETE | `/logout` | Logs the user out. Returns 204. |

Signup, login and check_session return the user like this:

```json
{ "id": 1, "username": "alice" }
```

### Notes

You must be logged in to use these routes, otherwise you get a 401. If you try to access a note that belongs to someone else you get a 403.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notes` | Returns your notes, 10 per page. Use `?page=2` to change page and `?per_page=5` to change how many you get (max 50). |
| POST | `/notes` | Creates a note. Needs `title` and `content`. Returns 201, or 422 if a field is missing. |
| GET | `/notes/<id>` | Returns one of your notes. |
| PATCH | `/notes/<id>` | Updates the `title` and/or `content` of a note. |
| DELETE | `/notes/<id>` | Deletes a note. Returns 204. |

Example response from `GET /notes?page=1&per_page=10`:

```json
{
  "notes": [
    {
      "id": 1,
      "title": "Groceries",
      "content": "Milk, eggs and bread",
      "created_at": "2026-11-04T09:19:47",
      "updated_at": "2026-11-04T09:19:47",
      "user_id": 1
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 12,
  "total_pages": 2
}
```

## Models

- **User**: `id`, `username` (unique), `_password_hash`. A user has many notes.
- **Note**: `id`, `title`, `content`, `created_at`, `updated_at`, `user_id`. A note belongs to a user.
