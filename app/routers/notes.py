from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.note import Note
from app.models.followup import FollowUp
from app.models.user import User
from app.schemas.note import NoteCreate, NoteOut, FollowUpCreate, FollowUpUpdate, FollowUpOut
from app.services.application_service import owned_application
from app.utils.dependencies import get_current_user

router = APIRouter(tags=["Notes & Follow-ups"])

@router.post("/applications/{application_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(application_id: int, payload: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_application(db, application_id, user.id)
    item = Note(application_id=application_id, content=payload.content.strip())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/applications/{application_id}/notes", response_model=list[NoteOut])
def list_notes(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_application(db, application_id, user.id)
    return db.query(Note).filter(Note.application_id == application_id).order_by(Note.created_at.desc()).all()

def owned_note(db: Session, note_id: int, user_id: int):
    item = db.query(Note).join(Note.application).filter(Note.id == note_id, Note.application.has(user_id=user_id)).first()
    if not item: raise HTTPException(status_code=404, detail="Note not found")
    return item

@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_note(db, note_id, user.id)
    db.delete(item); db.commit()
    return None

@router.post("/applications/{application_id}/followups", response_model=FollowUpOut, status_code=status.HTTP_201_CREATED)
def create_followup(application_id: int, payload: FollowUpCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_application(db, application_id, user.id)
    item = FollowUp(application_id=application_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/applications/{application_id}/followups", response_model=list[FollowUpOut])
def list_followups(application_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_application(db, application_id, user.id)
    return db.query(FollowUp).filter(FollowUp.application_id == application_id).order_by(FollowUp.follow_up_date.asc()).all()

def owned_followup(db: Session, followup_id: int, user_id: int):
    item = db.query(FollowUp).join(FollowUp.application).filter(FollowUp.id == followup_id, FollowUp.application.has(user_id=user_id)).first()
    if not item: raise HTTPException(status_code=404, detail="Follow-up not found")
    return item

@router.patch("/followups/{followup_id}", response_model=FollowUpOut)
def update_followup(followup_id: int, payload: FollowUpUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_followup(db, followup_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item

@router.delete("/followups/{followup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_followup(followup_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_followup(db, followup_id, user.id)
    db.delete(item); db.commit()
    return None
