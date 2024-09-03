from tests.conftest import test_admin, client, test_user, test_pamong
import json
import os


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


def test_create_pamong(client, test_admin, test_pamong):
    admin_token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, admin_token)


def test_get_pamong(client, test_admin, test_user, test_pamong):
    user_token = create_and_login_user(client, test_user, test_admin, test_pamong)
    response = client.get("pamong/", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200


def test_update_pamong(client, test_admin, test_user, test_pamong):
    user_token = create_and_login_user(client, test_user, test_admin, test_pamong)
    test_pamong.update({"nama": "mDavid Hoop"})

    path = "app/uploads/"
    with open(f"{path}0.jpg", "rb") as image:
        response = client.put(
            "pamong/",
            data={"pamong": json.dumps(test_pamong)},
            files={"file": ("test.jpg", image, "image/jpeg")},
            headers={"Authorization": f"Bearer {user_token}"},
        )
    assert response.status_code == 200
    os.remove(f"{path}test.jpg")
