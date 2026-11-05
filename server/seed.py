from faker import Faker
 
from config import app, db
from models import User, Note
 
fake = Faker()
 
 
def seed():
    print("Clearing old data...")
    Note.query.delete()
    User.query.delete()
 
    print("Creating user...")
    user = User(username="David")
    user.password_hash = "password123"
    db.session.add(user)
    db.session.commit()
 
    print("Creating notes...")
    notes = []
    for _ in range(15):
        notes.append(Note(
            title=fake.sentence(nb_words=4).rstrip("."),
            content=fake.paragraph(nb_sentences=4),
            user=user,
        ))
 
    db.session.add_all(notes)
    db.session.commit()
 
    print(f"Done! Created 1 user and {len(notes)} notes.")
    print("Log in with username 'David' and password 'password123'.")
 
 
if __name__ == "__main__":
    with app.app_context():
        seed()
 