from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models import (
    Assignment,
    StudentProfile,
    Subject,
)


from app.schemas import (
    AssignmentCreate,
    AssignmentResponse,
)

from app.dependencies import (
    get_db,
    get_current_student,
)


router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


# =====================================================
# CREATE ASSIGNMENT
# Teacher/Admin Use
# =====================================================

@router.post(
    "/{student_id}",
    response_model=AssignmentResponse
)
def create_assignment(

    student_id: str,

    data: AssignmentCreate,

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

    # Assignment is global (not tied to a StudentProfile in the DB schema)
    assignment = Assignment(
        subject_id=data.subject_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
    )


    db.add(assignment)

    db.commit()

    db.refresh(assignment)

    return assignment


# =====================================================
# UPDATE ASSIGNMENT
# =====================================================

# @router.put(
#     "/{assignment_id}",
#     response_model=AssignmentResponse
# )
# def update_assignment(

#     assignment_id: int,

#     data: AssignmentUpdate,

#     db: Session = Depends(get_db)

# ):

#     assignment = (

#         db.query(Assignment)

#         .filter(
#             Assignment.id == assignment_id
#         )

#         .first()
#     )

#     if not assignment:

#         raise HTTPException(
#             status_code=404,
#             detail="Assignment not found"
#         )

#     update_data = data.model_dump(
#         exclude_unset=True
#     )

#     for field, value in update_data.items():

#         setattr(
#             assignment,
#             field,
#             value
#         )

#     db.commit()

#     db.refresh(assignment)

#     return assignment


# =====================================================
# STUDENT VIEW ASSIGNMENTS
# =====================================================

@router.get(
    "/my-assignments",
    response_model=list[AssignmentResponse]
)
def my_assignments(

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    # Assignment is global, so return all assignments ordered by due date
    return (

        db.query(Assignment)

        .order_by(
            Assignment.due_date.desc()
        )

        .all()
    )


# =====================================================
# GET SINGLE ASSIGNMENT
# =====================================================

@router.get(
    "/{assignment_id}",
    response_model=AssignmentResponse
)
def get_assignment(

    assignment_id: int,

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    assignment = (

        db.query(Assignment)

        .filter(
            Assignment.id == assignment_id
        )

        .first()
    )

    if not assignment:

        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return assignment


# =====================================================
# FILTER BY SUBJECT
# =====================================================

@router.get(
    "/subject/{subject_name}",
    response_model=list[AssignmentResponse]
)
def assignments_by_subject(

    subject_name: str,

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    # Filter by subject name (Assignment stores subject_id)
    return (

        db.query(Assignment)

        .join(
            Subject,
            Assignment.subject_id == Subject.id
        )

        .filter(
            Subject.subject_name == subject_name
        )

        .all()
    )
