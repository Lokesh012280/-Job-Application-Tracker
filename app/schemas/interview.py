from datetime import date, time, datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from app.models.interview import InterviewResult

class InterviewCreate(BaseModel):
    round: str = Field(min_length=1, max_length=120)
    interview_date: date
    interview_time: time | None = None
    interview_type: str = Field(default="Online", min_length=1, max_length=60)
    interviewer: str | None = Field(default=None, max_length=160)
    meeting_link: HttpUrl | None = None

class InterviewUpdate(BaseModel):
    round: str | None = Field(default=None, min_length=1, max_length=120)
    interview_date: date | None = None
    interview_time: time | None = None
    interview_type: str | None = None
    interviewer: str | None = None
    meeting_link: HttpUrl | None = None
    feedback: str | None = None
    result: InterviewResult | None = None

class InterviewOut(BaseModel):
    id: int
    application_id: int
    round: str
    interview_date: date
    interview_time: time | None
    interview_type: str
    interviewer: str | None
    meeting_link: str | None
    feedback: str | None
    result: InterviewResult
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
