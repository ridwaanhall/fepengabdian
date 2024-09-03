from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Union
from PIL import Image
import io


from app.dependencies import db_dependency, admin_dependency, user_dependency
from app.models import Pamong, User

router = APIRouter(prefix="/pamong", tags=["pamong"])


class StatusKawinEnum(str, Enum):
    Belum_Kawin = "Belum Kawin"
    Kawin = "Kawin"
    Cerai_Hidup = "Cerai Hidup"
    Cerai_Mati = "Cerai Mati"


class GologanDarahEnum(str, Enum):
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"


class AgamaEnum(str, Enum):
    Islam = "Islam"
    Kristen = "Kristen"
    Katolik = "Katolik"
    Hindu = "Hindu"
    Budha = "Budha"
    Konghucu = "Konghucu"


class JenisKelaminEnum(str, Enum):
    L = "L"
    P = "P"


class PamongBase(BaseModel):
    nama: str
    nik: str
    nip: str
    tempat_lahir: str
    tanggal_lahir: datetime
    alamat: str
    status_kawin: StatusKawinEnum
    pekerjaan: str
    jabatan: str
    gol_darah: GologanDarahEnum
    agama: AgamaEnum
    jenis_kelamin: JenisKelaminEnum
    masa_jabatan_mulai: int
    masa_jabatan_selesai: int
    pendidikan_terakhir: str


@router.post("/", status_code=201)
async def create_pamong(
    pamong: Json[PamongBase],
    db: db_dependency,
    file: Union[UploadFile, str] = File(None),
):
    if db.query(Pamong).filter(Pamong.nip == pamong.nip).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Pamong already exists"
        )

    new_pamong = Pamong(**pamong.model_dump())

    uploads_path = "app/uploads/"
    if file:
        image = await file.read()
        with open(f"{uploads_path}{file.filename}", "wb") as dump:
            dump.write(image)
        new_pamong.gambar = f"{uploads_path}{file.filename}"

    db.add(new_pamong)
    db.commit()
    db.refresh(new_pamong)

    return {"detail": "Pamong created"}


@router.get("/")
async def get_pamong(db: db_dependency, user: user_dependency):
    user_data = db.query(User).filter(User.id == user["id"]).first()
    if not user_data.pamong:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user_data.pamong


@router.put("/")
async def update_pamong(
    user: user_dependency,
    pamong: Json[PamongBase],
    db: db_dependency,
    file: Union[UploadFile, str] = File(None),
):
    user_data = db.query(User).filter(User.id == user["id"]).first()

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pamong not found"
        )

    pamong_to_update = user_data.pamong
    if file:
        image = await file.read()
        with open(f"app/uploads/{file.filename}", "wb") as dump:
            dump.write(image)
        pamong_to_update.gambar = file.filename

    for key, value in pamong.model_dump(exclude_unset=True).items():
        setattr(pamong_to_update, key, value)

    db.commit()
    db.refresh(pamong_to_update)

    return {"detail": "Pamong updated"}
