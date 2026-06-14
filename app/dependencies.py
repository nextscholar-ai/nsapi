from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database import SessionLocal


from app.models import (
    User,
    StudentProfile
)

from app.auth import verify_access_token



# =====================================================
# JWT TOKEN
# =====================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token"
)




# =====================================================
# DATABASE SESSION
# =====================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =====================================================
# CURRENT USER
# =====================================================

def get_current_user(

    token: str = Depends(oauth2_scheme),

    db: Session = Depends(get_db)

):

    user_id = verify_access_token(token)

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = (

        db.query(User)

        .filter(
            User.id == int(user_id)
        )

        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="Account disabled"
        )

    return user


# =====================================================
# CURRENT STUDENT PROFILE
# =====================================================

def get_current_student(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    student = (

        db.query(StudentProfile)

        .filter(
            StudentProfile.user_id
            == current_user.id
        )

        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail=(
                "Student profile not found for current user. "
                f"current_user.id={current_user.id} "
                "(ensure profile row exists in student_profiles.user_id)"
            )
        )

    return student


# =====================================================
# STUDENT BY STUDENT_ID
# =====================================================

def get_student_by_student_id(

    student_id: str,

    db: Session

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

    return student


# =====================================================
# CURRENT STUDENT ID
# =====================================================

def get_current_student_id(

    current_user: User = Depends(
        get_current_user
    )
):

    return current_user.student_id