from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from dotenv import load_dotenv

from typing import Annotated
import os

from app.models import User, Pamong
from app.dependencies import bcrypt_context, db_dependency, user_dependency


load_dotenv(override=True)
router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


class UserCreateRequest(BaseModel):
    nip: str
    username: str
    password: str
    email: str


class AdminCreateRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ForgetPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    token: str


def authenticate_user(
    username: str, password: str, db: db_dependency, is_admin: bool = False
):
    if is_admin:
        user = db.query(User).filter(User.username == username).first()
    else:
        user = (
            db.query(User)
            .join(Pamong, User.pamong_id == Pamong.id)
            .filter((Pamong.nip == username) | (User.username == username))
            .first()
        )

    if not user:
        return False

    if not bcrypt_context.verify(password, user.password):
        return False

    return user


def create_access_token(username: dict, user_id, is_admin, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "is_admin": is_admin}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_reset_password_token(email: str):
    encode = {"sub": email}
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateRequest, db: db_dependency):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    pamong = db.query(Pamong).filter(Pamong.nip == user.nip).first()
    if pamong:
        new_user = User(
            username=user.username,
            password=bcrypt_context.hash(user.password),
            email=user.email,
            pamong_id=pamong.id,
            pamong=pamong,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"detail": "User created successfully"}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="NIP not found",
    )


@router.post("/admin", status_code=status.HTTP_201_CREATED)
async def create_admin(user: AdminCreateRequest, db: db_dependency):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    new_user = User(
        username=user.username,
        password=bcrypt_context.hash(user.password),
        is_admin=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"detail": "Admin created successfully"}


@router.post("/admin/token", response_model=Token)
async def login_for_access_token_web(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(form_data.username, form_data.password, db, is_admin=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user.username, user.id, user.is_admin, timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/token", response_model=Token)
async def login_for_access_token_mobile(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user.username, user.id, user.is_admin, timedelta(days=7)
    )

    refresh_token = create_access_token(
        user.username, user.id, user.is_admin, timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_token(user: user_dependency):
    access_token = create_access_token(
        user["username"], user["id"], user["is_admin"], timedelta(minutes=10)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forget-password")
async def forget_password(request: ForgetPasswordRequest, db: db_dependency):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )

    reset_password_token = create_reset_password_token(user.email)

    return {"reset_password_token": reset_password_token}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: db_dependency):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password = bcrypt_context.hash(request.new_password)
    db.commit()

    return {"detail": "Password reset successfully"}
