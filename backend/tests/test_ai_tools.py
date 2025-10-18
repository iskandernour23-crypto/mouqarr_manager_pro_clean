import pytest


def test_execute_action_admin(client, seed_ids, token_factory):
    token = token_factory(seed_ids["admin_id"], "admin")
    response = client.post(
        "/ai/actions/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "summary_today", "params": {}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "summary_today"
    assert body["result"]["status"] == "ok"
    assert "invoices_due_today" in body["result"]


def test_execute_action_forbidden(client, seed_ids, token_factory):
    token = token_factory(seed_ids["resident_user_id"], "resident")
    response = client.post(
        "/ai/actions/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "pay_invoice", "params": {"invoice_id": seed_ids["invoice_id"]}},
    )
    assert response.status_code == 403
