from tests.conftest import client, test_user, test_admin, test_pamong
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


def test_create_and_login_user(client, test_user, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    response = client.post("/auth/token", data=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_user_with_nip(client, test_user, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    response = client.post(
        "/auth/token", data={"username": test_user["nip"], "password": "test"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_read_users_me(client, test_user, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    # Login
    response = client.post("/auth/token", data=test_user)
    token = response.json()["access_token"]

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == test_user["username"]


def test_create_and_login_admin(client, test_admin):
    response = client.post("/auth/admin", json=test_admin)
    assert response.status_code == 201
    assert response.json() == {"detail": "Admin created successfully"}

    response = client.post("/auth/admin/token", data=test_admin)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_admin_duplicate(client, test_admin):
    client.post("/auth/admin", json=test_admin)
    response = client.post("/auth/admin", json=test_admin)
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}


def test_login_admin_in_mobile(client, test_admin):
    client.post("/auth/admin", json=test_admin)
    response = client.post("/auth/token", data=test_admin)
    assert response.status_code == 401


def test_login_user_in_admin(client, test_user, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    response = client.post("/auth/admin/token", data=test_user)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized access"}


def test_refresh_token(client, test_user, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    response = client.post("/auth/token", data=test_user)
    token = response.json()["access_token"]
    assert response.status_code == 200

    response = client.post(
        "/auth/refresh-token", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_forget_password(client, test_user, test_admin, test_pamong):
    token = create_and_login_admin(client, test_admin)
    create_pamong(client, test_pamong, token)
    create_user(client, test_user)

    response = client.post("/auth/forget-password", json={"email": test_user["email"]})
    reset_password_token = response.json()["reset_password_token"]
    assert response.status_code == 200

    response = client.post(
        "/auth/reset-password",
        json={
            "token": reset_password_token,
            "new_password": "new",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset successfully"}
