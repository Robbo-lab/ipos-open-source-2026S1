from tests.mcp.conftest import parse_mcp_response


def test_initialise_server(mcp_url, mcp_headers, http_client, protocol_version):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": protocol_version,
            "capabilities": {},
            "clientInfo": {"name": "pytest", "version": "1.0"},
        },
    }

    response = http_client.post(mcp_url, json=payload, headers=mcp_headers)

    assert response.status_code in {200, 202}
    assert response.headers.get("mcp-session-id")
    body = parse_mcp_response(response)
    print(f"[test_initialise_server] status_code={response.status_code}")
    print(f"[test_initialise_server] headers={dict(response.headers)}")
    print(f"[test_initialise_server] body={body}")
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == 1
    assert "result" in body
    assert "serverInfo" in body["result"]


def test_initialized_notification(mcp_client):
    response = mcp_client.notification("notifications/initialized")

    print(f"[test_initialized_notification] status_code={response.status_code}")
    print(f"[test_initialized_notification] headers={dict(response.headers)}")
    print(f"[test_initialized_notification] text={response.text!r}")
    assert response.status_code in {200, 202, 204}
