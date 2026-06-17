from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import (
    get_db
)
from app.models import AssignmentSubmission
from app.schemas import(
    AssignmentSubmissionCreate,
    AssignmentSubmissionResponse
)

router = APIRouter(
    prefix="/assignment-submissions",
    tags=["Assignment Submissions"]
)

@router.post(
    "/submit/{student_id}",
    response_model=AssignmentSubmissionResponse
)
def submit_assignment(
    student_id: str,
    submission: AssignmentSubmissionCreate,
    db: Session = Depends(get_db)
):

    existing_submission = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.assignment_id
        == submission.assignment_id,

        AssignmentSubmission.student_id
        == student_id
    ).first()

    if existing_submission:
        raise HTTPException(
            status_code=400,
            detail="Assignment already submitted"
        )

    new_submission = AssignmentSubmission(
        assignment_id=submission.assignment_id,
        student_id=student_id,

        submission_type=submission.submission_type,
        text_content=submission.text_content,
        file_path=submission.file_path,

        status="Submitted"
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return new_submission


@router.get(
    "/student/{student_id}",
    response_model=list[AssignmentSubmissionResponse]
)
def get_student_submissions(
    student_id: str,
    db: Session = Depends(get_db)
):

    submissions = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student_id
    ).all()

    return submissions





@router.get(
    "/student/{student_id}/{assignment_id}",
    response_model=AssignmentSubmissionResponse
)
def get_submission(
    student_id: str,
    assignment_id: int,
    db: Session = Depends(get_db)
):

    submission = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student_id,

        AssignmentSubmission.assignment_id
        == assignment_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    return submission




@router.put(
    "/student/{student_id}/{assignment_id}",
    response_model=AssignmentSubmissionResponse
)
def update_submission(
    student_id: str,
    assignment_id: int,
    submission_data: AssignmentSubmissionCreate,
    db: Session = Depends(get_db)
):

    submission = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student_id,

        AssignmentSubmission.assignment_id
        == assignment_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    submission.submission_type = submission_data.submission_type
    submission.text_content = submission_data.text_content
    submission.file_path = submission_data.file_path

    db.commit()
    db.refresh(submission)

    return submission




@router.delete(
    "/student/{student_id}/{assignment_id}"
)
def delete_submission(
    student_id: str,
    assignment_id: int,
    db: Session = Depends(get_db)
):

    submission = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student_id,

        AssignmentSubmission.assignment_id
        == assignment_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    db.delete(submission)
    db.commit()

    return {
        "message": "Submission deleted successfully"
    }






