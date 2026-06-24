from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)

from app.schemas import NoticeResponse

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import (
    Notice,
    NoticeAttachment
)

import os
import shutil
import uuid

router = APIRouter(
    prefix="/notices",
    tags=["Notice Board"]
)

UPLOAD_DIR = "uploads/notices"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@router.post("/", response_model=NoticeResponse)
def create_notice(
    title: str = Form(...),
    description: str = Form(None),
    files: list[UploadFile] = File([]),
    db: Session = Depends(get_db)
):

    notice = Notice(
        title=title,
        description=description
    )

    db.add(notice)
    db.commit()
    db.refresh(notice)

    for file in files:

        extension = os.path.splitext(
            file.filename
        )[1]

        unique_name = (
            str(uuid.uuid4()) +
            extension
        )

        file_path = os.path.join(
            UPLOAD_DIR,
            unique_name
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        file_url = f"/uploads/notices/{unique_name}"

        attachment = NoticeAttachment(
            notice_id=notice.id,
            file_name=file.filename,
            file_path=file_url,
            file_type=file.content_type
        )

        db.add(attachment)

    db.commit()

    

    db.refresh(notice)

    notice = db.query(Notice).filter(
        Notice.id == notice.id
    ).first()

    return notice


@router.get("/",response_model=list[NoticeResponse])
def get_all_notices(
    db: Session = Depends(get_db)
):

    notices = db.query(
        Notice
    ).order_by(
        Notice.created_at.desc()
    ).all()

    return notices



@router.get("/{notice_id}",response_model=NoticeResponse)
def get_notice(
    notice_id: int,
    db: Session = Depends(get_db)
):

    notice = db.query(
        Notice
    ).filter(
        Notice.id == notice_id
    ).first()

    if not notice:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    return notice



@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db)
):

    notice = db.query(
        Notice
    ).filter(
        Notice.id == notice_id
    ).first()

    if not notice:
        raise HTTPException(
            status_code=404,
            detail="Notice not found"
        )

    for attachment in notice.attachments:

        if os.path.exists(
            attachment.file_path
        ):
            os.remove(
                attachment.file_path
            )

    db.delete(notice)

    db.commit()

    return {
        "message": "Notice deleted"
    }