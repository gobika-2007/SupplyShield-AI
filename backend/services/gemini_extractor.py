import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "supply_chain.json"


def load_supply_chain_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def local_fallback_extraction(notice: str, reason: str = ""):
    """
    Deterministic fallback used when Gemini is unavailable,
    quota exhausted, or returns invalid output.
    """

    data = load_supply_chain_data()
    text = notice.lower()

    suppliers = data.get("suppliers", [])
    products = data.get("products", [])
    warehouses = data.get("warehouses", [])
    shipments = data.get("shipments", [])

    supplier_name = ""
    carrier_name = ""
    warehouse_name = ""
    product_names = []
    product_codes = []
    affected_shipments = []

    # -----------------------------
    # Match suppliers
    # -----------------------------
    for supplier in suppliers:
        name = supplier.get("name", "")
        if name and name.lower() in text:
            supplier_name = name
            break

    # -----------------------------
    # Match products
    # -----------------------------
    for product in products:
        name = product.get("name", "")
        code = product.get("product_id", "")

        if name and name.lower() in text:
            product_names.append(name)
            if code:
                product_codes.append(code)

        elif code and code.lower() in text:
            product_codes.append(code)
            if name:
                product_names.append(name)

    # -----------------------------
    # Match warehouses
    # -----------------------------
    for warehouse in warehouses:
        name = warehouse.get("name", "")
        if name and name.lower() in text:
            warehouse_name = name
            break

    # -----------------------------
    # Match carriers from shipments
    # -----------------------------
    for shipment in shipments:
        carrier = shipment.get("carrier_name", "")

        if carrier and carrier.lower() in text:
            carrier_name = carrier
            break

    # -----------------------------
    # Match shipment IDs
    # -----------------------------
    for shipment in shipments:
        shipment_id = shipment.get("shipment_id", "")

        if shipment_id and shipment_id.lower() in text:
            affected_shipments.append(shipment_id)

    # -----------------------------
    # Detect disruption type
    # -----------------------------
    disruption_type = "unknown disruption"

    if "flood" in text:
        disruption_type = "flooding incident"
    elif "fire" in text:
        disruption_type = "fire incident"
    elif "production halt" in text:
        disruption_type = "production halt"
    elif "production stopped" in text:
        disruption_type = "production halt"
    elif "production stop" in text:
        disruption_type = "production halt"
    elif "factory" in text and ("shutdown" in text or "closed" in text):
        disruption_type = "factory shutdown"
    elif "carrier delay" in text or "transport delay" in text:
        disruption_type = "carrier delay"
    elif "delay" in text:
        disruption_type = "delivery delay"
    elif "warehouse" in text:
        disruption_type = "warehouse incident"
    elif "equipment failure" in text or "machinery failure" in text:
        disruption_type = "equipment failure"

    # -----------------------------
    # Duration
    # -----------------------------
    duration_days = ""

    duration_match = re.search(
        r"(\d+)\s*(?:day|days|d)",
        text
    )

    if duration_match:
        duration_days = duration_match.group(1)

    # -----------------------------
    # Explicit NO IMPACT detection
    # -----------------------------
    no_impact_patterns = [
        "does not affect any pending shipment",
        "does not affect pending shipments",
        "does not affect any customer order",
        "does not affect customer orders",
        "no customer orders are affected",
        "no pending shipments are affected",
        "not part of any pending shipment",
        "unrelated to current orders",
        "unrelated to customer orders",
        "unrelated to current customer orders",
        "does not affect any active customer order",
        "no active customer order is affected",
    ]

    no_impact_signal = any(
        phrase in text for phrase in no_impact_patterns
    )

    # -----------------------------
    # Severity language
    # -----------------------------
    severity_language = ""

    severity_keywords = [
        "critical",
        "severe",
        "major",
        "urgent",
        "temporarily suspended",
        "completely stopped",
        "halt",
        "shutdown",
        "flood",
        "fire",
    ]

    for keyword in severity_keywords:
        if keyword in text:
            severity_language = keyword
            break

    # -----------------------------
    # Match shipments using supplier/product/carrier
    # -----------------------------
    if supplier_name or product_names or product_codes or carrier_name:

        for shipment in shipments:
            supplier_match = (
                supplier_name
                and shipment.get("supplier_id", "").lower()
                in [
                    s.get("supplier_id", "").lower()
                    for s in suppliers
                    if s.get("name", "").lower() == supplier_name.lower()
                ]
            )

            product_match = False

            if product_names:
                for product in products:
                    if (
                        product.get("name", "").lower()
                        in [p.lower() for p in product_names]
                        and shipment.get("product_id", "").lower()
                        == product.get("product_id", "").lower()
                    ):
                        product_match = True

            if product_codes:
                if shipment.get("product_id", "").lower() in [
                    p.lower() for p in product_codes
                ]:
                    product_match = True

            carrier_match = (
                carrier_name
                and shipment.get("carrier_name", "").lower()
                == carrier_name.lower()
            )

            if supplier_match or product_match or carrier_match:
                shipment_id = shipment.get("shipment_id")

                if shipment_id and shipment_id not in affected_shipments:
                    affected_shipments.append(shipment_id)

    # -----------------------------
    # Facts
    # -----------------------------
    raw_facts = []

    if supplier_name:
        raw_facts.append(f"Supplier identified: {supplier_name}")

    if product_names:
        raw_facts.append(
            f"Product identified: {', '.join(product_names)}"
        )

    if carrier_name:
        raw_facts.append(f"Carrier identified: {carrier_name}")

    if warehouse_name:
        raw_facts.append(f"Warehouse identified: {warehouse_name}")

    if duration_days:
        raw_facts.append(
            f"Duration mentioned: {duration_days} days"
        )

    if affected_shipments:
        raw_facts.append(
            f"Shipment references: {', '.join(affected_shipments)}"
        )

    uncertain_fields = []

    if not supplier_name and not carrier_name and not warehouse_name and not product_names:
        uncertain_fields.append("business_entity")

    if disruption_type == "unknown disruption":
        uncertain_fields.append("disruption_type")

    return {
        "disruption_type": disruption_type,
        "supplier_name": supplier_name,
        "carrier_name": carrier_name,
        "warehouse_name": warehouse_name,
        "product_names": product_names,
        "product_codes": product_codes,
        "affected_shipments": affected_shipments,
        "start_date": "",
        "duration_days": duration_days,
        "expected_end_date": "",
        "severity_language": severity_language,
        "raw_facts": raw_facts,
        "uncertain_fields": uncertain_fields,
        "no_impact_signal": no_impact_signal,
        "extraction_source": "LOCAL FALLBACK",
        "fallback_reason": reason,
    }


def extract_disruption_notice(notice: str):

    if not notice or not notice.strip():
        raise ValueError("Disruption notice cannot be empty.")

    # ==========================================================
    # Try Gemini first
    # ==========================================================

    if client:

        prompt = f"""
You are a supply-chain disruption extraction system.

Extract ONLY facts explicitly present in the disruption notice.

IMPORTANT:
- Do not invent supplier names.
- Do not invent product names.
- Do not invent shipment IDs.
- Preserve exact names.
- If something is unknown, return an empty string/list.
- Return ONLY valid JSON.

Notice:
{notice}

Return this exact JSON structure:

{{
  "disruption_type": "",
  "supplier_name": "",
  "carrier_name": "",
  "warehouse_name": "",
  "product_names": [],
  "product_codes": [],
  "affected_shipments": [],
  "start_date": "",
  "duration_days": "",
  "expected_end_date": "",
  "severity_language": "",
  "raw_facts": [],
  "uncertain_fields": [],
  "no_impact_signal": false
}}

Set no_impact_signal to true ONLY when the notice explicitly says that
pending shipments, customer orders, or active commitments are NOT affected.

Examples:
- "no customer orders are affected"
- "does not affect any pending shipments"
- "unrelated to current orders"

Do NOT infer no impact just because IDs are missing.
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            raw_text = response.text.strip()

            # Remove markdown JSON fences if Gemini returns them
            raw_text = raw_text.replace("```json", "")
            raw_text = raw_text.replace("```", "")
            raw_text = raw_text.strip()

            result = json.loads(raw_text)

            # Ensure required fields exist
            defaults = {
                "disruption_type": "",
                "supplier_name": "",
                "carrier_name": "",
                "warehouse_name": "",
                "product_names": [],
                "product_codes": [],
                "affected_shipments": [],
                "start_date": "",
                "duration_days": "",
                "expected_end_date": "",
                "severity_language": "",
                "raw_facts": [],
                "uncertain_fields": [],
                "no_impact_signal": False,
            }

            for key, default in defaults.items():
                if key not in result:
                    result[key] = default

            # Make sure list fields are actually lists
            for key in [
                "product_names",
                "product_codes",
                "affected_shipments",
                "raw_facts",
                "uncertain_fields",
            ]:
                if not isinstance(result[key], list):
                    result[key] = []

            result["no_impact_signal"] = bool(
                result.get("no_impact_signal", False)
            )

            result["extraction_source"] = "GEMINI"

            return result

        except Exception as exc:

            # ==================================================
            # Gemini failed → LOCAL FALLBACK
            # ==================================================

            return local_fallback_extraction(
                notice,
                reason=str(exc)
            )

    # ==========================================================
    # No Gemini key → LOCAL FALLBACK
    # ==========================================================

    return local_fallback_extraction(
        notice,
        reason="GEMINI_API_KEY not configured"
    )