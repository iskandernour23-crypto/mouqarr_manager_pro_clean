def test_chat_returns_mock_response(client, seed_ids, token_factory):
    token = token_factory(seed_ids["admin_id"], "admin")
    response = client.post(
        "/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "messages": [
                {"role": "user", "content": "ما هي أحدث الدفعات؟"},
            ],
            "options": {"lang": "ar"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"]["role"] == "assistant"
    assert "تمت معالجة" in body["message"]["content"]
