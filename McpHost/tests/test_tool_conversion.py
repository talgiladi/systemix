from mcp_host.models.tooling import DiscoveredTool
from mcp_host.services.tool_conversion import build_llm_tool_name, convert_tool_to_llm_format


def test_build_llm_tool_name_is_stable_and_bounded() -> None:
    name = build_llm_tool_name("Operations API", "Deploy-Service.Now")
    assert name.startswith("operations_api__deploy_service_now")
    assert len(name) <= 64


def test_convert_tool_to_openai_format_sets_strict_schema() -> None:
    tool = DiscoveredTool(
        llm_name="inventory__lookup_asset",
        original_name="lookup_asset",
        description="Look up an asset by id.",
        input_schema={
            "type": "object",
            "properties": {
                "asset_id": {
                    "type": "string",
                }
            },
            "required": ["asset_id"],
        },
        server_name="inventory",
        server_url="http://localhost:9001/mcp",
        server_description="Inventory tools",
    )

    converted = convert_tool_to_llm_format(tool, "openai")

    assert converted["type"] == "function"
    assert converted["strict"] is True
    assert converted["parameters"]["additionalProperties"] is False
