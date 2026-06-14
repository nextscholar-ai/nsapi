from fastapi import APIRouter, HTTPException, Depends


from sqlalchemy.orm import Session
from sqlalchemy import or_

from datetime import datetime, timedelta

from app.database import SessionLocal

from app.models import (
    User,
    OTP,
    StudentProfile
)

from app.schemas import (
    SignupSchema,
    LoginSchema,
    ResetPasswordSchema,
    SendOTPRequest,
    VerifyOTPRequest,
    ForgotPasswordSchema,

)


from fastapi.security import OAuth2PasswordRequestForm


from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    verify_reset_token,
    generate_otp
)

from app.email_services import (
    send_reset_email,
    send_otp_email
)

router = APIRouter(
    tags=["Authentication"]
)


# =====================================================
# SIGNUP
# =====================================================

@router.post("/signup")
def signup(data: SignupSchema):

    db = SessionLocal()

    try:

        existing_user = db.query(User).filter(
            or_(
                User.email == data.email.lower().strip(),
                User.phone == data.phone.strip()
            )
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        new_user = User(
            username=data.email.lower().strip(),
            email=data.email.lower().strip(),
            phone=data.phone.strip(),
            password_hash=hash_password(
                data.password
            ),
            role="student"
        )

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        student_id = f"STU{new_user.id:06d}"

        new_user.student_id = student_id

        db.commit()

        db.refresh(new_user)

        profile = StudentProfile(

            user_id=new_user.id,

            student_id=student_id,

            student_name="",

            student_email=new_user.email,

            student_phone=new_user.phone
        )

        db.add(profile)

        db.commit()

        db.refresh(profile)

        return {
            "message":
            "Signup successful",

            "student_id":
            student_id
        }

    finally:
        db.close()




# =====================================================
# COMMON LOGIN FUNCTION
# =====================================================


def authenticate_user(identifier: str, password: str):

    db = SessionLocal()

    try:

        user = db.query(User).filter(
            or_(
                User.email == identifier,
                User.phone == identifier
            )
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not verify_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        user.last_login = datetime.utcnow()
        db.commit()

        token = create_access_token(
            {"sub": str(user.id)}
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "student_id": user.student_id,
        }

    finally:
        db.close()


# =====================================================
# NORMAL LOGIN
# Visible in Swagger
# =====================================================

@router.post(
    "/login",
    tags=["Authentication"]
)
def login(data: LoginSchema):

    return authenticate_user(
        identifier=data.identifier,
        password=data.password
    )


# =====================================================
# OAUTH2 LOGIN
# Used by Swagger Authorize Button
# =====================================================

@router.post(
    "/token",
    include_in_schema=False
)
def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    return authenticate_user(
        identifier=form_data.username,
        password=form_data.password
    )


# =====================================================
# SEND LOGIN OTP
# =====================================================

@router.post("/send-login-otp")
def send_login_otp(data: SendOTPRequest):

    db = SessionLocal()

    try:

        user = db.query(User).filter(
            User.email == data.email
        ).first()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        otp_code = generate_otp()

        otp_entry = OTP(

            email=data.email,

            otp=otp_code,

            expires_at=(
                datetime.utcnow()
                + timedelta(minutes=10)
            ),

            is_used=False
        )

        db.add(otp_entry)

        db.commit()

        ok = send_otp_email(
            data.email,
            otp_code
        )

        if not ok:
            raise HTTPException(
                status_code=500,
                detail="Email sending failed "
            )

        return {
            "message":
            "OTP sent successfully"
        }

    finally:
        db.close()


# =====================================================
# VERIFY LOGIN OTP
# =====================================================

@router.post("/verify-login-otp")
def verify_login_otp(
    data: VerifyOTPRequest
):

    db = SessionLocal()

    try:

        otp_record = (

            db.query(OTP)

            .filter(
                OTP.email == data.email
            )

            .order_by(
                OTP.id.desc()
            )

            .first()
        )

        if not otp_record:

            raise HTTPException(
                status_code=400,
                detail="Invalid OTP"
            )

        if otp_record.is_used:

            raise HTTPException(
                status_code=400,
                detail="OTP already used"
            )

        if otp_record.expires_at < datetime.utcnow():

            raise HTTPException(
                status_code=400,
                detail="OTP expired"
            )

        if otp_record.otp != data.otp:

            raise HTTPException(
                status_code=400,
                detail="Invalid OTP"
            )

        otp_record.is_used = True

        user = db.query(User).filter(
            User.email == data.email
        ).first()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user.last_login = datetime.utcnow()

        db.commit()

        token = create_access_token(
            {
                "sub": str(user.id)
            }
        )

        return {

            "access_token":
            token,

            "token_type":
            "bearer",

            "student_id":
            user.student_id
        }

    finally:
        db.close()


# =====================================================
# FORGOT PASSWORD
# =====================================================

@router.post("/forgot-password")
def forgot_password(
    data: "ForgotPasswordSchema"
):

    email = data.email


    if not email:

        raise HTTPException(
            status_code=400,
            detail="Email required"
        )

    db = SessionLocal()

    try:

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:

            return {
                "message":
                "If email exists, reset link sent"
            }

        token = create_reset_token(
            email
        )

        reset_link = (
            f"http://localhost:8501/"
            f"reset-password?token={token}"
        )

        ok = send_reset_email(
            email,
            reset_link
        )

        if not ok:
            raise HTTPException(
                status_code=500,
                detail="Email sending failed "
            )

        return {
            "message":
            "Password reset link sent"
        }

    finally:
        db.close()


# =====================================================
# RESET PASSWORD
# =====================================================

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordSchema
):

    db = SessionLocal()

    try:

        email = verify_reset_token(
            data.token
        )

        if not email:

            raise HTTPException(
                status_code=400,
                detail="Invalid token"
            )

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user.password_hash = hash_password(
            data.new_password
        )

        db.commit()

        return {
            "message":
            "Password reset successful"
        }

    finally:
        db.close()