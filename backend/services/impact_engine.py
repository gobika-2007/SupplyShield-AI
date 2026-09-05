import json
from pathlib import Path
from datetime import date


# ---------------------------------------------------------
# PATH
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "supply_chain.json"


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(value):
    if value is None:
        return ""

    return " ".join(str(value).strip().lower().split())


def priority_rank(priority):
    ranks = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }

    return ranks.get(normalize(priority), 5)


def add_evidence(evidence, source_type, source_id, field, value):
    evidence.append({
        "source_type": source_type,
        "source_id": source_id,
        "field": field,
        "value": value
    })


# ---------------------------------------------------------
# MAIN IMPACT ENGINE
# ---------------------------------------------------------

def analyze_impact(
    supplier_name=None,
    product_name=None,
    carrier_name=None,
    warehouse_name=None,
    no_impact_signal=False
):

    data = load_data()

    # -----------------------------------------------------
    # EXPLICIT NO-IMPACT SIGNAL
    # -----------------------------------------------------

    if no_impact_signal:
        return {
            "severity": "NO IMPACT",
            "status": "NO CURRENT IMPACT",
            "reason": (
                "The disruption notice explicitly states that "
                "the disruption does not affect pending "
                "shipments or customer orders."
            ),
            "affected_products": [],
            "affected_shipments": [],
            "affected_inventory": [],
            "orders": [],
            "total_shortage": 0,
            "evidence": [],
            "review_reasons": []
        }

    # -----------------------------------------------------
    # INPUT NORMALIZATION
    # -----------------------------------------------------

    supplier_query = normalize(supplier_name)
    product_query = normalize(product_name)
    carrier_query = normalize(carrier_name)
    warehouse_query = normalize(warehouse_name)

    evidence = []
    review_reasons = []

    # -----------------------------------------------------
    # SUPPLIER MATCHING
    # -----------------------------------------------------

    matched_supplier = None

    if supplier_query:

        for supplier in data.get("suppliers", []):

            if normalize(supplier.get("name")) == supplier_query:
                matched_supplier = supplier
                break

        if matched_supplier is None:

            return {
                "severity": "HUMAN REVIEW",
                "status": "REVIEW REQUIRED",
                "reason": (
                    "The supplier mentioned in the disruption "
                    "notice could not be matched to the known "
                    "supply-chain data."
                ),
                "affected_products": [],
                "affected_shipments": [],
                "affected_inventory": [],
                "orders": [],
                "total_shortage": 0,
                "evidence": [],
                "review_reasons": [
                    f"Unknown supplier: {supplier_name}"
                ]
            }

        add_evidence(
            evidence,
            "supplier",
            matched_supplier.get("supplier_id"),
            "name",
            matched_supplier.get("name")
        )

    # -----------------------------------------------------
    # CARRIER MATCHING
    # -----------------------------------------------------

    matched_carrier = None

    if carrier_query:

        for shipment in data.get("shipments", []):

            shipment_carrier = normalize(
                shipment.get("carrier_name")
            )

            if shipment_carrier == carrier_query:
                matched_carrier = carrier_name
                break

        if matched_carrier is None:

            return {
                "severity": "HUMAN REVIEW",
                "status": "REVIEW REQUIRED",
                "reason": (
                    "The carrier mentioned in the disruption "
                    "notice could not be matched to the known "
                    "supply-chain data."
                ),
                "affected_products": [],
                "affected_shipments": [],
                "affected_inventory": [],
                "orders": [],
                "total_shortage": 0,
                "evidence": [],
                "review_reasons": [
                    f"Unknown carrier: {carrier_name}"
                ]
            }

    # -----------------------------------------------------
    # WAREHOUSE MATCHING
    # -----------------------------------------------------

    matched_warehouse = None

    if warehouse_query:

        for warehouse in data.get("warehouses", []):

            warehouse_name_value = normalize(
                warehouse.get("name")
            )

            if warehouse_name_value == warehouse_query:
                matched_warehouse = warehouse
                break

        if matched_warehouse is None:

            return {
                "severity": "HUMAN REVIEW",
                "status": "REVIEW REQUIRED",
                "reason": (
                    "The warehouse mentioned in the disruption "
                    "notice could not be matched to the known "
                    "supply-chain data."
                ),
                "affected_products": [],
                "affected_shipments": [],
                "affected_inventory": [],
                "orders": [],
                "total_shortage": 0,
                "evidence": [],
                "review_reasons": [
                    f"Unknown warehouse: {warehouse_name}"
                ]
            }

        add_evidence(
            evidence,
            "warehouse",
            matched_warehouse.get("warehouse_id"),
            "name",
            matched_warehouse.get("name")
        )

    # -----------------------------------------------------
    # PRODUCT MATCHING
    # -----------------------------------------------------

    matched_product = None

    if product_query:

        for product in data.get("products", []):

            product_name_value = normalize(
                product.get("name")
            )

            if product_name_value == product_query:
                matched_product = product
                break

        if matched_product is None:

            return {
                "severity": "HUMAN REVIEW",
                "status": "REVIEW REQUIRED",
                "reason": (
                    "The product mentioned in the disruption "
                    "notice could not be matched to the known "
                    "supply-chain data."
                ),
                "affected_products": [],
                "affected_shipments": [],
                "affected_inventory": [],
                "orders": [],
                "total_shortage": 0,
                "evidence": [],
                "review_reasons": [
                    f"Unknown product: {product_name}"
                ]
            }

        add_evidence(
            evidence,
            "product",
            matched_product.get("product_id"),
            "name",
            matched_product.get("name")
        )

    # -----------------------------------------------------
    # FIND AFFECTED PRODUCT IDS
    # -----------------------------------------------------

    affected_product_ids = set()

    # Specific product takes highest priority
    if matched_product:

        affected_product_ids.add(
            matched_product.get("product_id")
        )

    # Supplier-only disruption
    elif matched_supplier:

        supplier_id = matched_supplier.get("supplier_id")

        for product in data.get("products", []):

            if product.get("supplier_id") == supplier_id:

                affected_product_ids.add(
                    product.get("product_id")
                )

    # Carrier disruption
    elif matched_carrier:

        for shipment in data.get("shipments", []):

            if (
                normalize(shipment.get("carrier_name"))
                == carrier_query
                and normalize(shipment.get("status"))
                != "delivered"
            ):

                affected_product_ids.add(
                    shipment.get("product_id")
                )

    # Warehouse disruption
    elif matched_warehouse:

        warehouse_id = matched_warehouse.get("warehouse_id")

        for inventory in data.get("inventory", []):

            if inventory.get("warehouse_id") == warehouse_id:

                affected_product_ids.add(
                    inventory.get("product_id")
                )

    # -----------------------------------------------------
    # FIND AFFECTED SHIPMENTS
    # -----------------------------------------------------

    affected_shipments = []

    for shipment in data.get("shipments", []):

        shipment_status = normalize(
            shipment.get("status")
        )

        # Delivered shipments are not operationally affected
        if shipment_status == "delivered":
            continue

        shipment_product_id = shipment.get(
            "product_id"
        )

        shipment_supplier_id = shipment.get(
            "supplier_id"
        )

        shipment_carrier = normalize(
            shipment.get("carrier_name")
        )

        shipment_matches = False

        # Supplier mapping
        if matched_supplier:

            if shipment_supplier_id == matched_supplier.get(
                "supplier_id"
            ):
                shipment_matches = True

        # Product mapping
        if matched_product:

            if shipment_product_id == matched_product.get(
                "product_id"
            ):
                shipment_matches = True

        # Carrier mapping
        if matched_carrier:

            if shipment_carrier == carrier_query:
                shipment_matches = True

        # Warehouse mapping
        #
        # Current shipment data does not necessarily contain
        # warehouse_id, so we safely check only when available.
        if matched_warehouse:

            shipment_warehouse_id = shipment.get(
                "warehouse_id"
            )

            if (
                shipment_warehouse_id
                == matched_warehouse.get("warehouse_id")
            ):
                shipment_matches = True

        if shipment_matches:

            affected_shipments.append(shipment)

            affected_product_ids.add(
                shipment_product_id
            )

            add_evidence(
                evidence,
                "shipment",
                shipment.get("shipment_id"),
                "product_id",
                shipment_product_id
            )

    # -----------------------------------------------------
    # FIND AFFECTED INVENTORY
    # -----------------------------------------------------

    affected_inventory = []

    for inventory in data.get("inventory", []):

        inventory_product_id = inventory.get(
            "product_id"
        )

        inventory_warehouse_id = inventory.get(
            "warehouse_id"
        )

        inventory_matches = False

        # Product match
        if inventory_product_id in affected_product_ids:
            inventory_matches = True

        # Warehouse match
        if matched_warehouse:

            if (
                inventory_warehouse_id
                == matched_warehouse.get("warehouse_id")
            ):
                inventory_matches = True

        if inventory_matches:

            affected_inventory.append(inventory)

            add_evidence(
                evidence,
                "inventory",
                inventory.get("inventory_id"),
                "quantity",
                inventory.get("quantity")
            )

    # -----------------------------------------------------
    # FIND AFFECTED ORDERS
    # -----------------------------------------------------

    affected_orders = []

    for order in data.get("orders", []):

        order_product_id = order.get("product_id")

        if order_product_id in affected_product_ids:

            affected_orders.append(order)

            add_evidence(
                evidence,
                "order",
                order.get("order_id"),
                "quantity",
                order.get("quantity")
            )

    # -----------------------------------------------------
    # NO CURRENT IMPACT
    # -----------------------------------------------------

    if (
        len(affected_shipments) == 0
        and len(affected_orders) == 0
    ):

        return {
            "severity": "NO IMPACT",
            "status": "NO CURRENT IMPACT",
            "reason": (
                "The disruption was mapped to the known "
                "supply-chain data, but no pending shipments "
                "or customer orders are currently affected."
            ),
            "affected_products": [],
            "affected_shipments": [],
            "affected_inventory": affected_inventory,
            "orders": [],
            "total_shortage": 0,
            "evidence": evidence,
            "review_reasons": []
        }

    # -----------------------------------------------------
    # AVAILABLE STOCK
    # -----------------------------------------------------

    available_stock = {}

    for inventory in affected_inventory:

        product_id = inventory.get("product_id")

        quantity = inventory.get(
            "quantity",
            0
        )

        reserved_quantity = inventory.get(
            "reserved_quantity",
            0
        )

        available_stock[product_id] = (
            available_stock.get(product_id, 0)
            + max(
                0,
                quantity - reserved_quantity
            )
        )

    # -----------------------------------------------------
    # ORDER PRIORITY
    # -----------------------------------------------------

    affected_orders.sort(
        key=lambda order: (
            priority_rank(
                order.get("priority")
            ),
            order.get("deadline", "")
        )
    )

    # -----------------------------------------------------
    # CALCULATE SHORTAGE
    # -----------------------------------------------------

    remaining_stock = dict(
        available_stock
    )

    order_results = []
    total_shortage = 0

    for order in affected_orders:

        product_id = order.get(
            "product_id"
        )

        required_quantity = order.get(
            "quantity",
            0
        )

        available_quantity = remaining_stock.get(
            product_id,
            0
        )

        allocated_quantity = min(
            available_quantity,
            required_quantity
        )

        shortage = (
            required_quantity
            - allocated_quantity
        )

        remaining_stock[product_id] = max(
            0,
            available_quantity - allocated_quantity
        )

        result = {
            **order,
            "available_stock": available_quantity,
            "allocated_stock": allocated_quantity,
            "shortage": shortage,
            "risk": "AT RISK" if shortage > 0 else "COVERED"
        }

        order_results.append(result)

        total_shortage += shortage

    # -----------------------------------------------------
    # SEVERITY
    # -----------------------------------------------------

    critical_orders = [
        order
        for order in order_results
        if normalize(order.get("priority"))
        == "critical"
        and order.get("shortage", 0) > 0
    ]

    high_orders = [
        order
        for order in order_results
        if normalize(order.get("priority"))
        == "high"
        and order.get("shortage", 0) > 0
    ]

    medium_orders = [
        order
        for order in order_results
        if normalize(order.get("priority"))
        == "medium"
        and order.get("shortage", 0) > 0
    ]

    if critical_orders:

        severity = "CRITICAL"

    elif high_orders:

        severity = "HIGH"

    elif medium_orders:

        severity = "MEDIUM"

    else:

        severity = "LOW"

    # -----------------------------------------------------
    # AFFECTED PRODUCT DETAILS
    # -----------------------------------------------------

    affected_products = []

    for product in data.get("products", []):

        if product.get("product_id") in affected_product_ids:

            affected_products.append(product)

    # -----------------------------------------------------
    # REASON
    # -----------------------------------------------------

    at_risk_orders = [
        order
        for order in order_results
        if order.get("shortage", 0) > 0
    ]

    if at_risk_orders:

        reason = (
            f"{len(at_risk_orders)} customer order(s) "
            f"are at risk with a total calculated shortage "
            f"of {total_shortage} unit(s)."
        )

    else:

        reason = (
            f"{len(affected_shipments)} pending shipment(s) "
            "are affected, but current customer demand is "
            "covered by available stock."
        )

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {
        "severity": severity,
        "status": "IMPACT IDENTIFIED",
        "reason": reason,
        "affected_products": affected_products,
        "affected_shipments": affected_shipments,
        "affected_inventory": affected_inventory,
        "orders": order_results,
        "total_shortage": total_shortage,
        "evidence": evidence,
        "review_reasons": review_reasons
    }