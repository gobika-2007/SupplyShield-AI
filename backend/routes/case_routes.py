from fastapi import APIRouter, HTTPException

from backend.services.case_store import (
    get_all_cases,
    get_case_by_id
)


router = APIRouter(
    prefix="/api/cases",
    tags=["Case History"]
)


# =========================================================
# GET ALL CASES
# =========================================================

@router.get("")
def get_cases():
    cases = get_all_cases()

    return {
        "status": "success",
        "count": len(cases),
        "cases": cases
    }


# =========================================================
# GET SINGLE CASE
# =========================================================

@router.get("/{case_id}")
def get_case(case_id: str):

    case = get_case_by_id(case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    return {
        "status": "success",
        "case": case
    }