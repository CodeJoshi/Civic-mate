from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

class Language(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
    TAMIL = "Tamil"
    TELUGU = "Telugu"
    MARATHI = "Marathi"

class UserProfile(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=100)
    annual_income: float = Field(gt=0, allow_inf_nan=False)
    state: str = Field(min_length=2, max_length=80)
    category: str = Field(default="General", pattern="^(General|OBC|SC|ST)$")
    preferred_language: Language = Language.TAMIL

class SchemeSummary(BaseModel):
    scheme_name: str
    eligibility_bullets: list[str] = Field(min_length=1, max_length=3)
    income_cap: float | None = None
    eligible: bool
    notes: list[str] = Field(default_factory=list)

class AgentStep(BaseModel):
    step_number: int
    action: str
    selector_used: str | None = None
    status: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ExecutionSession(BaseModel):
    session_id: str
    user_profile: UserProfile
    scheme_name: str
    status: str
    trace_log: list[AgentStep] = Field(default_factory=list)
    screenshot_path: str | None = None
    submitted: bool = False
    receipt_reference: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AnalyzeRequest(BaseModel):
    profile: UserProfile
    scheme_id: str
    policy_text: str | None = None

class ExecuteRequest(BaseModel):
    profile: UserProfile
    scheme_name: str
    eligible: bool
