from datetime import date, timedelta


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_resident_creation_and_assignment(client, seed_ids, token_factory):
    token = token_factory(seed_ids["admin_id"], "admin")
    payload = {
        "name": "سارة",
        "phone": "+966500123456",
        "email": "sara@example.com",
        "unit_no": "5A",
        "start_date": date.today().isoformat(),
    }
    response = client.post("/residents", headers=_auth_header(token), json=payload)
    assert response.status_code == 201
    resident = response.json()
    assert resident["unit_no"] == "5A"
    assign = client.post(
        f"/residents/{resident['id']}/assign-unit",
        headers=_auth_header(token),
        params={"unit_no": "6B"},
    )
    assert assign.status_code == 200
    assert assign.json()["unit_no"] == "6B"


def test_subscription_and_invoice_generation(client, seed_ids, token_factory):
    token = token_factory(seed_ids["admin_id"], "admin")
    payload = {
        "resident_id": seed_ids["resident_id"],
        "type": "water",
        "plan": "مميز",
        "cycle": "monthly",
        "unit_price": 210.5,
        "next_due": date.today().isoformat(),
        "active": True,
    }
    sub_resp = client.post("/subscriptions", headers=_auth_header(token), json=payload)
    assert sub_resp.status_code == 201
    gen_resp = client.post(
        "/invoices/generate",
        headers=_auth_header(token),
        json={"target_date": date.today().isoformat()},
    )
    assert gen_resp.status_code == 200
    assert gen_resp.json()["created"] >= 1


def test_invoice_payment_mock(client, seed_ids, token_factory):
    token = token_factory(seed_ids["supervisor_user_id"], "supervisor")
    response = client.post(
        f"/invoices/{seed_ids['invoice_id']}/pay-mock",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "paid"


def test_reminder_job_marks_overdue(client, seed_ids, token_factory):
    token = token_factory(seed_ids["admin_id"], "admin")
    overdue_due = (date.today() - timedelta(days=3)).isoformat()
    create_invoice = client.post(
        "/invoices",
        headers=_auth_header(token),
        json={
            "resident_id": seed_ids["resident_id"],
            "subscription_id": seed_ids["subscription_id"],
            "amount": 120.0,
            "due_date": overdue_due,
        },
    )
    assert create_invoice.status_code == 201
    run_resp = client.post("/ops/run-reminders", headers=_auth_header(token))
    assert run_resp.status_code == 200
    result = run_resp.json()
    assert result["overdue_invoices"] >= 1


def test_maintenance_ticket_assign(client, seed_ids, token_factory):
    token = token_factory(seed_ids["admin_id"], "admin")
    create_resp = client.post(
        "/maintenance",
        headers=_auth_header(token),
        json={
            "asset_id": seed_ids["asset_id"],
            "title": "تنظيف الخزان",
            "description": "تنظيف دوري",
            "priority": "medium",
            "due_date": (date.today() + timedelta(days=4)).isoformat(),
        },
    )
    assert create_resp.status_code == 201
    ticket_id = create_resp.json()["id"]
    assign = client.post(
        f"/maintenance/{ticket_id}/assign/{seed_ids['supervisor_id']}",
        headers=_auth_header(token),
    )
    assert assign.status_code == 200
    assert assign.json()["assigned_to"] == seed_ids["supervisor_id"]
