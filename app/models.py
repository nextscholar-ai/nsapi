from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship

from .database import Base


# =====================================================
# USERS
# =====================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        String,
        unique=True,
        nullable=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="student"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    last_login = Column(
        DateTime,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    student_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =====================================================
# OTP
# =====================================================

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String,
        nullable=False,
        index=True
    )

    otp = Column(
        String,
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    is_used = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# STUDENT PROFILE
# =====================================================

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    student_id = Column(
        String,
        unique=True,
        primary_key=True,   
        index=True,
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )


    student_name = Column(
        String,
        nullable=False
    )

    student_email = Column(
        String,
        nullable=False
    )

    student_phone = Column(
        String,
        nullable=True
    )

    student_class = Column(
        String,
        nullable=True
    )

    student_address = Column(
        Text,
        nullable=True
    )

    parent_name = Column(
        String,
        nullable=True
    )

    parent_phone = Column(
        String,
        nullable=True
    )

    guardian_name = Column(
        String,
        nullable=True
    )

    guardian_phone = Column(
        String,
        nullable=True
    )

    school_name = Column(
        String,
        nullable=True
    )

    school_address = Column(
        Text,
        nullable=True
    )

    medium = Column(
        String,
        nullable=True
    )

    board = Column(
        String,
        nullable=True
    )

    profile_image_url = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="student_profile"
    )

    alumnus_detail = relationship(
        "AlumnusDetail",
        back_populates="student_profile",
        uselist=False,
        cascade="all, delete-orphan"
    )

    subject_progress = relationship(
        "SubjectProgress",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    daily_classes = relationship(
        "DailyClass",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    exam_results = relationship(
        "ExamResult",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    fee_records = relationship(
        "Fee",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    assignment_submissions = relationship(
        "AssignmentSubmission",
        back_populates="student",
        cascade="all, delete-orphan"
    )


# =====================================================
# ALUMNUS DETAIL
# =====================================================

class AlumnusDetail(Base):
    __tablename__ = "alumnus_details"


    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        unique=True,
        primary_key=True,   # make it the primary key
        index=True,
        nullable=False
    )


    student_name = Column(
        String,
        nullable=False
    )

    student_address = Column(
        Text,
        nullable=True
    )

    student_class = Column(
        String,
        nullable=True
    )

    medium = Column(
        String,
        nullable=True
    )

    previous_result = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    student_profile = relationship(
        "StudentProfile",
        back_populates="alumnus_detail"
    )


# =====================================================
# SUBJECTS
# =====================================================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)

    subject_name = Column(
        String,
        unique=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    progress_records = relationship(
        "SubjectProgress",
        back_populates="subject",
        cascade="all, delete-orphan"
    )


# =====================================================
# SUBJECT PROGRESS
# =====================================================

class SubjectProgress(Base):
    __tablename__ = "subject_progress"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        index=True,
        nullable=False
    )

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )


    total_chapters = Column(Integer, default=0)

    completed_chapters = Column(Integer, default=0)

    total_classes = Column(Integer, default=0)

    attended_classes = Column(Integer, default=0)

    student = relationship(
        "StudentProfile",
        back_populates="subject_progress"
    )

    subject = relationship(
        "Subject",
        back_populates="progress_records"
    )


# =====================================================
# DAILY CLASS
# =====================================================

class DailyClass(Base):
    __tablename__ = "daily_classes"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        index=True,
        nullable=False
    )

    subject_name = Column(
        String,
        nullable=False)


    teacher_name = Column(
        String, 
        nullable=False)

    day_name = Column(
        String,
        nullable=False
    )        

    class_date = Column(
        DateTime,
        nullable=False
    )        

    start_time = Column(String, nullable=False)

    end_time = Column(String, nullable=False)

    duration = Column(String, nullable=False)

    attendance = Column(String, nullable=False)

    behaviour = Column(Text, nullable=True)

    student = relationship(
        "StudentProfile",
        back_populates="daily_classes"
    )


# =====================================================
# ASSIGNMENTS
# =====================================================

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    due_date = Column(DateTime, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    submissions = relationship(
        "AssignmentSubmission",
        back_populates="assignment",
        cascade="all, delete-orphan"
    )


# =====================================================
# ASSIGNMENT SUBMISSION
# =====================================================

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"


    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id"),
        nullable=False,
        primary_key=True
    )

    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        primary_key=True,   
        index=True,
        nullable=False
    )

    submission_type = Column(String, nullable=False)

    text_content = Column(Text, nullable=True)

    file_path = Column(String, nullable=True)

    status = Column(String, default="Pending")

    marks = Column(Integer, nullable=True)

    submitted_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    assignment = relationship(
        "Assignment",
        back_populates="submissions"
    )

    student = relationship(
        "StudentProfile",
        back_populates="assignment_submissions"
    )


# =====================================================
# EXAM & EXAM RESULTS
# =====================================================
class Exam(Base):
    __tablename__ = "exam"

    id = Column(Integer, primary_key=True, index=True)

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    exam_name = Column(String, nullable=False)

    exam_date = Column(DateTime, nullable=False)

    title = Column(String, nullable=True)

    duration = Column(String, nullable=False)

    total_marks = Column(Float, nullable=False)

    exam_results = relationship(
        "ExamResult",
        back_populates="exam",
        cascade="all, delete-orphan"
    )



class ExamResult(Base):
    __tablename__ = "exam_results"


    Exam_id = Column(
        Integer,
        ForeignKey("exam.id"),
        nullable=False,
        primary_key=True
    )

    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        primary_key=True,   # make it the primary key
        index=True,
        nullable=False
    )

    subject_name = Column(String, nullable=False)

    exam_name = Column(String, nullable=False)

    exam_date = Column(DateTime, nullable=False)

    total_marks = Column(Float, nullable=False)

    obtained_marks = Column(Float, nullable=False)

    percentage = Column(Float, nullable=False)

    student = relationship(
        "StudentProfile",
        back_populates="exam_results"
    )

    exam = relationship(
        "Exam",
        back_populates="exam_results"
    )

# =====================================================

class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        index=True,
        nullable=False
    )

    month = Column(String, nullable=False)


    paid_amount = Column(String, nullable=False)

    payment_date = Column(DateTime, nullable=True)

    status = Column(String, nullable=False)

    student = relationship(
        "StudentProfile",
        back_populates="fee_records"
    )


# =====================================================
# TEXT  & VOICE MESSAGES
# =====================================================



class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        index=True,
        nullable=False
    )

    sender_type = Column(
        String,
        nullable=False
    )

    # student / teacher

    sender_name = Column(
        String,
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    student = relationship(
        "StudentProfile"
    )


class VoiceMessage(Base):

    __tablename__ = "voice_messages"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        String,
        ForeignKey("student_profiles.student_id"),
        index=True,
        nullable=False
    )


    sender_type = Column(
        String,
        nullable=False
    )

    sender_name = Column(
        String,
        nullable=False
    )

    voice_file = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    student = relationship(
        "StudentProfile"
    )