def test_streaming_response(mcp_url, mcp_headers, http_client, protocol_version):
    headers = dict(mcp_headers)
    headers["Accept"] = "text/event-stream, application/json"

    payload = {
        "jsonrpc": "2.0",
        "id": "stream-init",
        "method": "initialize",
        "params": {
            "protocolVersion": protocol_version,
            "capabilities": {},
            "clientInfo": {"name": "pytest-stream", "version": "1.0"},
        },
    }

    with http_client.stream("POST", mcp_url, json=payload, headers=headers) as response:
        assert response.status_code in {200, 202}
        content_type = response.headers.get("content-type", "")
        print(f"[test_streaming_response] status_code={response.status_code}")
        print(f"[test_streaming_response] headers={dict(response.headers)}")
        print(f"[test_streaming_response] content_type={content_type}")
        assert "event-stream" in content_type or "json" in content_type

        first_chunk = next(response.iter_text(), "")
        print(f"[test_streaming_response] first_chunk={first_chunk!r}")
        assert first_chunk is not None


def collect_sse_data_lines(response, max_lines: int = 20) -> list[str]:
    data_lines = []

    for line in response.iter_lines():
        if not line:
            continue
        if line.startswith("data:"):
            data_lines.append(line.removeprefix("data:").strip())
        if len(data_lines) >= max_lines:
            break

    return data_lines
