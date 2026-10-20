"""Local read-only orders MCP server (mcp==2.3.0)."""
import json
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field


DATA = Path(__file__).with_name("orders.json")
mcp = MCPServer("LocalOrders")


class LineItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)
    unit_price: int = Field(ge=0)


class Order(BaseModel):
    id: str
    items: list[LineItem]


class Total(BaseModel):
    order_id: str
    total: int


def find_order(order_id: str) -> Order:
    """Only look up records in the fixed demonstration catalog."""
    if not order_id.startswith("ORD-") or len(order_id) > 32:
        raise ToolError("Invalid order ID")
    orders = json.loads(DATA.read_text(encoding="utf-8"))
    for record in orders:
        if record["id"] == order_id:
            return Order.model_validate(record)
    raise ToolError("Order not found")


@mcp.tool()
def get_order(order_id: str) -> Order:
    """Return an order from the local catalog."""
    return find_order(order_id)


@mcp.tool()
def calculate_order_total(order_id: str) -> Total:
    """Calculate the total of order line items."""
    order = find_order(order_id)
    return Total(
        order_id=order.id,
        total=sum(item.quantity * item.unit_price for item in order.items),
    )


if __name__ == "__main__":
    mcp.run()
