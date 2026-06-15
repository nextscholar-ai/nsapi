from pydantic import (
    BaseModel,
    EmailStr,
    Field
)

from typing import Optional
from datetime import datetime


# =====================================================
# AUTH
# =====================================================

class SignupSchema(BaseModel):
    email: EmailStr

    phone: str = Field(
        min_length=10,
        max_length=10
    )

    password: str = Field(
        min_length=8
    )


class LoginSchema(BaseModel):
    identifier: str
    password: str


class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6
    )


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str

    new_password: str = Field(
        min_length=8
    )


# =====================================================
# STUDENT PROFILE
# =====================================================

class StudentProfileCreate(BaseModel):

    student_name: str

    student_phone: Optional[str] = None

    student_class: Optional[str] = None

    student_address: Optional[str] = None

    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None

    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None

    school_name: Optional[str] = None
    school_address: Optional[str] = None

    medium: Optional[str] = None

    board: Optional[str] = None

    profile_image_url: Optional[str] = None


class StudentProfileUpdate(BaseModel):

    student_name: Optional[str] = None

    student_phone: Optional[str] = None

    student_class: Optional[str] = None

    student_address: Optional[str] = None

    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None

    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None

    school_name: Optional[str] = None
    school_address: Optional[str] = None

    medium: Optional[str] = None

    board: Optional[str] = None

    profile_image_url: Optional[str] = None


class StudentProfileResponse(BaseModel):

    student_id: str

    student_name: str

    student_email: str


    student_phone: Optional[str] = None

    student_class: Optional[str] = None

    student_address: Optional[str] = None

    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None

    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None

    school_name: Optional[str] = None
    school_address: Optional[str] = None

    medium: Optional[str] = None

    board: Optional[str] = None

    profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================
# ALUMNUS DETAIL
# =====================================================

class AlumnusDetailCreate(BaseModel):

    student_address: Optional[str] = None

    student_class: Optional[str] = None

    medium: Optional[str] = None

    previous_result: Optional[str] = None


class AlumnusDetailUpdate(BaseModel):

    student_address: Optional[str] = None

    student_class: Optional[str] = None

    medium: Optional[str] = None

    previous_result: Optional[str] = None


class AlumnusDetailResponse(BaseModel):



    student_id: str

    student_name: str

    student_address: Optional[str] = None

    student_class: Optional[str] = None

    medium: Optional[str] = None

    previous_result: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================
# SUBJECT
# =====================================================

class SubjectCreate(BaseModel):
    subject_name: str


class SubjectResponse(BaseModel):

    id: int

    subject_name: str

    class Config:
        from_attributes = True


# =====================================================
# SUBJECT PROGRESS
# =====================================================

class SubjectProgressCreate(BaseModel):

    subject_id: int

    total_chapters: int

    completed_chapters: int

    total_classes: int

    attended_classes: int


class SubjectProgressResponse(BaseModel):
    
    id: int
    subject_name: str
    
    total_chapters: int
    completed_chapters: int
    
    total_classes: int
    attended_classes: int
    
    class Config:
        from_attributes = True



# =====================================================
# DAILY CLASS
# =====================================================

class DailyClassCreate(BaseModel):

    subject_name: str

    teacher_name: str

    day_name: str

    class_date: datetime

    start_time: str

    end_time: str

    duration: str

    attendance: str

    behaviour: str | None = None


class DailyClassResponse(BaseModel):

    id: int

    subject_name: str

    teacher_name: str

    day_name: str

    class_date: datetime

    start_time: str

    end_time: str

    duration: str

    attendance: str

    behaviour: str | None = None

    class Config:
        from_attributes = True




# =====================================================
# ASSIGNMENTS
# =====================================================

class AssignmentCreate(BaseModel):

    subject_id: int

    title: str

    description: Optional[str] = None

    due_date: datetime


class AssignmentResponse(BaseModel):

    id: int

    subject_id: int

    title: str

    description: Optional[str] = None

    due_date: datetime

    class Config:
        from_attributes = True


# =====================================================
# ASSIGNMENT SUBMISSION
# =====================================================

class AssignmentSubmissionCreate(BaseModel):

    assignment_id: int

    submission_type: str

    text_content: Optional[str] = None

    file_path: Optional[str] = None


class AssignmentSubmissionResponse(BaseModel):

    id: int

    assignment_id: int

    submission_type: str

    text_content: Optional[str] = None

    file_path: Optional[str] = None

    status: str

    marks: Optional[int] = None

    class Config:
        from_attributes = True


# =====================================================
# EXAM (Exam table)
# =====================================================

class ExamTableCreate(BaseModel):
    subject_name: str
    exam_name: str
    exam_date: datetime
    title: Optional[str] = None
    duration: str
    total_marks: float


class ExamTableUpdate(BaseModel):
    subject_name: Optional[str] = None
    exam_name: Optional[str] = None
    exam_date: Optional[datetime] = None
    title: Optional[str] = None
    duration: Optional[str] = None
    total_marks: Optional[float] = None


class ExamTableResponse(BaseModel):
    id: int
    subject_name: str
    exam_name: str
    exam_date: datetime
    title: Optional[str] = None
    duration: str
    total_marks: float

    class Config:
        from_attributes = True


# =====================================================
# EXAM RESULT (ExamResult table)
# =====================================================

class ExamCreate(BaseModel):

    # Recommended: exam_id se link karna
    exam_id: Optional[int] = None

    # Legacy/backup fields (current code fallback supports them)
    subject_name: str
    exam_name: str
    exam_date: datetime

    total_marks: float
    obtained_marks: float


class ExamUpdate(BaseModel):

    total_marks: Optional[float] = None
    obtained_marks: Optional[float] = None

    # Optional: allow updating linking fields (if you want)
    subject_name: Optional[str] = None
    exam_name: Optional[str] = None
    exam_date: Optional[datetime] = None


class ExamResponse(BaseModel):

    # ExamResult model ke composite primary key fields:
    # - Exam_id
    # - student_id
    # DB model me "id" column nahi hai.
    Exam_id: int
    student_id: str

    subject_name: str
    exam_name: str
    exam_date: datetime
    total_marks: float
    obtained_marks: float
    percentage: float

    class Config:
        from_attributes = True





# =====================================================
# FEES
# =====================================================

class FeeCreate(BaseModel):

    month: str

    paid_fee: float

    payment_date: datetime

    status: str


class FeeUpdate(BaseModel):

    month: Optional[str] = None

    paid_fee: Optional[float] = None

    payment_date: Optional[datetime] = None

    status: Optional[str] = None


class FeeResponse(BaseModel):

    id: int

    student_name: str

    phone_number: str | None = None

    month: str

    paid_fee: float

    payment_date: datetime

    status: str

    class Config:
        from_attributes = True


# =====================================================
# CHAT
# =====================================================

class MessageCreate(BaseModel):

    teacher_name: str

    message: str


class MessageResponse(BaseModel):

    id: int

    sender_student_id: str

    teacher_name: str

    message: str

    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# VOICE MESSAGE
# =====================================================

class ChatMessageCreate(BaseModel):

    sender_type: str
    sender_name: str
    message: str


class ChatMessageResponse(BaseModel):

    id: int

    sender_type: str

    sender_name: str

    message: str

    created_at: datetime

    class Config:
        from_attributes = True


class VoiceMessageCreate(BaseModel):

    sender_type: str

    sender_name: str

    voice_file: str


class VoiceMessageResponse(BaseModel):

    id: int

    sender_type: str

    sender_name: str

    voice_file: str

    created_at: datetime

    class Config:
        from_attributes = True

