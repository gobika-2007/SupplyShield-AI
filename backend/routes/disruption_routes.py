from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.gemini_extractor import (
    extract_disruption_notice
)

from backend.services.impact_engine import (
    analyze_impact
)

from backend.services.action_planner import (
    build_action_plan
)

from backend.services.case_store import (
    save_case
)


router = APIRouter(
    prefix="/api/disruption",
    tags=["Disruption Analysis"]
)


# =========================================================
# REQUEST MODEL
# =========================================================

class DisruptionRequest(BaseModel):

    notice: str


# =========================================================
# ANALYZE DISRUPTION
# =========================================================

@router.post("/analyze")
def analyze_disruption(
    request: DisruptionRequest
):

    # =====================================================
    # VALIDATE INPUT
    # =====================================================

    if not request.notice.strip():

        raise HTTPException(
            status_code=400,
            detail="Disruption notice cannot be empty."
        )

    try:

        # =================================================
        # STEP 1 — GEMINI EXTRACTION
        # =================================================

        extracted = extract_disruption_notice(
            request.notice
        )

        # =================================================
        # STEP 2 — EXTRACT MAPPED ENTITIES
        # =================================================

        supplier_name = (
            extracted.get("supplier_name")
            or None
        )

        carrier_name = (
            extracted.get("carrier_name")
            or None
        )

        warehouse_name = (
            extracted.get("warehouse_name")
            or None
        )

        product_names = (
            extracted.get("product_names", [])
        )

        product_codes = (
            extracted.get("product_codes", [])
        )

        affected_shipments = (
            extracted.get("affected_shipments", [])
        )

        disruption_type = (
            extracted.get("disruption_type", "")
        )

        no_impact_signal = (
            extracted.get(
                "no_impact_signal",
                False
            )
        )

        # =================================================
        # STEP 3 — PRODUCT
        # =================================================

        product_name = None

        if product_names:

            product_name = product_names[0]

        # =================================================
        # STEP 4 — DETERMINISTIC IMPACT ENGINE
        # =================================================

        impact = analyze_impact(
    supplier_name=supplier_name,
    product_name=product_name,
    carrier_name=carrier_name,
    warehouse_name=warehouse_name,
    no_impact_signal=extracted.get("no_impact_signal", False)
)

        # =================================================
        # STEP 5 — ADD DISRUPTION METADATA
        # =================================================

        impact["disruption_type"] = (
            disruption_type
        )

        impact["mapped_entities"] = {

            "supplier_name":
                supplier_name,

            "carrier_name":
                carrier_name,

            "warehouse_name":
                warehouse_name,

            "product_names":
                product_names,

            "product_codes":
                product_codes,

            "affected_shipments":
                affected_shipments
        }

        # =================================================
        # STEP 6 — ACTION PLANNER
        # =================================================

        action_plan = build_action_plan(
            impact
        )

        # =================================================
        # STEP 7 — CASE ID
        # =================================================

        case_id = (
            "CASE-"
            + datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )
        )

        # =================================================
        # STEP 8 — SAVE CASE
        # =================================================

        save_case(
            case_id,
            extracted,
            impact,
            action_plan
        )

        # =================================================
        # STEP 9 — RESPONSE
        # =================================================

        return {

            "status": "success",

            "case_id": case_id,

            "notice": request.notice,

            "extracted": extracted,

            "impact": impact,

            "action_plan": action_plan,

            "traceability": {

                "supplier":
                    supplier_name,

                "carrier":
                    carrier_name,

                "warehouse":
                    warehouse_name,

                "products":
                    product_names,

                "product_codes":
                    product_codes,

                "shipments":
                    affected_shipments
            }
        }

    # =====================================================
    # EXPECTED VALIDATION ERROR
    # =====================================================

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # =====================================================
    # UNEXPECTED ERROR
    # =====================================================

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(error)}"
        )