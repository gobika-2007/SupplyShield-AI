def build_action_plan(impact):
    """
    Build a deterministic action plan from the calculated impact.
    The system recommends actions but never executes them automatically.
    """

    severity = impact.get("severity", "LOW")
    orders = impact.get("orders", [])
    total_shortage = impact.get("total_shortage", 0)
    affected_shipments = impact.get("affected_shipments", [])

    critical_orders = [
        order for order in orders
        if order.get("priority", "").lower() == "critical"
        and order.get("shortage", 0) > 0
    ]

    high_priority_orders = [
        order for order in orders
        if order.get("priority", "").lower() == "high"
        and order.get("shortage", 0) > 0
    ]

    at_risk_orders = [
        order for order in orders
        if order.get("shortage", 0) > 0
    ]

    # ---------------------------------------------------------
    # NO IMPACT
    # ---------------------------------------------------------
    if severity == "NO IMPACT":
        return {
            "recommendation": "NO ACTION REQUIRED",
            "reason": "No current customer or shipment impact was identified.",
            "total_shortage": 0,
            "critical_orders": 0,
            "high_priority_orders": 0,
            "actions": [],
            "options": [],
            "requires_human_approval": False
        }

    # ---------------------------------------------------------
    # HUMAN REVIEW
    # ---------------------------------------------------------
    if severity == "HUMAN REVIEW":
        return {
            "recommendation": "ESCALATE FOR HUMAN REVIEW",
            "reason": impact.get(
                "reason",
                "The disruption could not be reliably mapped."
            ),
            "total_shortage": total_shortage,
            "critical_orders": len(critical_orders),
            "high_priority_orders": len(high_priority_orders),
            "actions": [
                {
                    "action": "HUMAN_REVIEW",
                    "description": "Validate the disruption details and affected entities.",
                    "priority": "Immediate"
                }
            ],
            "options": [],
            "requires_human_approval": True
        }

    # ---------------------------------------------------------
    # OPTION 1 — EXPEDITE
    # ---------------------------------------------------------
    expedite_option = {
        "action": "EXPEDITE",
        "title": "Expedite replacement or delayed supply",
        "benefit": "Fastest way to recover the shortage.",
        "tradeoff": "Higher transportation or supplier-expediting cost.",
        "best_for": "Critical and high-priority orders",
        "recommended": True
    }

    # ---------------------------------------------------------
    # OPTION 2 — REALLOCATE
    # ---------------------------------------------------------
    reallocate_option = {
        "action": "REALLOCATE",
        "title": "Reallocate available stock",
        "benefit": "Uses existing inventory instead of waiting for new supply.",
        "tradeoff": "May reduce stock available for another customer or warehouse.",
        "best_for": "Situations with available stock elsewhere",
        "recommended": False
    }

    # ---------------------------------------------------------
    # OPTION 3 — PART SHIP
    # ---------------------------------------------------------
    part_ship_option = {
        "action": "PART_SHIP",
        "title": "Part-ship affected orders",
        "benefit": "Allows customers to receive available units immediately.",
        "tradeoff": "The order remains partially unfulfilled.",
        "best_for": "Orders where partial fulfillment is acceptable",
        "recommended": False
    }

    # ---------------------------------------------------------
    # OPTION 4 — PRIORITIZE
    # ---------------------------------------------------------
    prioritize_option = {
        "action": "PRIORITIZE",
        "title": "Prioritize critical orders",
        "benefit": "Protects the most time-sensitive customer commitments.",
        "tradeoff": "Lower-priority orders may experience additional delay.",
        "best_for": "Multiple orders competing for limited stock",
        "recommended": bool(critical_orders)
    }

    # ---------------------------------------------------------
    # OPTION 5 — NOTIFY
    # ---------------------------------------------------------
    notify_option = {
        "action": "NOTIFY_CUSTOMERS",
        "title": "Notify affected customers",
        "benefit": "Provides transparent communication about expected delays.",
        "tradeoff": "Does not directly resolve the physical shortage.",
        "best_for": "Orders that cannot meet their deadlines",
        "recommended": bool(at_risk_orders)
    }

    # ---------------------------------------------------------
    # OPTION 6 — WAIT
    # ---------------------------------------------------------
    wait_option = {
        "action": "WAIT",
        "title": "Wait for the original supply",
        "benefit": "Avoids additional emergency logistics cost.",
        "tradeoff": "Higher risk of missing customer deadlines.",
        "best_for": "Low-priority orders with sufficient deadline buffer",
        "recommended": False
    }

    options = [
        expedite_option,
        reallocate_option,
        part_ship_option,
        prioritize_option,
        notify_option,
        wait_option
    ]

    # ---------------------------------------------------------
    # PRIMARY RECOMMENDATION
    # ---------------------------------------------------------

    if critical_orders and total_shortage > 0:
        recommendation = "EXPEDITE + PRIORITIZE CRITICAL ORDERS"

        reason = (
            f"{len(critical_orders)} critical order(s) and "
            f"{len(high_priority_orders)} high-priority order(s) "
            f"are exposed, with a total shortage of "
            f"{total_shortage} unit(s). Expedite recovery supply "
            f"while protecting critical commitments first."
        )

    elif high_priority_orders and total_shortage > 0:
        recommendation = "EXPEDITE + PRIORITIZE HIGH-PRIORITY ORDERS"

        reason = (
            f"{len(high_priority_orders)} high-priority order(s) "
            f"are exposed with a total shortage of "
            f"{total_shortage} unit(s). Expediting is recommended "
            f"to reduce the probability of deadline failure."
        )

    elif total_shortage > 0:
        recommendation = "PART-SHIP + NOTIFY AFFECTED CUSTOMERS"

        reason = (
            f"{len(at_risk_orders)} order(s) have a calculated "
            f"shortage of {total_shortage} unit(s). Part-shipping "
            f"available stock can reduce immediate customer impact."
        )

    else:
        recommendation = "MONITOR AFFECTED SHIPMENTS"

        reason = (
            f"{len(affected_shipments)} pending shipment(s) are affected, "
            f"but current customer demand is covered by available stock."
        )

    # ---------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------

    actions = []

    if critical_orders:
        actions.append({
            "action": "PRIORITIZE_CRITICAL",
            "description": (
                f"Protect {len(critical_orders)} critical order(s) "
                "before lower-priority demand."
            ),
            "priority": "Immediate"
        })

    if total_shortage > 0:
        actions.append({
            "action": "EXPEDITE",
            "description": (
                f"Identify replacement or expedited supply for "
                f"{total_shortage} shortage unit(s)."
            ),
            "priority": "Immediate"
        })

        actions.append({
            "action": "PART_SHIP",
            "description": (
                "Evaluate partial fulfillment using currently "
                "available stock."
            ),
            "priority": "High"
        })

        actions.append({
            "action": "REALLOCATE",
            "description": (
                "Check other warehouses or available stock sources "
                "for possible reallocation."
            ),
            "priority": "High"
        })

    if at_risk_orders:
        actions.append({
            "action": "NOTIFY_CUSTOMERS",
            "description": (
                f"Prepare communication for {len(at_risk_orders)} "
                "at-risk customer order(s)."
            ),
            "priority": "High"
        })

    actions.append({
        "action": "HUMAN_APPROVAL",
        "description": (
            "Obtain human approval before executing shipment, "
            "reallocation, or customer-communication actions."
        ),
        "priority": "Required"
    })

    return {
        "recommendation": recommendation,
        "reason": reason,
        "total_shortage": total_shortage,
        "critical_orders": len(critical_orders),
        "high_priority_orders": len(high_priority_orders),
        "actions": actions,
        "options": options,
        "requires_human_approval": True
    }