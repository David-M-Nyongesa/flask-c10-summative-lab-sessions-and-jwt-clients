# Notes API – Full Auth Flask Backend

A secure Flask REST API for a personal notes app. Users can sign up, log in, and manage their own notes. Authentication uses **Flask sessions**, passwords are hashed with **Flask-Bcrypt**, and every notes route is protected so users can only see and change their own notes.

This backend is built to work with the provided `client-with-sessions` React frontend.

## Tech Stack

- Flask, Flask-RESTful
- Flask-SQLAlchemy + Flask-Migrate (SQLite)
- Flask-Bcrypt (password hashing)
- Marshmallow (serialization)
- Faker (seed data)
- Pytest (tests)

## Project Structure

```
.
├── Pipfile
├── README.md
├── client-with-sessions/   # provided React frontend (sessions)
├── client-with-jwt/        # provided React frontend (JWT, not used)
└── server/
    ├── app.py              # routes / resources
    ├── config.py           # app, db, bcrypt, api and migrate setup
    ├── models.py           # User and Note models
    ├── schemas.py          # Marshmallow schemas
    ├── seed.py             # sample data
    ├── migrations/         # Flask-Migrate files
    ├── pytest.ini
    └── testing/            # pytest tests
```

## Installation

You need Python 3.8+ and `pipenv`.

1. Clone the repo and move into it:

   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. Install the dependencies and activate the virtual environment:

   ```bash
   pipenv install
   pipenv shell
   ```

3. Move into the server folder, create the database and seed it:

   ```bash
   cd server
   flask db upgrade
   python seed.py
   ```

   The seed creates three users — `alice`, `bob` and `charlie` — all with the password `password123`, plus some notes for each one.

## Running the App

From the `server` folder:

```bash
python app.py
```

or

```bash
flask run --port 5555
```

The API runs on `http://localhost:5555`.

To use the frontend, open a second terminal:

```bash
cd client-with-sessions
npm install
npm start
```

The frontend runs on `http://localhost:4000` and proxies API requests to port 5555.

## Running Tests

From the `server` folder:

```bash
pytest
```

Tests use an in-memory database, so your `app.db` is never touched.

## API Endpoints

All request and response bodies are JSON. Errors are returned as `{"errors": ["message"]}`.

### Auth

| Method | Endpoint         | Description                                                    | Success | Errors                                   |
|--------|------------------|----------------------------------------------------------------|---------|------------------------------------------|
| POST   | `/signup`        | Create a user and log them in                                  | 201     | 422 missing fields, mismatch, taken name |
| POST   | `/login`         | Log in an existing user                                        | 200     | 401 invalid username or password         |
| GET    | `/check_session` | Return the logged-in user (keeps users logged in on refresh)   | 200     | 401 returns `{}` when not logged in      |
| DELETE | `/logout`        | Log out the current user                                       | 204     | 401 not logged in                        |

**POST `/signup`** body:

```json
{ "username": "alice", "password": "password123", "password_confirmation": "password123" }
```

**POST `/login`** body:

```json
{ "username": "alice", "password": "password123" }
```

Signup, login and check_session respond with the user:

```json
{ "id": 1, "username": "alice" }
```

### Notes (login required)

Every notes route returns `401` if you are not logged in. Trying to view, edit or delete a note that belongs to another user returns `403`.

| Method | Endpoint      | Description                                  | Success | Errors             |
|--------|---------------|----------------------------------------------|---------|--------------------|
| GET    | `/notes`      | Get the current user's notes (paginated)     | 200     | 401                |
| POST   | `/notes`      | Create a note                                | 201     | 401, 422           |
| GET    | `/notes/<id>` | Get one of the current user's notes          | 200     | 401, 403, 404      |
| PATCH  | `/notes/<id>` | Update a note's `title` and/or `content`     | 200     | 401, 403, 404, 422 |
| DELETE | `/notes/<id>` | Delete a note                                | 204     | 401, 403, 404      |

**GET `/notes?page=1&per_page=10`**

- `page` – page number (default `1`)
- `per_page` – notes per page (default `10`, max `50`)

Response:

```json
{
  "notes": [
    {
      "id": 12,
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

**POST `/notes`** body (both fields required, title max 100 characters):

```json
{ "title": "Groceries", "content": "Milk, eggs and bread" }
```

**PATCH `/notes/<id>`** body (send only the fields you want to change):

```json
{ "title": "Shopping list" }
```

## Models

**User**

- `id`
- `username` – required and unique
- `_password_hash` – bcrypt hash (the plain password is never stored)
- has many `notes`

**Note**

- `id`
- `title` – required, max 100 characters
- `content` – required
- `created_at`, `updated_at`
- `user_id` – foreign key to `users.id`
