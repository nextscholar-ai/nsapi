import bcrypt
import random

from jose import jwt, JWTError
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer

# =========================
# CONFIG
# =========================

SECRET_KEY = "your_super_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

serializer = URLSafeTimedSerializer(SECRET_KEY)


# =========================
# PASSWORD HASH
# =========================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode(),
        hashed.encode()
    )


# =========================
# JWT TOKEN
# =========================

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload.get("sub")

    except JWTError:
        return None


# =========================
# RESET TOKEN
# =========================

def create_reset_token(email: str):
    return serializer.dumps(email, salt="reset-password")


def verify_reset_token(token: str, max_age=1800):
    try:
        return serializer.loads(
            token,
            salt="reset-password",
            max_age=max_age
        )
    except Exception:
        return None


# =========================
# OTP
# =========================

def generate_otp():
    return str(random.randint(100000, 999999))

