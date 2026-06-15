from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models import (
    User,
    StudentProfile,
    AlumnusDetail
)

from app.schemas import (
    StudentProfileUpdate,
    StudentProfileResponse,
    AlumnusDetailCreate,
    AlumnusDetailUpdate,
    AlumnusDetailResponse
)

from app.dependencies import (
    get_db,
    get_current_user,
    get_current_student
)

router = APIRouter(
    prefix="/student",
    tags=["Student"]
)

# =====================================================
# GET PROFILE
# =====================================================

@router.get(
    "/profile",
    response_model=StudentProfileResponse
)
def get_profile(
    student: StudentProfile = Depends(
        get_current_student
    )
):
    # This endpoint depends on get_current_student(), so if it returns,
    # the token->user_id matched student_profiles.user_id.
    return student


# =====================================================
# UPDATE PROFILE
# =====================================================

@router.put(
    "/profile",
    response_model=StudentProfileResponse
)
def update_profile(

    data: StudentProfileUpdate,

    db: Session = Depends(get_db),

    student: StudentProfile = Depends(
        get_current_student
    )
):

    update_data = data.model_dump(
        exclude_unset=True
    )

    # Protected fields
    protected_fields = {
        "student_id",
        "student_email"
    }

    for field, value in update_data.items():

        if field in protected_fields:
            continue

        setattr(
            student,
            field,
            value
        )

    db.commit()

    db.refresh(student)

    return student


# =====================================================
# CREATE ALUMNUS DETAIL
# =====================================================

@router.post(
    "/alumnus",
    response_model=AlumnusDetailResponse
)
def create_alumnus_detail(

    data: AlumnusDetailCreate,

    db: Session = Depends(get_db),

    student: StudentProfile = Depends(
        get_current_student
    )
):

    existing = (

        db.query(AlumnusDetail)

        .filter(
            AlumnusDetail.student_id
            == student.student_id
        )

        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Alumnus detail already exists"
        )

    alumnus = AlumnusDetail(

        student_id=student.student_id,

        student_name=student.student_name,

        student_address=data.student_address,

        student_class=data.student_class,

        medium=data.medium,

        previous_result=data.previous_result
    )

    db.add(alumnus)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create alumnus detail: {e}"
        )

    # Verify row actually exists in DB after commit
    saved = (
        db.query(AlumnusDetail)
        .filter(AlumnusDetail.student_id == student.student_id)
        .first()
    )

    if not saved:
        raise HTTPException(
            status_code=500,
            detail="Commit succeeded but alumnus_details row not found"
        )

    db.refresh(saved)

    return saved


# =====================================================
# GET ALUMNUS DETAIL
# =====================================================

@router.get(
    "/alumnus",
    response_model=AlumnusDetailResponse
)
def get_alumnus_detail(

    db: Session = Depends(get_db),

    student: StudentProfile = Depends(
        get_current_student
    )
):

    alumnus = (

        db.query(AlumnusDetail)

        .filter(
            AlumnusDetail.student_id
            == student.student_id
        )

        .first()
    )

    # If alumnus detail row doesn't exist yet, return a detail payload
    # fetched from student profile instead of 404.
    if not alumnus:
        return AlumnusDetailResponse(
            student_id=student.student_id,
            student_name=student.student_name,
            student_address=student.student_address,
             student_class=student.student_class,
            medium=student.medium,
            previous_result=None,
        )

    return alumnus



# =====================================================
# UPDATE ALUMNUS DETAIL
# =====================================================

@router.put(
    "/alumnus",
    response_model=AlumnusDetailResponse
)
def update_alumnus_detail(
    data: AlumnusDetailUpdate,

    db: Session = Depends(get_db),

    student: StudentProfile = Depends(
        get_current_student
    )
):

    alumnus = (

        db.query(AlumnusDetail)

        .filter(
            AlumnusDetail.student_id
            == student.student_id
        )

        .first()
    )

    if not alumnus:

        raise HTTPException(
            status_code=404,
            detail="Alumnus detail not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            alumnus,
            field,
            value
        )

    db.commit()

    db.refresh(alumnus)

    return alumnus


# =====================================================
# STUDENT DASHBOARD
# =====================================================

@router.get("/dashboard")
def student_dashboard(

    current_user: User = Depends(
        get_current_user
    ),

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(
        get_db
    )
):

    alumnus = (

        db.query(AlumnusDetail)

        .filter(
            AlumnusDetail.student_id
            == student.student_id
        )

        .first()
    )

    return {

        "student_id":
        student.student_id,
    
        "student_name":
        student.student_name,
    
        "student_email":
        student.student_email,
    
        "student_phone":
        student.student_phone,
    
        "student_class":
        student.student_class,
    
        "student_address":
        student.student_address,
    
        "parent_name":
        student.parent_name,
    
        "parent_phone":
        student.parent_phone,
    
        "guardian_name":
        student.guardian_name,
    
        "guardian_phone":
        student.guardian_phone,
    
        "school_name":
        student.school_name,
    
        "school_address":
        student.school_address,
    
        "medium":
        student.medium,
    
        "board":
        student.board,
    
        "profile_completed":
        bool(student.student_name),
    
        "alumnus_available":
        alumnus is not None
    }    