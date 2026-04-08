def register_and_login(client, name, email, role):
    client.post("/auth/register", json={"name": name, "email": email, "password": "Pass123!", "role": role})
    login = client.post("/auth/login", json={"email": email, "password": "Pass123!"})
    token = login.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_lead_and_opportunity_crud(client):
    admin_headers = register_and_login(client, "Admin", "admin2@example.com", "ADMIN")

    lead = client.post(
        "/leads",
        json={"name": "Lead One", "email": "lead1@example.com", "source": "website"},
        headers=admin_headers,
    )
    assert lead.status_code == 201
    lead_id = lead.json()["id"]

    leads = client.get("/leads", headers=admin_headers)
    assert leads.status_code == 200
    assert len(leads.json()) == 1

    opp = client.post(
        "/opportunities",
        json={"lead_id": lead_id, "deal_value": 10000, "stage": "CLOSED_WON", "probability": 0.9, "expected_close_date": "2026-01-15"},
        headers=admin_headers,
    )
    assert opp.status_code == 201

    kpis = client.get("/dashboard/kpis", headers=admin_headers)
    assert kpis.status_code == 200
    body = kpis.json()
    assert "total_leads" in body
    assert "conversion_rate" in body
    assert "total_revenue" in body
    assert "pipeline_stage_distribution" in body
    assert "lead_source_performance" in body

    trend = client.get("/dashboard/revenue-trend", headers=admin_headers)
    assert trend.status_code == 200
    assert trend.json()[0]["month"] == "2026-01"
