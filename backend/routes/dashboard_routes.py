import json
from pathlib import Path

from fastapi import APIRouter

from backend.services.case_store import get_all_cases


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

DATA_FILE = Path("data/supply_chain.json")


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@router.get("")
def get_dashboard():

    data = load_data()

    suppliers = data.get("suppliers", [])
    products = data.get("products", [])
    warehouses = data.get("warehouses", [])
    shipments = data.get("shipments", [])
    inventory = data.get("inventory", [])
    orders = data.get("orders", [])

    # -----------------------------------------------------
    # ACTIVE SHIPMENTS
    # -----------------------------------------------------

    active_shipments = [
        shipment
        for shipment in shipments
        if shipment.get("status") != "Delivered"
    ]

    # -----------------------------------------------------
    # ORDERS BY PRIORITY
    # -----------------------------------------------------

    critical_orders = [
        order
        for order in orders
        if order.get("priority") == "Critical"
    ]

    high_priority_orders = [
        order
        for order in orders
        if order.get("priority") == "High"
    ]

    # -----------------------------------------------------
    # INVENTORY
    # -----------------------------------------------------

    total_stock = sum(
        item.get("quantity", 0)
        for item in inventory
    )

    total_reserved = sum(
        item.get("reserved_quantity", 0)
        for item in inventory
    )

    available_stock = (
        total_stock - total_reserved
    )

    # -----------------------------------------------------
    # CASE HISTORY
    # -----------------------------------------------------

    cases = get_all_cases()

    active_disruptions = len(cases)

    orders_at_risk = 0
    stock_at_risk = 0
    suppliers_impacted = set()

    recent_cases = []

    for case in cases:

        impact = case.get("impact", {})

        # Count orders currently at risk
        at_risk_orders = impact.get(
            "orders",
            []
        )

        orders_at_risk += len(
            [
                order
                for order in at_risk_orders
                if order.get("risk") == "AT RISK"
            ]
        )

        # Total shortage
        stock_at_risk += impact.get(
            "total_shortage",
            0
        )

        # Impacted suppliers
        affected_products = impact.get(
            "affected_products",
            []
        )

        for product in affected_products:

            supplier_name = product.get(
                "supplier_name"
            )

            if supplier_name:
                suppliers_impacted.add(
                    supplier_name
                )

        recent_cases.append({
            "case_id": case.get("case_id"),
            "severity": impact.get(
                "severity",
                "UNKNOWN"
            ),
            "total_shortage": impact.get(
                "total_shortage",
                0
            )
        })

    # -----------------------------------------------------
    # RETURN DASHBOARD DATA
    # -----------------------------------------------------

    return {

        "status": "success",

        "summary": {

            "active_disruptions":
                active_disruptions,

            "orders_at_risk":
                orders_at_risk,

            "stock_at_risk":
                stock_at_risk,

            "suppliers_impacted":
                len(suppliers_impacted),

            "active_shipments":
                len(active_shipments),

            "critical_orders":
                len(critical_orders),

            "high_priority_orders":
                len(high_priority_orders)
        },

        "supply_chain": {

            "suppliers":
                len(suppliers),

            "products":
                len(products),

            "warehouses":
                len(warehouses),

            "shipments":
                len(shipments),

            "inventory_records":
                len(inventory),

            "orders":
                len(orders)
        },

        "inventory": {

            "total_stock":
                total_stock,

            "reserved_stock":
                total_reserved,

            "available_stock":
                available_stock
        },

        "recent_shipments":
            active_shipments[:5],

        "priority_orders":
            critical_orders[:5]
            + high_priority_orders[:5],

        "recent_cases":
            recent_cases[-5:]
    }