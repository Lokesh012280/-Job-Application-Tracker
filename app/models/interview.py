from datetime import date, datetime, time, timezone
import enum
from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base

class InterviewResult(str, enum.Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"

def utcnow():
    return datetime.now(timezone.utc)

class Interview(Base):
    __tablename__ = "interviews"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    round: Mapped[str] = mapped_column(String(120), nullable=False)
    interview_date: Mapped[date] = mapped_column(Date, nullable=False)
    interview_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    interview_type: Mapped[str] = mapped_column(String(60), nullable=False, default="Online")
    interviewer: Mapped[str | None] = mapped_column(String(160), nullable=True)
    meeting_link: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[InterviewResult] = mapped_column(Enum(InterviewResult, name="interview_result"), nullable=False, default=InterviewResult.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    application = relationship("Application", back_populates="interviews")
