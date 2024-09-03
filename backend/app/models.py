from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Pamong(Base):
    __tablename__ = "pamong"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)  #
    nik = Column(String(16), unique=True, nullable=False)
    nip = Column(String(18), unique=True, nullable=True)  #
    tempat_lahir = Column(String(50), nullable=True)
    tanggal_lahir = Column(Date, nullable=True)
    alamat = Column(String, nullable=True)
    status_kawin = Column(
        Enum("Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati"), nullable=True
    )
    pekerjaan = Column(String(50), nullable=True)
    jabatan = Column(String(50), nullable=True)  #
    gol_darah = Column(Enum("A", "B", "AB", "O"), nullable=True)
    agama = Column(
        Enum("Islam", "Kristen", "Katolik", "Hindu", "Budha", "Konghucu"), nullable=True
    )
    jenis_kelamin = Column(Enum("L", "P"), nullable=True)
    masa_jabatan_mulai = Column(Integer, nullable=True)
    masa_jabatan_selesai = Column(Integer, nullable=True)
    pendidikan_terakhir = Column(String(50), nullable=True)
    gambar = Column(String, nullable=True)

    user = relationship("User", back_populates="pamong")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    email = Column(String(50), unique=True, nullable=True)

    pamong_id = Column(Integer, ForeignKey("pamong.id"))

    pamong = relationship("Pamong", back_populates="user")

    kegiatan = relationship("Kegiatan", back_populates="user")


class Kegiatan(Base):
    __tablename__ = "kegiatan"

    id = Column(Integer, primary_key=True, index=True)
    nama_kegiatan = Column(String(50))
    tanggal = Column(Date)
    tempat = Column(String(50))
    deskripsi = Column(String(2000))
    gambar = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="kegiatan")
