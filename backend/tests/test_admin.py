from tests.conftest import client, test_admin, test_user, test_pamong
import os
import json


# Helper function to create and login admin
def create_and_login_admin(client, test_admin):
    client.post("/auth/admin", json=test_admin)
    response = client.post("/auth/admin/token", data=test_admin)
    assert response.status_code == 200
    return response.json()["access_token"]


# Helper function to create a user
def create_user(client, test_user):
    response = client.post("/auth/users", json=test_user)
    assert response.status_code == 201


# Helper function to create a pamong
def create_pamong(client, test_pamong, token):
    response = client.post(
        "pamong/",
        data={"pamong": json.dumps(test_pamong)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


def test_get_user_as_admin(client, test_admin, test_user, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_by_id_as_admin(client, test_admin, test_user, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    # Get user id
    response = client.post("/auth/token", data=test_user)
    token_user = response.json()["access_token"]
    user_id = client.get(
        "/users/me", headers={"Authorization": f"Bearer {token_user}"}
    ).json()["id"]

    response = client.get(
        f"/admin/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_delete_user_as_admin(client, test_admin, test_user, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    # Get user id
    response = client.post("/auth/token", data=test_user)
    token_user = response.json()["access_token"]
    user_id = client.get(
        "/users/me", headers={"Authorization": f"Bearer {token_user}"}
    ).json()["id"]

    response = client.delete(
        f"/admin/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "User deleted"}


def test_get_pamong_as_admin(client, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)

    response = client.get("/admin/pamong", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_pamong_by_id_as_admin(client, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)

    # Get pamong id
    pamong_id = client.get(
        "/admin/pamong/", headers={"Authorization": f"Bearer {token}"}
    ).json()[0]["id"]

    response = client.get(
        f"/admin/pamong/{pamong_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == pamong_id


def test_update_pamong_as_admin(client, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)

    # Get pamong id
    pamong_id = client.get(
        "/admin/pamong/", headers={"Authorization": f"Bearer {token}"}
    ).json()[0]["id"]

    # Update pamong as admin
    test_pamong.update({"nama": "mDavid Hoop"})

    path = "app/uploads/"
    with open(f"{path}0.jpg", "rb") as image:
        response = client.put(
            f"admin/pamong/{pamong_id}",
            data={"pamong": json.dumps(test_pamong)},
            files={"file": ("test.jpg", image, "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    os.remove(f"{path}test.jpg")


def test_delete_pamong_as_admin(client, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)

    # Get pamong id
    pamong_id = client.get(
        "admin/pamong/", headers={"Authorization": f"Bearer {token}"}
    ).json()[0]["id"]

    response = client.delete(
        f"/admin/pamong/{pamong_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Pamong deleted"}


def test_delete_pamong_as_user(client, test_user, test_pamong, test_admin):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    # Login as user
    response = client.post("/auth/token", data=test_user)
    token = response.json()["access_token"]

    # Get pamong id (this might need adjustment depending on your API)
    pamong_id = client.get(
        "pamong/", headers={"Authorization": f"Bearer {token}"}
    ).json()["id"]

    # Delete pamong as user
    response = client.delete(
        f"admin/pamong/{pamong_id}", headers={"Authorization": token}
    )
    assert response.status_code == 401
