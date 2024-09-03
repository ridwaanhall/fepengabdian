import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from main import app


@pytest.fixture(scope="function")
def db_session():
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user():
    return {
        "username": "test",
        "password": "test",
        "nip": "198703212011011005",
        "email": "test@gmail.com",
    }


@pytest.fixture(scope="function")
def test_admin():
    return {"username": "admin", "password": "admin"}


@pytest.fixture(scope="function")
def test_pamong():
    return {
        "nama": "David Lee",
        "nik": "3216012304891238",
        "nip": "198703212011011005",
        "tempat_lahir": "Medan",
        "tanggal_lahir": "1987-03-21T06:54:18.299Z",
        "alamat": "Jl. Sisingamangaraja No. 101, Medan",
        "status_kawin": "Kawin",
        "pekerjaan": "PNS",
        "jabatan": "Kepala Sub Bagian",
        "gol_darah": "A",
        "agama": "Hindu",
        "jenis_kelamin": "L",
        "masa_jabatan_mulai": 2017,
        "masa_jabatan_selesai": 2022,
        "pendidikan_terakhir": "S1 Teknik Sipil",
    }
