def test_malformed_jsonrpc_request(mcp_url, mcp_headers, http_client):
    response = http_client.post(
        mcp_url,
        json={"id": 99, "params": {}},
        headers=mcp_headers,
    )

    assert response.status_code in {200, 400, 422}
    body = response.json()
    print(f"[test_malformed_jsonrpc_request] status_code={response.status_code}")
    print(f"[test_malformed_jsonrpc_request] body={body}")
    assert "error" in body or response.status_code in {400, 422}
