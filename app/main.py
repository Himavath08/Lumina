from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session, select
import qrcode
import uuid
import os

from app.database import init_db, engine
from app.models import User
from app.auth import create_user, authenticate_user
from app.trust_engine import calculate_trust_level
from app.security import create_token, verify_token
from app.phishing import analyze_url
from app.keys import generate_keys
from app.analytics import report_failure, get_noisy_metrics
from urllib.parse import urlparse
from app.analytics import report_phishing, get_noisy_phishing
from fastapi import Header

# =========================
# Create FastAPI App FIRST
# =========================
app = FastAPI()


# =========================
# Enable CORS (for extension)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Startup Event
# =========================
@app.on_event("startup")
def on_startup():
    generate_keys()   # Create RSA keys if not exists
    init_db()         # Initialize database


# =========================
# Request Models
# =========================
class URLRequest(BaseModel):
    url: str


class TokenRequest(BaseModel):
    token: str


# =========================
# Root
# =========================
@app.get("/")
def root():
    return {"message": "Lumina Trust Core Running"}


# =========================
# Register
# =========================
@app.post("/register")
def register(username: str, email: str, password: str):
    user = create_user(username, email, password)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }


# =========================
# Login (Returns RS256 Token)
# =========================
@app.post("/login")
def login(email: str, password: str):
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Assign role
    role = "admin" if user.email == "admin@gmail.com" else "student"

    token = create_token({
        "student_id": user.id,
        "trust_level": calculate_trust_level(user.badge_score),
        "role": role
    })

    return {
        "message": "Login successful",
        "access_token": token
    }
# =========================
# Verify Token
# =========================
@app.post("/verify-token")
def verify(request: TokenRequest):
    return verify_token(request.token)


# =========================
# Generate QR Code from Token
# =========================
@app.post("/generate-qr")
def generate_qr(request: TokenRequest):
    token = request.token

    # Create unique file name
    filename = f"{uuid.uuid4()}.png"
    path = os.path.join("app", filename)

    # Generate QR
    img = qrcode.make(token)
    img.save(path)

    return FileResponse(path, media_type="image/png", filename="lumina_qr.png")


# =========================
# Club Verification Endpoint
# =========================
@app.post("/verify-student")
def verify_student(request: TokenRequest):
    return verify_token(request.token)


# =========================
# Analyze URL (Phishing)
# =========================
@app.post("/analyze-url")
def analyze(request: URLRequest):
    result = analyze_url(request.url)

    domain = urlparse(request.url).netloc
    is_suspicious = result["status"] == "Suspicious"

    report_phishing(domain, is_suspicious)

    return result

# =========================
# Optional: View Users (Debug Only)
# =========================
@app.get("/users")
def get_users():
    with Session(engine) as session:
        statement = select(User)
        users = session.exec(statement).all()
        return users
class LabReportRequest(BaseModel):
    simulation_id: str
    step_number: int


@app.post("/report-lab-step")
def report_lab_step(request: LabReportRequest):
    return report_failure(request.simulation_id, request.step_number)


@app.get("/admin/analytics")
def admin_analytics(authorization: str = Header(...)):
    # Extract token from header
    token = authorization.replace("Bearer ", "")

    # Verify signature
    payload = verify_token(token)

    # Check role
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return {
        "lab_metrics": get_noisy_metrics(),
        "phishing_metrics": get_noisy_phishing()
    }