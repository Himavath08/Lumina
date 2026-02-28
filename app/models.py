from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    badge_score: int = 0
class LabMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    simulation_id: str
    step_number: int
    fail_count: int = 0
class PhishingMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    domain: str
    suspicious_count: int = 0
    safe_count: int = 0