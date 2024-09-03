import json
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from datetime import datetime
from typing import Optional

from app.dependencies import db_dependency
from app.models import Pamong, User, Kegiatan
from app.dependencies import bcrypt_context


router = APIRouter(prefix="/helper", tags=["helper"])


@router.delete("/clear")
async def clear_data(db: db_dependency, table_name: Optional[str] = "all"):
    if table_name == "all":
        db.execute(text("DELETE FROM pamong"))
        db.execute(text("DELETE FROM user"))
        db.execute(text("DELETE FROM kegiatan"))
        db.commit()

        return {"detail": "All tables cleared"}

    db.execute(text(f"DELETE FROM {table_name}"))
    db.commit()

    return {"detail": f"{table_name} cleared"}


with open("app/helper/pamong.json") as f:
    data_pamong = json.load(f)

with open("app/helper/user.json") as f:
    data_user = json.load(f)

with open("app/helper/kegiatan.json") as f:
    data_kegiatan = json.load(f)


@router.post("/add_pamong", status_code=201)
async def add_pamong(db: db_dependency):
    try:
        for item in data_pamong:
            new_item = Pamong(
                nama=item["nama"],
                nik=item["nik"],
                nip=item["nip"],
                tempat_lahir=item["tempat_lahir"],
                tanggal_lahir=datetime.strptime(
                    item["tanggal_lahir"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                alamat=item["alamat"],
                status_kawin=item["status_kawin"],
                pekerjaan=item["pekerjaan"],
                jabatan=item["jabatan"],
                gol_darah=item["gol_darah"],
                agama=item["agama"],
                jenis_kelamin=item["jenis_kelamin"],
                masa_jabatan_mulai=item["masa_jabatan_mulai"],
                masa_jabatan_selesai=item["masa_jabatan_selesai"],
                pendidikan_terakhir=item["pendidikan_terakhir"],
                gambar=item["gambar"],
            )
            db.add(new_item)
        db.commit()
        return {"detail": "Pamong added"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/add_user", status_code=201)
async def add_user(db: db_dependency):
    try:
        for item in data_user:
            pamong = db.query(Pamong).filter(Pamong.nip == item["nip"]).first()
            if pamong:
                new_user = User(
                    username=item["username"],
                    password=bcrypt_context.hash(item["password"]),
                    email=item["email"],
                    pamong_id=pamong.id,
                    pamong=pamong,
                )
                db.add(new_user)

        db.commit()
        return {"detail": "User added"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/add_kegiatan", status_code=201)
async def add_kegiatan(db: db_dependency):
    try:
        for item in data_kegiatan:
            user = db.query(User).filter(User.username == item["username"]).first()
            if user:
                for kegiatan in item["kegiatan"]:
                    new_item = Kegiatan(
                        nama_kegiatan=kegiatan["nama_kegiatan"],
                        tanggal=datetime.strptime(
                            kegiatan["tanggal"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        tempat=kegiatan["tempat"],
                        deskripsi=kegiatan["deskripsi"],
                        gambar=kegiatan["gambar"],
                        user_id=user.id,
                        user=user,
                    )
                    db.add(new_item)
        db.commit()
        return {"detail": "Kegiatan added"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
