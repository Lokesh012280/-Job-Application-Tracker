from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.interview import Interview
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewOut
from app.services.application_service import owned_application
from app.utils.dependencies import get_current_user

router = APIRouter(tags=["Interviews"])

@router.post("/applications/{application_id}/interviews", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
def create_interview(application_id: int, payload: InterviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_application(db, application_id, user.id)
    data = payload.model_dump()
    if data.get("meeting_link") is not None: data["meeting_link"] = str(data["meeting_link"])
    item = Interview(application_id=application_id, **data)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/applications/{application_id}/interviews", response_model=list[InterviewOut])
def list_interviews(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_application(db, application_id, user.id)
    return db.query(Interview).filter(Interview.application_id == application_id).order_by(Interview.interview_date.asc()).all()

def owned_interview(db: Session, interview_id: int, user_id: int):
    item = db.query(Interview).join(Interview.application).filter(Interview.id == interview_id, Interview.application.has(user_id=user_id)).first()
    if not item: raise HTTPException(status_code=404, detail="Interview not found")
    return item

@router.put("/interviews/{interview_id}", response_model=InterviewOut)
def update_interview(interview_id: int, payload: InterviewUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_interview(db, interview_id, user.id)
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("meeting_link") is not None: updates["meeting_link"] = str(updates["meeting_link"])
    for key, value in updates.items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item

@router.delete("/interviews/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(interview_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_interview(db, interview_id, user.id)
    db.delete(item); db.commit()
    return None
