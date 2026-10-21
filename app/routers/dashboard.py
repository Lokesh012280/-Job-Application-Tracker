from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview
from app.models.followup import FollowUp
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    counts = {s.value.lower(): 0 for s in ApplicationStatus}
    rows = db.query(Application.status, func.count(Application.id)).filter(Application.user_id == user.id).group_by(Application.status).all()
    for status_value, count in rows: counts[status_value.value.lower()] = count
    total = sum(counts.values())
    interview_count = db.query(func.count(Interview.id)).join(Application).filter(Application.user_id == user.id).scalar() or 0
    offers = counts["offer"] + counts["accepted"]
    return {
        "total_applications": total,
        "saved": counts["saved"], "applied": counts["applied"], "screening": counts["screening"],
        "interviews": counts["interview"], "offers": counts["offer"], "accepted": counts["accepted"],
        "rejected": counts["rejected"], "withdrawn": counts["withdrawn"],
        "interview_rounds": interview_count,
        "interview_rate_percent": round((counts["interview"] + interview_count) / total * 100, 2) if total else 0,
        "offer_rate_percent": round(offers / total * 100, 2) if total else 0,
    }

@router.get("/companies")
def company_statistics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(
        Application.company_name,
        func.count(Application.id).label("applications"),
        func.sum(case((Application.status == ApplicationStatus.INTERVIEW, 1), else_=0)).label("interviews"),
        func.sum(case((Application.status.in_([ApplicationStatus.OFFER, ApplicationStatus.ACCEPTED]), 1), else_=0)).label("offers")
    ).filter(Application.user_id == user.id).group_by(Application.company_name).order_by(func.count(Application.id).desc()).all()
    return [{"company": r.company_name, "applications": r.applications, "interviews": int(r.interviews or 0), "offers": int(r.offers or 0)} for r in rows]

@router.get("/upcoming-followups")
def upcoming_followups(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(FollowUp, Application).join(Application, FollowUp.application_id == Application.id).filter(
        Application.user_id == user.id, FollowUp.is_completed.is_(False), FollowUp.follow_up_date >= date.today()
    ).order_by(FollowUp.follow_up_date.asc()).limit(20).all()
    return [{"id": f.id, "application_id": a.id, "company_name": a.company_name, "job_title": a.job_title,
             "follow_up_date": f.follow_up_date, "note": f.note} for f, a in rows]

@router.get("/upcoming-interviews")
def upcoming_interviews(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Interview, Application).join(Application, Interview.application_id == Application.id).filter(
        Application.user_id == user.id, Interview.interview_date >= date.today()
    ).order_by(Interview.interview_date.asc()).limit(20).all()
    return [{"id": i.id, "application_id": a.id, "company_name": a.company_name, "job_title": a.job_title,
             "round": i.round, "interview_date": i.interview_date, "interview_time": i.interview_time,
             "interview_type": i.interview_type} for i, a in rows]
