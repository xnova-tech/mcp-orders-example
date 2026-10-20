"""End-to-end MCP smoke checks, including invalid tool calls.

Run from the project root: python test_orders.py
"""
import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


SERVER = Path(__file__).with_name("server.py")
TOOLS = {"get_order", "calculate_order_total"}


def require_success(result, *, description: str):
    assert not result.is_error, f"{description}: {result.content}"
    assert result.structured_content is not None, f"{description}: missing structured content"
    return result.structured_content


def require_tool_error(result, *, description: str) -> None:
    assert result.is_error, f"{description}: incorrectly succeeded"
    assert result.structured_content is None, f"{description}: error returned data"
    assert result.content, f"{description}: no error information"


async def check() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with Client(params) as client:
        catalog = await client.list_tools()
        by_name = {tool.name: tool for tool in catalog.tools}
        assert set(by_name) == TOOLS, f"Unexpected tools: {set(by_name)}"

        # Discovery must expose a required string parameter, not only a name.
        for name in TOOLS:
            schema = by_name[name].input_schema
            assert schema["properties"]["order_id"]["type"] == "string", schema
            assert "order_id" in schema["required"], schema

        for order_id, expected_items, expected_total in [
            ("ORD-101", 2, 380),
            ("ORD-102", 1, 900),
        ]:
            order = require_success(
                await client.call_tool("get_order", {"order_id": order_id}),
                description=f"get_order({order_id})",
            )
            assert order["id"] == order_id, order
            assert len(order["items"]) == expected_items, order

            total = require_success(
                await client.call_tool("calculate_order_total", {"order_id": order_id}),
                description=f"calculate_order_total({order_id})",
            )
            assert total == {"order_id": order_id, "total": expected_total}, total

        # Domain errors: well-formed string IDs that the catalog cannot resolve.
        for name in TOOLS:
            require_tool_error(
                await client.call_tool(name, {"order_id": "ORD-999"}),
                description=f"{name}: missing order",
            )
            require_tool_error(
                await client.call_tool(name, {"order_id": "../secrets"}),
                description=f"{name}: invalid ID",
            )

        # Protocol/SDK input validation: reject missing and wrongly typed arguments.
        for name in TOOLS:
            require_tool_error(
                await client.call_tool(name, {}),
                description=f"{name}: missing order_id",
            )
            require_tool_error(
                await client.call_tool(name, {"order_id": 123}),
                description=f"{name}: numeric order_id",
            )

        require_tool_error(
            await client.call_tool("no_such_tool", {"order_id": "ORD-101"}),
            description="unknown tool name",
        )
        # A rejected call must not close the stdio connection.
        recovered = require_success(
            await client.call_tool("get_order", {"order_id": "ORD-101"}),
            description="get_order after rejected calls",
        )
        assert recovered["id"] == "ORD-101", recovered
    print("smoke checks passed")


if __name__ == "__main__":
    asyncio.run(check())
