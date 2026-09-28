from app import app
from database import models, db


def check_username(u):
    if models.User.query.filter_by(username=u).first():
        print("User with this username already exists.")
        return False
    return True


def check_password(p1, p2):
    if p1 != p2:
        print("Passwords do not match.")
        return False
    return True


def create_user(u, p):
    user = models.User(username=u)
    user.set_password(p)
    db.db.session.add(user)
    db.db.session.commit()
    return user


def main():
    with app.app_context():
        print("Creating new user\n------------------------")
        username = input("Username: ")
        if not check_username(username):
            return
        password1 = input("Password: ")
        password2 = input("Confirm Password: ")
        if not check_password(password1, password2):
            return

        user = create_user(username, password1)
        print(f"User created successfully.\nusername: {user.username}, password: {password1}")


if __name__ == "__main__":
    main()
