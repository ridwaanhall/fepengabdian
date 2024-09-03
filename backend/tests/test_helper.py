from tests.conftest import client


def test_clear_data(client):
    response = client.delete("/helper/clear?table_name=all")
    assert response.status_code == 200

    tables = ["user", "pamong", "kegiatan"]
    for table in tables:
        response = client.delete(f"/helper/clear?table_name={table}")
        assert response.status_code == 200


def test_add_pamong(client):
    response = client.post("/helper/add_pamong/")
    print(response.json())
    assert response.status_code == 201


def test_add_kegiatan(client):
    response = client.post("/helper/add_user")
    print(response.json())
    assert response.status_code == 201


def test_add_user(client):
    response = client.post("/helper/add_user")
    print(response.json())
    assert response.status_code == 201
