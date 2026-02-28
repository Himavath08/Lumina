import bcrypt
from sqlmodel import Session, select
from app.models import User
from app.database import engine


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_user(username: str, email: str, password: str):
    with Session(engine) as session:
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            badge_score=0
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def authenticate_user(email: str, password: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user