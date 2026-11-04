from random import randint

from faker import Faker

from config import app, db
from models import User, Note

fake = Faker()


def seed():
    print("Clearing old data...")
    Note.query.delete()
    User.query.delete()

    print("Creating users...")
    users = []
    for username in ["alice", "bob", "charlie"]:
        user = User(username=username)
        user.password_hash = "password123"
        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print("Creating notes...")
    notes = []
    for user in users:
        for _ in range(randint(8, 15)):
            notes.append(Note(
                title=fake.sentence(nb_words=4).rstrip("."),
                content=fake.paragraph(nb_sentences=4),
                user=user,
            ))

    db.session.add_all(notes)
    db.session.commit()

    print(f"Done! Created {len(users)} users and {len(notes)} notes.")
    print("Log in with username 'alice', 'bob' or 'charlie' and password 'password123'.")


if __name__ == "__main__":
    with app.app_context():
        seed()
