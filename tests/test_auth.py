def register_user(client, name, email, password, role):
    response = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    )
    return response


def test_register_and_login_happy_path(client):
    register = register_user(client, "Admin User", "admin@example.com", "Admin123!", "ADMIN")
    assert register.status_code == 200
    payload = register.json()
    assert payload["token"]["access_token"]

    login = client.post("/auth/login", json={"email": "admin@example.com", "password": "Admin123!"})
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "ADMIN"


def test_protected_route_denied_without_token(client):
    response = client.get("/dashboard/kpis")
    assert response.status_code == 401


def test_role_mismatch_access_denied(client):
    register_user(client, "Sales User", "sales@example.com", "Sales123!", "SALES")
    login = client.post("/auth/login", json={"email": "sales@example.com", "password": "Sales123!"})
    token = login.json()["token"]["access_token"]

    response = client.get("/dashboard/kpis", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
