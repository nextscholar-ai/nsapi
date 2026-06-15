from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models import (
    StudentProfile,
    DailyClass
)

from app.schemas import (
    DailyClassCreate,
    DailyClassResponse
)

from app.dependencies import (
    get_db,
    get_current_student
)

router = APIRouter(
    prefix="/daily-class",
    tags=["Daily Class"]
)


# =====================================================
# CREATE DAILY CLASS
# Teacher/Admin Use
# =====================================================

@router.post(
    "/{student_id}",
    response_model=DailyClassResponse
)
def create_daily_class(

    student_id: str,

    data: DailyClassCreate,

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

    daily_class = DailyClass(

        student_id=student.student_id,

        subject_name=data.subject_name,

        teacher_name=data.teacher_name,

        day_name=data.day_name,

        class_date=data.class_date,

        start_time=data.start_time,

        end_time=data.end_time,

        duration=data.duration,

        attendance=data.attendance,

        behaviour=data.behaviour
    )

    db.add(daily_class)

    db.commit()

    db.refresh(daily_class)

    return daily_class


# =====================================================
# UPDATE DAILY CLASS
# Teacher/Admin Use
# =====================================================

@router.put(
    "/{class_id}",
    response_model=DailyClassResponse
)
def update_daily_class(

    class_id: int,

    data: DailyClassCreate,

    db: Session = Depends(get_db)

):

    record = (

        db.query(DailyClass)

        .filter(
            DailyClass.id == class_id
        )

        .first()
    )

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    record.subject_name = data.subject_name
    record.teacher_name = data.teacher_name
    record.day_name = data.day_name
    record.class_date = data.class_date
    record.start_time = data.start_time
    record.end_time = data.end_time
    record.duration = data.duration
    record.attendance = data.attendance
    record.behaviour = data.behaviour

    db.commit()

    db.refresh(record)

    return record


# =====================================================
# STUDENT VIEW ALL CLASSES
# =====================================================

@router.get(
    "/my-classes",
    response_model=list[DailyClassResponse]
)
def my_classes(

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    return (

        db.query(DailyClass)

        .filter(
            DailyClass.student_id
            == student.student_id
        )

        .order_by(
            DailyClass.class_date.desc()
        )

        .all()
    )


# =====================================================
# FILTER BY SUBJECT
# =====================================================

@router.get(
    "/my-classes/{subject_name}",
    response_model=list[DailyClassResponse]
)
def classes_by_subject(

    subject_name: str,

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    return (

        db.query(DailyClass)

        .filter(
            DailyClass.student_id
            == student.student_id,

            DailyClass.subject_name
            == subject_name
        )

        .order_by(
            DailyClass.class_date.desc()
        )

        .all()
    )