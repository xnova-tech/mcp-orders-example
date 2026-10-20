"""Check the fixed catalog without network access or third-party packages."""

import json
from pathlib import Path


ROOT = Path(__file__).parent
EXPECTED = {"ORD-101": 380, "ORD-102": 900}


def main() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert requirements == ["mcp==2.3.0", "pydantic==2.13.5"], requirements

    orders = json.loads((ROOT / "orders.json").read_text(encoding="utf-8"))
    totals = {
        order["id"]: sum(item["quantity"] * item["unit_price"] for item in order["items"])
        for order in orders
    }
    assert totals == EXPECTED, totals
    print("catalog checks passed")


if __name__ == "__main__":
    main()
