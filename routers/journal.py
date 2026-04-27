from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.journal import JournalEntryCreate, JournalEntryResponse
from services.journal_service import create_journal_entry
from models.journal import JournalEntry

router = APIRouter(
    prefix="/api/v1/journal-entries",
    tags=["Journal Entries"]
)


@router.post("/", response_model=JournalEntryResponse)
def create_entry(data: JournalEntryCreate, db: Session = Depends(get_db)):
    return create_journal_entry(db, data)


@router.get("/", response_model=list[JournalEntryResponse])
def get_entries(db: Session = Depends(get_db)):
    return db.query(JournalEntry).order_by(JournalEntry.entry_date.desc()).all()