from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models import (
    StudentProfile,
    Exam,
    ExamResult,
    Subject,
)



from app.schemas import (
    ExamCreate,
    ExamUpdate,
    ExamResponse,
)

from app.dependencies import (
    get_db,
    get_current_student,
)


router = APIRouter(
    prefix="/exams",
    tags=["Exams"]
)


# =====================================================
# CREATE EXAM RESULT
# Teacher/Admin Use
# =====================================================

@router.post(
    "/{student_id}",
    response_model=ExamResponse
)
def create_exam(

    student_id: str,

    data: ExamCreate,

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

    percentage: float = 0.0

    # Ensure numeric types for DB model (ExamResult fields are Float)
    total_marks = float(data.total_marks or 0)
    obtained_marks = float(data.obtained_marks or 0)

    if total_marks > 0:
        percentage = round((obtained_marks / total_marks) * 100, 2)

    # Resolve Exam row first so ExamResult can be linked via Exam_id
    if data.exam_id is not None:
        exam = db.query(Exam).filter(Exam.id == data.exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam table row not found")
    else:
        exam = (
            db.query(Exam)
            .join(Subject, Exam.subject_id == Subject.id)
            .filter(
                Subject.subject_name == data.subject_name,
                Exam.exam_name == data.exam_name,
                Exam.exam_date == data.exam_date,
            )
            .first()
        )


        if not exam:
            # Exam table model uses subject_id (not subject_name)
            subject = (
                db.query(Subject)
                .filter(Subject.subject_name == data.subject_name)
                .first()
            )
            if not subject:
                raise HTTPException(status_code=404, detail="Subject not found")

            exam = Exam(
                subject_id=subject.id,
                exam_name=data.exam_name,
                exam_date=data.exam_date,
                # These fields are required in model; set safe defaults
                duration="",
                title=None,
                total_marks=float(data.total_marks or 0),
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)


    # Exam model stores only subject_id; ExamResult expects subject_name
    subject_for_result = (
        db.query(Subject)
        .filter(Subject.id == exam.subject_id)
        .first()
    )
    if not subject_for_result:
        raise HTTPException(status_code=404, detail="Subject not found")

    result = ExamResult(
        Exam_id=exam.id,
        student_id=student.student_id,

        subject_name=subject_for_result.subject_name,
        exam_name=exam.exam_name,
        exam_date=exam.exam_date,
        total_marks=total_marks,
        obtained_marks=obtained_marks,
        percentage=percentage,
    )



    db.add(result)
    db.commit()
    db.refresh(result)

    return result



# =====================================================
# UPDATE EXAM
# =====================================================

@router.put(
    "/{exam_id}",
    response_model=ExamResponse
)
def update_exam(

    exam_id: int,

    data: ExamUpdate,

    db: Session = Depends(get_db)

):

    exam = (
        db.query(ExamResult)
        .filter(
            ExamResult.Exam_id == exam_id
        )
        .first()
    )


    if not exam:

        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            exam,
            field,
            value
        )

    if exam.total_marks > 0:

        exam.percentage = round(
            (
                exam.obtained_marks
                /
                exam.total_marks
            ) * 100,
            2
        )

    db.commit()

    db.refresh(exam)

    return exam


# =====================================================
# STUDENT VIEW ALL EXAMS
# =====================================================

@router.get(
    "/my-results",
    response_model=list[ExamResponse]
)
def my_results(

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    return (

        db.query(ExamResult)

        .filter(
            ExamResult.student_id
            == student.student_id
        )

        .order_by(
            ExamResult.exam_date.desc()
        )

        .all()
    )


# =====================================================
# SINGLE RESULT
# =====================================================

@router.get(
    "/result/{exam_id}",
    response_model=ExamResponse
)
def single_result(

    exam_id: int,

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    exam = (
        db.query(ExamResult)
        .filter(
            ExamResult.Exam_id == exam_id,
            ExamResult.student_id == student.student_id,
        )
        .first()
    )

    if not exam:

        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )

    return exam


# =====================================================
# FILTER BY SUBJECT
# =====================================================

@router.get(
    "/subject/{subject_name}",
    response_model=list[ExamResponse]
)
def results_by_subject(

    subject_name: str,

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    return (

        db.query(ExamResult)

        .filter(
            ExamResult.student_id
            == student.student_id,

            ExamResult.subject_name
            == subject_name
        )

        .all()
    )