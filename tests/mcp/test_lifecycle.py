from tests.mcp.conftest import build_mcp_test_client


def test_initialise_server(mcp_url, mcp_headers, http_client, protocol_version):
    client = build_mcp_test_client(
        http_client,
        mcp_url,
        headers=mcp_headers,
        protocol_version=protocol_version,
    )

    assert client.session_id is not None
    assert "Mcp-Session-Id" in client.headers

    print(f"[test_initialise_server] headers={dict(client.headers)}")
    print(f"[test_initialise_server] session_id={client.session_id}")


def test_initialized_notification(mcp_client):
    response = mcp_client.notification("notifications/initialized")

    print(f"[test_initialized_notification] status_code={response.status_code}")
    print(f"[test_initialized_notification] headers={dict(response.headers)}")
    print(f"[test_initialized_notification] text={response.text!r}")
    assert response.status_code in {200, 202, 204}
