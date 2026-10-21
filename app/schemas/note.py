from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field

class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

class NoteOut(BaseModel):
    id: int
    application_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FollowUpCreate(BaseModel):
    follow_up_date: date
    note: str | None = Field(default=None, max_length=10000)

class FollowUpUpdate(BaseModel):
    follow_up_date: date | None = None
    note: str | None = None
    is_completed: bool | None = None

class FollowUpOut(BaseModel):
    id: int
    application_id: int
    follow_up_date: date
    note: str | None
    is_completed: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
