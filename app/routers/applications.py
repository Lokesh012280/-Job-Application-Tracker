from datetime import date
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.application import Application, ApplicationStatus
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationOut, StatusUpdate, PaginatedApplications
from app.services.application_service import owned_application, change_status
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump()
    if data.get("job_url") is not None:
        data["job_url"] = str(data["job_url"])
    item = Application(**data, user_id=user.id)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("", response_model=PaginatedApplications)
def list_applications(
    company: str | None = None, job_title: str | None = None,
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    location: str | None = None, source: str | None = None,
    from_date: date | None = None, to_date: date | None = None,
    sort: str = Query(default="applied_date", pattern="^(applied_date|company|salary|status|created_at)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1), limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    q = db.query(Application).filter(Application.user_id == user.id)
    if company: q = q.filter(Application.company_name.ilike(f"%{company}%"))
    if job_title: q = q.filter(Application.job_title.ilike(f"%{job_title}%"))
    if status_filter: q = q.filter(Application.status == status_filter)
    if location: q = q.filter(Application.location.ilike(f"%{location}%"))
    if source: q = q.filter(Application.source.ilike(f"%{source}%"))
    if from_date: q = q.filter(Application.applied_date >= from_date)
    if to_date: q = q.filter(Application.applied_date <= to_date)
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be on or before to_date")
    total = q.with_entities(func.count(Application.id)).scalar() or 0
    sort_columns = {"applied_date": Application.applied_date, "company": Application.company_name, "salary": Application.salary_min, "status": Application.status, "created_at": Application.created_at}
    q = q.order_by((asc if order == "asc" else desc)(sort_columns[sort]))
    items = q.offset((page - 1) * limit).limit(limit).all()
    return {"page": page, "limit": limit, "total": total, "total_pages": ceil(total / limit) if total else 0, "data": items}

@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return owned_application(db, application_id, user.id)

@router.put("/{application_id}", response_model=ApplicationOut)
def update_application(application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_application(db, application_id, user.id)
    updates = payload.model_dump(exclude_unset=True)
    for field in ("salary_min", "salary_max"):
        if field in updates and updates[field] is not None and updates[field] < 0:
            raise HTTPException(status_code=422, detail=f"{field} cannot be negative")
    minimum = updates.get("salary_min", item.salary_min)
    maximum = updates.get("salary_max", item.salary_max)
    if minimum is not None and maximum is not None and maximum < minimum:
        raise HTTPException(status_code=422, detail="salary_max must be greater than or equal to salary_min")
    if updates.get("applied_date") and updates["applied_date"] > date.today():
        raise HTTPException(status_code=422, detail="applied_date cannot be in the future")
    if "job_url" in updates and updates["job_url"] is not None:
        updates["job_url"] = str(updates["job_url"])
    if "status" in updates and updates["status"] is not None:
        change_status(item, updates.pop("status"))
    for key, value in updates.items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item

@router.patch("/{application_id}/status", response_model=ApplicationOut)
def update_status(application_id: int, payload: StatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_application(db, application_id, user.id)
    change_status(item, payload.status)
    db.commit(); db.refresh(item)
    return item

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_application(db, application_id, user.id)
    db.delete(item); db.commit()
    return None
