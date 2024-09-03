from tests.conftest import test_user, test_admin, client, test_pamong
import json


# Helper function to create and login admin
def create_and_login_admin(client, test_admin):
    client.post("/auth/admin", json=test_admin)
    response = client.post("/auth/admin/token", data=test_admin)
    assert response.status_code == 200
    return response.json()["access_token"]


# Helper function to create a user and login
def create_and_login_user(client, test_user, test_admin, test_pamong):
    admin_token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, admin_token)
    client.post("/auth/users", json=test_user)
    response = client.post("/auth/token", data=test_user)
    assert response.status_code == 200
    return response.json()["access_token"]


# Helper function to create a pamong
def create_pamong(client, test_pamong, token):
    response = client.post(
        "pamong/",
        data={"pamong": json.dumps(test_pamong)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


# Helper function to create a kegiatan
def create_kegiatan(client, token):
    response = client.post(
        "/kegiatan/",
        json={
            "nama_kegiatan": "Kegiatan 1",
            "tanggal": "2022-12-12",
            "tempat": "Tempat 1",
            "deskripsi": "Deskripsi 1",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


def test_create_kegiatan(client, test_user, test_admin, test_pamong):
    user_token = create_and_login_user(client, test_user, test_admin, test_pamong)
    create_kegiatan(client, user_token)


def test_get_kegiatan(client, test_user, test_admin, test_pamong):
    user_token = create_and_login_user(client, test_user, test_admin, test_pamong)
    create_kegiatan(client, user_token)
    response = client.get(
        "/kegiatan/", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200


def test_create_kegiatan_as_admin(client, test_admin):
    admin_token = create_and_login_admin(client, test_admin)
    response = client.post(
        "/kegiatan/",
        json={
            "nama_kegiatan": "Kegiatan 1",
            "tanggal": "2022-12-12",
            "tempat": "Tempat 1",
            "deskripsi": "Deskripsi 1",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
