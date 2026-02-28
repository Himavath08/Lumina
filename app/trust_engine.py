from sqlmodel import Session
from app.database import engine
from app.models import User

TRUST_ACTION_POINTS = {
    "enable_mfa": 20,
    "secure_password": 15,
    "passed_phishing": 25,
    "encrypted_device": 20
}

def add_trust_points(user_id: int, action: str):
    if action not in TRUST_ACTION_POINTS:
        return None

    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None

        user.badge_score += TRUST_ACTION_POINTS[action]
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.badge_score

def calculate_trust_level(score: int):
    if score <= 30:
        return "Bronze"
    elif score <= 60:
        return "Silver"
    else:
        return "Gold"