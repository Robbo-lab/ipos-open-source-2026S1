EXPECTED_STATUS_CODE = 200
# Expected status code to avoid magic number

def test_root(base_url, http_client):
    """Verify root endpoint (/) works and returns results displaying available tools"""
    
    response = http_client.get(f"{base_url}/")

    assert response.status_code == EXPECTED_STATUS_CODE
    body = response.json()
    print(f"[test_root] status_code={response.status_code}")
    print(f"[test_root] body={body}")
    assert body["status"] == "ok"
    assert body["service"] == "unit-converter-mcp-server"
    assert "docs" in body
    assert "health" in body
    assert "mcp" in body
