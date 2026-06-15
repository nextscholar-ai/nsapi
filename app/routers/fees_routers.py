from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models import (
    StudentProfile,
    Fee
)

from app.schemas import (
    FeeCreate,
    FeeUpdate,
    FeeResponse
)

from app.dependencies import (
    get_db,
    get_current_student
)

router = APIRouter(
    prefix="/fees",
    tags=["Fees"]
)


# =====================================================
# CREATE FEE RECORD
# Teacher/Admin Use
# =====================================================

@router.post(
    "/{student_id}",
    response_model=FeeResponse
)
def create_fee(

    student_id: str,

    data: FeeCreate,

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

    fee = Fee(

        student_id=student.student_id,

        month=data.month,

        paid_amount=data.paid_fee,

        payment_date=data.payment_date,

        status=data.status
    )

    db.add(fee)

    db.commit()

    db.refresh(fee)

    return {

        "id": fee.id,

        "student_name": student.student_name,

        "phone_number": student.student_phone,

        "month": fee.month,

        "paid_fee": fee.paid_amount,

        "payment_date": fee.payment_date,

        "status": fee.status
    }


# =====================================================
# UPDATE FEE RECORD
# =====================================================

@router.put(
    "/{fee_id}",
    response_model=FeeResponse
)
def update_fee(

    fee_id: int,

    data: FeeUpdate,

    db: Session = Depends(get_db)

):

    fee = (

        db.query(Fee)

        .filter(
            Fee.id == fee_id
        )

        .first()
    )

    if not fee:

        raise HTTPException(
            status_code=404,
            detail="Fee record not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            fee,
            field,
            value
        )

    db.commit()

    db.refresh(fee)

    student = (

        db.query(StudentProfile)

        .filter(
            StudentProfile.student_id
            == fee.student_id
        )

        .first()
    )

    return {

        "id": fee.id,

        "student_name": student.student_name,

        "phone_number": student.student_phone,

        "month": fee.month,

        "paid_fee": fee.paid_amount,

        "payment_date": fee.payment_date,

        "status": fee.status
    }


# =====================================================
# STUDENT VIEW FEES
# =====================================================

@router.get(
    "/my-fees",
    response_model=list[FeeResponse]
)
def my_fees(

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    records = (

        db.query(Fee)

        .filter(
            Fee.student_id
            == student.student_id
        )

        .order_by(
            Fee.payment_date.desc()
        )

        .all()
    )

    result = []

    for fee in records:

        result.append({

            "id": fee.id,

            "student_name": student.student_name,

            "phone_number": student.student_phone,

            "month": fee.month,

            "paid_fee": fee.paid_amount,

            "payment_date": fee.payment_date,

            "status": fee.status
        })

    return result


# =====================================================
# SINGLE FEE RECORD
# =====================================================

@router.get(
    "/{fee_id}",
    response_model=FeeResponse
)
def fee_detail(

    fee_id: int,

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    fee = (

        db.query(Fee)

        .filter(
            Fee.id == fee_id,

            Fee.student_id
            == student.student_id
        )

        .first()
    )

    if not fee:

        raise HTTPException(
            status_code=404,
            detail="Fee record not found"
        )

    return {

        "id": fee.id,

        "student_name": student.student_name,

        "phone_number": student.student_phone,

        "month": fee.month,

        "paid_fee": fee.paid_amount,

        "payment_date": fee.payment_date,

        "status": fee.status
    }