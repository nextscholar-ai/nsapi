from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy import func

from sqlalchemy.orm import Session

from app.models import (
    Subject,
    SubjectProgress,
    StudentProfile
)

from app.schemas import (
    SubjectCreate,
    SubjectResponse,
    SubjectProgressCreate,
    SubjectProgressResponse
)

from app.dependencies import (
    get_db,
    get_current_student
)

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


# =====================================================
# CREATE SUBJECT
# =====================================================
# Used by admin later
# For now create Math Science English manually
# =====================================================

@router.post(
    "/",
    response_model=SubjectResponse
)
def create_subject(

    data: SubjectCreate,

    db: Session = Depends(get_db)

):

    existing = (

        db.query(Subject)

        .filter(
            func.lower(Subject.subject_name) == func.lower(data.subject_name)
        )

        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Subject already exists"
        )

    subject = Subject(
        subject_name=data.subject_name
    )

    db.add(subject)

    db.commit()

    db.refresh(subject)

    return subject


# =====================================================
# GET ALL SUBJECTS
# =====================================================

@router.get(
    "/",
    response_model=list[SubjectResponse]
)
def get_subjects(

    db: Session = Depends(get_db)

):

    return db.query(
        Subject
    ).all()


# =====================================================
# CREATE SUBJECT PROGRESS
# =====================================================
# Teacher/Admin will use later
# =====================================================

@router.post(
    "/progress/{student_id}",
    response_model=SubjectProgressResponse
)
def create_subject_progress(

    student_id: str,

    data: SubjectProgressCreate,

    db: Session = Depends(get_db)

):

    student = (

        db.query(StudentProfile)

        .filter(
            StudentProfile.student_id
            == student_id
        )

        .first()
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing = (

        db.query(SubjectProgress)

        .filter(
            SubjectProgress.student_id
            == student.student_id,


            SubjectProgress.subject_id
            == data.subject_id
        )

        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Progress already exists"
        )

    progress = SubjectProgress(

        student_id=student.student_id,


        subject_id=data.subject_id,

        total_chapters=data.total_chapters,

        completed_chapters=data.completed_chapters,

        total_classes=data.total_classes,

        attended_classes=data.attended_classes
    )

    db.add(progress)

    db.commit()

    db.refresh(progress)

    return SubjectProgressResponse(
        id=progress.id,
        subject_name=(progress.subject.subject_name if progress.subject else ""),
        total_chapters=progress.total_chapters,
        completed_chapters=progress.completed_chapters,
        total_classes=progress.total_classes,
        attended_classes=progress.attended_classes,
    )


# =====================================================
# UPDATE SUBJECT PROGRESS
# =====================================================


@router.put(
    "/progress/{student_id}/{subject_id}",
    response_model=SubjectProgressResponse
)
def update_subject_progress(

    student_id: str,

    subject_id: int,

    data: SubjectProgressCreate,

    db: Session = Depends(get_db)

):

    student = (

        db.query(StudentProfile)

        .filter(
            StudentProfile.student_id
            == student_id
        )

        .first()
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    progress = (

        db.query(SubjectProgress)

        .filter(
            SubjectProgress.student_id
            == student.student_id,

            SubjectProgress.subject_id
            == subject_id

        )

        .first()
    )

    if not progress:

        raise HTTPException(
            status_code=404,
            detail="Progress not found"
        )

    progress.total_chapters = data.total_chapters

    progress.completed_chapters = data.completed_chapters

    progress.total_classes = data.total_classes

    progress.attended_classes = data.attended_classes

    db.commit()

    db.refresh(progress)

    return SubjectProgressResponse(
        id=progress.id,
        subject_name=(progress.subject.subject_name if progress.subject else ""),
        total_chapters=progress.total_chapters,
        completed_chapters=progress.completed_chapters,
        total_classes=progress.total_classes,
        attended_classes=progress.attended_classes,
    )


# =====================================================
# STUDENT VIEW PROGRESS
# =====================================================

@router.get(
    "/my-progress",
    response_model=list[SubjectProgressResponse]
)
def my_progress(

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    progresses = (

        db.query(
            SubjectProgress
        )

        .filter(
            SubjectProgress.student_id
            == student.student_id

        )

        .all()
    )

    return [
        SubjectProgressResponse(
            id=p.id,
            subject_name=(p.subject.subject_name if p.subject else ""),

            total_chapters=p.total_chapters,
            completed_chapters=p.completed_chapters,
            total_classes=p.total_classes,
            attended_classes=p.attended_classes,
        )
        for p in progresses
    ]


