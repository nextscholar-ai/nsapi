from pyexpat.errors import messages

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

import os
import uuid
from pathlib import Path

from fastapi import (
    UploadFile,
    File,
    Form,
    HTTPException
)

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


