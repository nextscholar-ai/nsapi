from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import (
    get_db,
    get_current_student
)

from app.models import (
    StudentProfile,
    AlumnusDetail,
    SubjectProgress,
    DailyClass,
    Assignment,
    AssignmentSubmission,
    ExamResult,
    Fee,
    ChatMessage
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# =====================================================
# STUDENT DASHBOARD SUMMARY
# =====================================================

@router.get("/")
def dashboard(

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

    progress_count = (

        db.query(
            SubjectProgress
        )

        .filter(
            SubjectProgress.student_id
            == student.student_id
        )

        .count()
    )

    total_classes = (

        db.query(
            DailyClass
        )

        .filter(
            DailyClass.student_id
            == student.student_id
        )

        .count()
    )

    present_classes = (

        db.query(
            DailyClass
        )

        .filter(
            DailyClass.student_id
            == student.student_id,

            func.lower(DailyClass.attendance).in_(["p", "present"])
        )

        .count()
    )

    assignments = (

        db.query(
            AssignmentSubmission
        )

        .filter(
            AssignmentSubmission.student_id
            == student.student_id
        )

        .count()
    )


    exams = (

        db.query(
            ExamResult
        )

        .filter(
            ExamResult.student_id
            == student.student_id
        )

        .count()
    )

    avg_percentage = (

        db.query(
            func.avg(
                ExamResult.percentage
            )
        )

        .filter(
            ExamResult.student_id
            == student.student_id
        )

        .scalar()
    )

    fee_records = (

        db.query(
            Fee
        )

        .filter(
            Fee.student_id
            == student.student_id
        )

        .all()
    )

    paid_count = len([
        f for f in fee_records
        if f.status.lower() == "paid"
    ])

    remaining_count = len([
        f for f in fee_records
        if f.status.lower() == "remaining"
    ])

    unread_messages = (

        db.query(
            ChatMessage
        )

        .filter(
            ChatMessage.student_id
            == student.student_id
        )

        .count()
    )

    recent_classes = (

        db.query(
            DailyClass
        )

        .filter(
            DailyClass.student_id
            == student.student_id
        )

        .order_by(
            DailyClass.class_date.desc()
        )

        .limit(5)

        .all()
    )

    class_data = []

    for cls in recent_classes:

        class_data.append({

            "subject_name":
            cls.subject_name,

            "teacher_name":
            cls.teacher_name,

            "day_name":
            cls.day_name,

            "attendance":
            cls.attendance,

            "class_date":
            cls.class_date
        })

    attendance_percentage = 0

    if total_classes > 0:

        attendance_percentage = round(

            (
                present_classes
                /
                total_classes
            ) * 100,

            2
        )

    return {

        # ==========================
        # PROFILE
        # ==========================

        "student_profile": {

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

            "school_name":
            student.school_name,

            "school_address":
            student.school_address,

            "parent_name":
            student.parent_name,

            "parent_phone":
            student.parent_phone,

            "guardian_name":
            student.guardian_name,

            "guardian_phone":
            student.guardian_phone,

            "medium":
            student.medium,

            "board":
            student.board
        },

        # ==========================
        # ALUMNUS
        # ==========================

        "alumnus_available":
        alumnus is not None,

        # ==========================
        # SUBJECT
        # ==========================

        "subject_progress_count":
        progress_count,

        # ==========================
        # ATTENDANCE
        # ==========================

        "attendance": {

            "total_classes":
            total_classes,

            "present_classes":
            present_classes,

            "attendance_percentage":
            attendance_percentage
        },

        # ==========================
        # ASSIGNMENT
        # ==========================

        "assignments": {

            "total_assignments":
            assignments
        },

        # ==========================
        # EXAM
        # ==========================

        "exam_summary": {

            "total_exams":
            exams,

            "average_percentage":
            round(
                avg_percentage or 0,
                2
            )
        },

        # ==========================
        # FEES
        # ==========================

        "fees": {

            "paid_months":
            paid_count,

            "remaining_months":
            remaining_count
        },

        # ==========================
        # CHAT
        # ==========================

        "chat": {

            "total_messages":
            unread_messages
        },

        # ==========================
        # RECENT CLASSES
        # ==========================

        "recent_classes":
        class_data
    }