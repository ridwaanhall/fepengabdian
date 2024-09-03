from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from datetime import date
from typing import Union
from pydantic import Json
from pathlib import Path

from app.models import User, Kegiatan, Pamong
from app.dependencies import db_dependency, admin_dependency
from app.routers.pamong import PamongBase

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def get_users(db: db_dependency, admin: admin_dependency):

    users = db.query(User).filter(User.is_admin == False).all()

    return users


@router.get("/users/{user_id}")
async def get_user_by_id(user_id: int, db: db_dependency, admin: admin_dependency):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: db_dependency, admin: admin_dependency):

    user = (
        db.query(User)
        .filter((User.id == user_id))
        .filter(User.is_admin == False)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"detail": "User deleted"}


@router.get("/pamong")
async def get_pamong(db: db_dependency, admin: admin_dependency):
    pamong = db.query(Pamong).all()
    if not pamong:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pamong not found"
        )

    return pamong


@router.get("/pamong/{pamong_id}")
async def get_pamong_by_id(pamong_id: int, db: db_dependency, admin: admin_dependency):
    pamong = db.query(Pamong).filter(Pamong.id == pamong_id).first()

    if not pamong:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pamong not found"
        )

    return pamong


@router.put("/pamong/{pamong_id}")
async def update_pamong(
    pamong_id: int,
    pamong: Json[PamongBase],
    db: db_dependency,
    admin: admin_dependency,
    file: Union[UploadFile, str] = File(None),
):
    pamong_data = db.query(Pamong).filter(Pamong.id == pamong_id).first()

    if not pamong_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pamong not found"
        )

    uploads_path = "app/uploads/"

    if file:
        image = await file.read()
        image_path = f"{uploads_path}{file.filename}"
        with open(image_path, "wb") as dump:
            dump.write(image)
        pamong_data.gambar = image_path

    for key, value in pamong.model_dump(exclude_unset=True).items():
        setattr(pamong_data, key, value)

    db.commit()
    db.refresh(pamong_data)

    return {"detail": "Pamong updated"}


@router.delete("/pamong/{pamong_id}")
async def delete_pamong(db: db_dependency, pamong_id: int, admin: admin_dependency):
    pamong = db.query(Pamong).filter(Pamong.id == pamong_id).first()

    if not pamong:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pamong not found"
        )

    db.delete(pamong)
    db.commit()

    return {"detail": "Pamong deleted"}


@router.get("/pamong/{pamong_id}/image")
async def get_pamong_image(pamong_id: int, db: db_dependency):
    pamong = db.query(Pamong).filter(Pamong.id == pamong_id).first()

    if not pamong:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pamong not found"
        )

    try:
        return FileResponse(pamong.gambar)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )


# Get all kegiatan by date
@router.get("/kegiatan")
async def get_kegiatan(
    db: db_dependency, admin: admin_dependency, start_date: date, end_date: date
):
    kegiatan = (
        db.query(Kegiatan)
        .filter(Kegiatan.tanggal >= start_date)
        .filter(Kegiatan.tanggal <= end_date)
        .all()
    )

    if len(kegiatan) == 0 or not kegiatan:
        return {"detail": "No kegiatan found"}

    return kegiatan
