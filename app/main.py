from fastapi import FastAPI

from app.database import Base, engine

# IMPORT MODELS (IMPORTANT)
import app.models

# ROUTERS
from app.routers.auth_routers import router as auth_router
from app.routers.student_routers import router as student_router
from app.routers.subject_routers import router as subject_router
from app.routers.daily_class_routers import router as daily_class_router
from app.routers.assignment_routers import router as assignment_router
from app.routers.exam_routers import router as exam_router
from app.routers.exam_table_routers import router as exam_table_router

from app.routers.fees_routers import router as fees_router
from app.routers.chat_routers import router as chat_router
from app.routers.dashboard_routers import router as dashboard_router

# CREATE TABLES
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Activity Dashboard API"
)


# =========================
# ROUTERS
# =========================

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(subject_router)
app.include_router(daily_class_router)
app.include_router(assignment_router)
app.include_router(exam_router)
app.include_router(exam_table_router)
app.include_router(fees_router)

app.include_router(chat_router)
app.include_router(dashboard_router)


# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Student ERP Backend Active"
    }