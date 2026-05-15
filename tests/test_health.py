def test_server_health(base_url, http_client):
    response = http_client.get(f"{base_url}/health")

    assert response.status_code == 200  # noqa: PLR2004
    body = response.json()
    print(f"[test_server_health] status_code={response.status_code}")
    print(f"[test_server_health] body={body}")
    assert body["status"] == "ok"
    assert "python" in body
    assert "uptime_seconds" in body
