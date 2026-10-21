from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator
from app.models.application import ApplicationStatus

class ApplicationBase(BaseModel):
    company_name: str = Field(min_length=1, max_length=160)
    job_title: str = Field(min_length=1, max_length=160)
    location: str = Field(min_length=1, max_length=160)
    employment_type: str = Field(default="Full Time", min_length=1, max_length=60)
    source: str = Field(default="Other", min_length=1, max_length=100)
    job_url: HttpUrl | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    applied_date: date = Field(default_factory=date.today)
    status: ApplicationStatus = ApplicationStatus.SAVED
    description: str | None = None

    @model_validator(mode="after")
    def validate_salary_and_date(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_max < self.salary_min:
            raise ValueError("salary_max must be greater than or equal to salary_min")
        if self.applied_date > date.today():
            raise ValueError("applied_date cannot be in the future")
        return self

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=160)
    job_title: str | None = Field(default=None, min_length=1, max_length=160)
    location: str | None = Field(default=None, min_length=1, max_length=160)
    employment_type: str | None = Field(default=None, min_length=1, max_length=60)
    source: str | None = Field(default=None, min_length=1, max_length=100)
    job_url: HttpUrl | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    applied_date: date | None = None
    status: ApplicationStatus | None = None
    description: str | None = None

class StatusUpdate(BaseModel):
    status: ApplicationStatus

class ApplicationOut(BaseModel):
    id: int
    user_id: int
    company_name: str
    job_title: str
    location: str
    employment_type: str
    source: str
    job_url: str | None
    salary_min: int | None
    salary_max: int | None
    applied_date: date
    status: ApplicationStatus
    description: str | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaginatedApplications(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    data: list[ApplicationOut]
