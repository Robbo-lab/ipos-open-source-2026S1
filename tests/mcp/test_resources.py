from tests.mcp.conftest import parse_mcp_response


def test_resources_list(mcp_client):
    response = mcp_client.rpc("resources/list", {}, id=20)
    assert response.status_code == 200  # noqa: PLR2004

    body = parse_mcp_response(response)
    resources = body["result"]["resources"]
    print(f"[test_resources_list] status_code={response.status_code}")
    print(f"[test_resources_list] body={body}")
    print(f"[test_resources_list] resources={resources}")
    uris = {resource["uri"] for resource in resources}
    assert any("unit_reference" in uri for uri in uris)


# TODO
def test_resource_unit_reference(mcp_client):
    pass
