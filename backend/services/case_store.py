import json
from pathlib import Path

CASES_FILE = Path("data/cases.json")


def load_cases():
    if not CASES_FILE.exists():
        return []

    try:
        with open(CASES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_case(case_id, extracted, impact, action_plan):
    cases = load_cases()

    case = {
        "case_id": case_id,
        "extracted": extracted,
        "impact": impact,
        "action_plan": action_plan
    }

    cases.append(case)

    CASES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(CASES_FILE, "w", encoding="utf-8") as file:
        json.dump(cases, file, indent=2)


def get_all_cases():
    return load_cases()


def get_case_by_id(case_id):
    cases = load_cases()

    for case in cases:
        if case.get("case_id") == case_id:
            return case

    return None