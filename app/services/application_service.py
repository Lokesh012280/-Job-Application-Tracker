from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationStatus

ALLOWED_TRANSITIONS = {
    ApplicationStatus.SAVED: {ApplicationStatus.APPLIED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.APPLIED: {ApplicationStatus.SCREENING, ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.SCREENING: {ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.INTERVIEW: {ApplicationStatus.OFFER, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.OFFER: {ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.ACCEPTED: set(),
    ApplicationStatus.REJECTED: set(),
    ApplicationStatus.WITHDRAWN: set(),
}

def owned_application(db: Session, application_id: int, user_id: int) -> Application:
    item = db.query(Application).filter(Application.id == application_id, Application.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    return item

def change_status(item: Application, new_status: ApplicationStatus):
    if item.status == new_status:
        return
    if new_status not in ALLOWED_TRANSITIONS[item.status]:
        raise HTTPException(status_code=400, detail=f"Invalid status transition: {item.status.value} -> {new_status.value}")
    item.status = new_status
