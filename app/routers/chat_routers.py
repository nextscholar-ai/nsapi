from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models import (
    StudentProfile,
    ChatMessage,
    VoiceMessage
)

from app.schemas import (
    ChatMessageCreate,
    ChatMessageResponse,
    VoiceMessageCreate,
    VoiceMessageResponse
)

from app.dependencies import (
    get_db,
    get_current_student
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# =====================================================
# SEND TEXT MESSAGE
# =====================================================

@router.post(
    "/message/{student_id}",
    response_model=ChatMessageResponse
)
def send_message(

    student_id: str,

    data: ChatMessageCreate,

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

    chat = ChatMessage(

        student_id=student.student_id,

        sender_type=data.sender_type,

        sender_name=data.sender_name,

        message=data.message
    )

    db.add(chat)

    db.commit()

    db.refresh(chat)

    return chat


# =====================================================
# CHAT HISTORY
# =====================================================

@router.get(
    "/messages",
    response_model=list[ChatMessageResponse]
)
def my_messages(

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    return (

        db.query(ChatMessage)

        .filter(
            ChatMessage.student_id
            == student.student_id
        )

        .order_by(
            ChatMessage.created_at.asc()
        )

        .all()
    )


# =====================================================
# SEND VOICE MESSAGE
# =====================================================

@router.post(
    "/voice/{student_id}",
    response_model=VoiceMessageResponse
)
def send_voice_message(

    student_id: str,

    data: VoiceMessageCreate,

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

    voice = VoiceMessage(

        student_id=student.student_id,

        sender_type=data.sender_type,

        sender_name=data.sender_name,

        voice_file=data.voice_file
    )

    db.add(voice)

    db.commit()

    db.refresh(voice)

    return voice


# =====================================================
# VOICE HISTORY
# =====================================================

@router.get(
    "/voice",
    response_model=list[VoiceMessageResponse]
)
def my_voice_messages(

    student: StudentProfile = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)

):

    return (

        db.query(VoiceMessage)

        .filter(
            VoiceMessage.student_id
            == student.student_id
        )

        .order_by(
            VoiceMessage.created_at.desc()
        )

        .all()
    )