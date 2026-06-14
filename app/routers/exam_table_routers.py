from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Exam, Subject
from app.schemas import ExamTableCreate, ExamTableUpdate, ExamTableResponse

router = APIRouter(
    prefix="/exam-tables",
    tags=["Exam Tables"],
)


def _get_exam(db: Session, exam_id: int) -> Exam:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


def _resolve_subject_id(db: Session, subject_name: str) -> Subject:
    subject = db.query(Subject).filter(Subject.subject_name == subject_name).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


def _exam_to_response(db: Session, exam: Exam) -> ExamTableResponse:
    subject = db.query(Subject).filter(Subject.id == exam.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Build response explicitly because Exam model stores subject_id
    return ExamTableResponse(
        id=exam.id,
        subject_name=subject.subject_name,
        exam_name=exam.exam_name,
        exam_date=exam.exam_date,
        title=exam.title,
        duration=exam.duration,
        total_marks=exam.total_marks,
    )


@router.post("", response_model=ExamTableResponse, status_code=201)
def create_exam_table(data: ExamTableCreate, db: Session = Depends(get_db)):
    subject = _resolve_subject_id(db, data.subject_name)

    # Prevent duplicates (subject_id, exam_name, exam_date)
    existing = (
        db.query(Exam)
        .filter(
            Exam.subject_id == subject.id,
            Exam.exam_name == data.exam_name,
            Exam.exam_date == data.exam_date,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Exam already exists for the same subject_name, exam_name, exam_date",
        )

    exam = Exam(
        subject_id=subject.id,
        exam_name=data.exam_name,
        exam_date=data.exam_date,
        title=data.title,
        duration=data.duration,
        total_marks=data.total_marks,
    )

    db.add(exam)
    db.commit()
    db.refresh(exam)

    return _exam_to_response(db, exam)


@router.put("/{exam_id}", response_model=ExamTableResponse)
def update_exam_table(
    exam_id: int,
    data: ExamTableUpdate,
    db: Session = Depends(get_db),
):
    exam = _get_exam(db, exam_id)
    update_data = data.model_dump(exclude_unset=True)

    # Resolve current subject_name for comparison with incoming subject_name
    current_subject = db.query(Subject).filter(Subject.id == exam.subject_id).first()
    if not current_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    next_subject_id = exam.subject_id
    next_subject_name = update_data.get("subject_name", current_subject.subject_name)
    if "subject_name" in update_data:
        next_subject_id = _resolve_subject_id(db, next_subject_name).id

    next_exam_name = update_data.get("exam_name", exam.exam_name)
    next_exam_date = update_data.get("exam_date", exam.exam_date)

    # If keys that participate in uniqueness are updated, check duplicates
    if (
        next_subject_id != exam.subject_id
        or next_exam_name != exam.exam_name
        or next_exam_date != exam.exam_date
    ):
        dup = (
            db.query(Exam)
            .filter(
                Exam.subject_id == next_subject_id,
                Exam.exam_name == next_exam_name,
                Exam.exam_date == next_exam_date,
                Exam.id != exam.id,
            )
            .first()
        )
        if dup:
            raise HTTPException(
                status_code=409,
                detail="Another exam already exists for the same subject_name, exam_name, exam_date",
            )

    for field, value in update_data.items():
        if field == "subject_name":
            setattr(exam, "subject_id", next_subject_id)
        else:
            setattr(exam, field, value)

    db.commit()
    db.refresh(exam)

    return _exam_to_response(db, exam)


@router.get("/{exam_id}", response_model=ExamTableResponse)
def get_exam_table(exam_id: int, db: Session = Depends(get_db)):
    exam = _get_exam(db, exam_id)
    return _exam_to_response(db, exam)


@router.get("", response_model=list[ExamTableResponse])
def list_exam_tables(
    subject_name: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Exam)

    if subject_name:
        subject = db.query(Subject).filter(Subject.subject_name == subject_name).first()
        if not subject:
            return []
        q = q.filter(Exam.subject_id == subject.id)

    exams = q.order_by(Exam.exam_date.desc()).all()
    return [_exam_to_response(db, exam) for exam in exams]

