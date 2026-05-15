from tests.mcp.conftest import parse_mcp_response


def test_prompts_list(mcp_client):
    response = mcp_client.rpc("prompts/list", {}, id=10)
    assert response.status_code == 200  # noqa: PLR2004

    body = parse_mcp_response(response)
    prompts = body["result"]["prompts"]
    print(f"[test_prompts_list] status_code={response.status_code}")
    print(f"[test_prompts_list] body={body}")
    print(f"[test_prompts_list] prompts={prompts}")
    names = {prompt["name"] for prompt in prompts}
    assert "explain_conversion" in names
    assert "api_usage" in names


# Example prompt - TODO
def test_prompt_explain_conversion(mcp_client):
    pass
