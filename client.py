"""List and call both MCP tools using a local stdio process."""
import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


SERVER = Path(__file__).with_name("server.py")


async def run() -> None:
    parameters = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with Client(parameters) as client:
        response = await client.list_tools()
        names = {tool.name for tool in response.tools}
        assert names == {"get_order", "calculate_order_total"}, names
        print("tools:", ", ".join(sorted(names)))

        order = await client.call_tool("get_order", {"order_id": "ORD-101"})
        assert not order.is_error, order.content
        assert order.structured_content is not None
        assert order.structured_content["id"] == "ORD-101"
        assert len(order.structured_content["items"]) == 2
        print("order: ORD-101, items: 2")

        total = await client.call_tool(
            "calculate_order_total", {"order_id": "ORD-101"}
        )
        assert not total.is_error, total.content
        assert total.structured_content is not None
        assert total.structured_content["total"] == 380
        print("total: 380")


if __name__ == "__main__":
    asyncio.run(run())
