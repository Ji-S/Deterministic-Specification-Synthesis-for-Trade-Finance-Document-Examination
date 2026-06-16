"""BL Clause Generator - Generate clauses and GT from Bill of Lading data"""

import json
import os
import random
import re
from typing import Any, Dict, List, Tuple

from .templates import (
    CLEAN_AND_BOARD_TEMPLATES,
    CONSIGNEE_TEMPLATES,
    DATE_OF_ISSUE_TEMPLATES,
    DELIVERY_TEMPLATES,
    DESTINATION_TEMPLATES,
    DOC_TYPE_TEMPLATES,
    FREIGHT_TERMS_TEMPLATES,
    NOTIFY_OPTIONAL_TEMPLATES,
    NOTIFY_TEMPLATES,
    ORIGINALS_TEMPLATES,
    ROUTE_TEMPLATES,
    SHIPMENT_DATE_TEMPLATES,
    SIGNED_DOC_TYPE_TEMPLATES,
)
from .constants import (
    # Originals related
    ORIGINALS_3_3_OPTIONS,
    ORIGINALS_SUFFIX_OPTIONS,
    ORIGINALS_IGNORE_VALUES,
    # Probability values
    PROB_CLEAN_ON_BOARD,
    PROB_CONSIGNEE,
    PROB_FREIGHT,
    PROB_NOTIFY,
    PROB_NOTIFY_NAME_ONLY,
    PROB_NOTIFY_OPTIONAL,
    PROB_ROUTE_WITH_POD,
    PROB_ROUTE_POL_ONLY,
    PROB_DELIVERY,
    PROB_SHIPMENT_DATE,
    PROB_DATE_OF_ISSUE,
    PROB_CONSIGNEE_WITH_ADDRESS,
    # Consignee related
    CONSIGNEE_ISSUING_BANK,
    CONSIGNEE_DRAWEE_BANK,
    CONSIGNEE_ISSUING_BANK_KEYWORDS,
    CONSIGNEE_DRAWEE_BANK_KEYWORDS,
    # Notify related
    NOTIFY_SAME_AS_CONSIGNEE,
    NOTIFY_SAME_AS_CONSIGNEE_VALUE,
    NOTIFY_TYPE_APPLICANT,
    NOTIFY_TYPE_APPLICANT_WITH_ADDRESS,
    NOTIFY_WITH_ADDRESS_KEYWORD,
    # Template filtering
    SHOWING_KEYWORD,
    # Route related
    ROUTE_POL_ONLY_TEMPLATE,
    # Delivery related
    DELIVERY_KEYWORDS,
    DESTINATION_KEYWORD,
    # Regex patterns
    TEL_FAX_PATTERN,
    ENTITY_PARSE_PATTERN,
    NOTIFY_PARSE_PATTERN,
)


def build_head(bl_data: dict) -> Tuple[str, bool]:
    """
    Build HEAD section (originals + clean_on_board + doc_type)
    
    Args:
        bl_data: BL extraction data
        
    Returns:
        Tuple of (head_text, signed_used)
    """
    parts = []
    signed_used = False
    
    # 1. ORIGINALS (based on number_of_documents)
    number_of_documents = bl_data.get("number_of_documents", "")
    
    # If number_of_documents is ZERO, empty, or 0, don't use ORIGINALS template
    if any(ignore in number_of_documents for ignore in ORIGINALS_IGNORE_VALUES) or not number_of_documents:
        pass
    elif "3/3" == number_of_documents.replace(" ", ""):
        # "3/3" format: select from predefined options
        originals = random.choice(ORIGINALS_3_3_OPTIONS)
        parts.append(originals)
    else:
        # Others: use "{n}/{n} ORIGINAL", "{n} ORIGINAL"
        optional = random.choice(ORIGINALS_SUFFIX_OPTIONS)
        originals = number_of_documents + optional
        parts.append(originals)
    
    # 2. CLEAN ON BOARD
    # Condition: (clean_wording is true or adverse_remarks is null) AND (on_board_notation is not null or on_board_date is not null)
    clean_wording = bl_data.get("clean_wording", False)
    adverse_remarks = bl_data.get("adverse_remarks")
    on_board_notation = bl_data.get("on_board_notation")
    on_board_date = bl_data.get("on_board_date")
    
    condition_1 = clean_wording or (adverse_remarks is None or adverse_remarks == "")
    condition_2 = (on_board_notation is not None and on_board_notation != "") or (on_board_date is not None and on_board_date != "")
    
    if condition_1 and condition_2 and random.random() < PROB_CLEAN_ON_BOARD:
        clean_on_board = random.choice(CLEAN_AND_BOARD_TEMPLATES)
        parts.append(clean_on_board)
    
    # 3. DOC TYPE (required)
    doc_types = DOC_TYPE_TEMPLATES.copy()
    # Add SIGNED BILLS OF LADING if signed exists
    if bl_data.get("signed", ""):
        doc_types.extend(SIGNED_DOC_TYPE_TEMPLATES)
    doc_type = random.choice(doc_types)
    if "SIGNED" in doc_type:
        signed_used = True
    parts.append(doc_type)
    
    return " ".join(parts), signed_used


def _clean_contact_info(text: str) -> str:
    """Remove phone/fax information"""
    return re.sub(TEL_FAX_PATTERN, '', text, flags=re.IGNORECASE).strip()


def build_consignee(bl_data: dict, avoid_showing: bool = False) -> str:
    """
    Build CONSIGNEE section
    
    Args:
        bl_data: BL extraction data
        avoid_showing: Whether to avoid SHOWING templates
        
    Returns:
        Generated consignee string
    """
    consignee = bl_data.get("consignee", "")
    if not consignee:
        return ""
    
    # If consignee is dict format (name, address separated)
    if isinstance(consignee, dict):
        consignee_name = consignee.get("name", "")
        consignee_address = consignee.get("address", "")
        # Probabilistically use name only or name + address
        if consignee_address and random.random() >= (1 - PROB_CONSIGNEE_WITH_ADDRESS):
            consignee_full = f"{consignee_name} {consignee_address}"
        else:
            consignee_full = consignee_name
    else:
        # String format: use name + address only (exclude phone/fax)
        consignee_full = _clean_contact_info(consignee)
    
    # If avoid_showing is True, exclude SHOWING templates
    templates = CONSIGNEE_TEMPLATES
    if avoid_showing:
        templates = [t for t in CONSIGNEE_TEMPLATES if SHOWING_KEYWORD not in t]
    
    template = random.choice(templates)
    return template.format(consignee=consignee_full)


def build_notify(bl_data: dict, avoid_showing: bool = False, is_same_as_consignee: bool = False) -> str:
    """
    Build NOTIFY PARTY section
    
    Args:
        bl_data: BL extraction data
        avoid_showing: Whether to avoid SHOWING templates
        is_same_as_consignee: Whether it's SAME AS CONSIGNEE
        
    Returns:
        Generated notify string
    """
    # Special case for "SAME AS CONSIGNEE"
    if is_same_as_consignee:
        return NOTIFY_SAME_AS_CONSIGNEE
    
    notify_party = bl_data.get("notify_party", "")
    if not notify_party:
        return ""
    
    # If notify_party is dict format (name, address separated)
    if isinstance(notify_party, dict):
        notify_name = notify_party.get("name", "")
        notify_address = notify_party.get("address", "")
        # Probabilistically use name only or name + address
        if notify_address and random.random() >= PROB_NOTIFY_NAME_ONLY:
            notify_full = f"{notify_name} {notify_address}"
            has_address = True
        else:
            notify_full = notify_name
            has_address = False
    else:
        # String format: use name + address only (exclude phone/fax)
        notify_full = _clean_contact_info(notify_party)
        has_address = len(notify_full.split()) > 3
    
    # Exclude "SAME AS CONSIGNEE" from templates
    templates = [t for t in NOTIFY_TEMPLATES if NOTIFY_SAME_AS_CONSIGNEE_VALUE not in t]
    
    # If avoid_showing is True, exclude SHOWING templates
    if avoid_showing:
        templates = [t for t in templates if SHOWING_KEYWORD not in t]
    
    template = random.choice(templates)
    
    if "{notify_party}" in template:
        # Template with {notify_party}: use name + address only, no optional
        return template.format(notify_party=notify_full)
    else:
        # Template without {notify_party}: "NOTIFY APPLICANT", "APPLICANT TO BE NOTIFIED"
        result = template
        if has_address and random.random() < PROB_NOTIFY_OPTIONAL:
            optional = random.choice(NOTIFY_OPTIONAL_TEMPLATES)
            result += f" {optional}"
        return result


def build_freight(bl_data: dict, avoid_showing: bool = False) -> str:
    """
    Build FREIGHT TERMS section
    
    Args:
        bl_data: BL extraction data
        avoid_showing: Whether to avoid SHOWING templates
        
    Returns:
        Generated freight string
    """
    freight_terms = bl_data.get("freight_terms", "")
    if not freight_terms:
        return ""
    
    templates = FREIGHT_TERMS_TEMPLATES
    
    # If avoid_showing is True, exclude SHOWING templates
    if avoid_showing:
        templates = [t for t in templates if SHOWING_KEYWORD not in t]
    
    template = random.choice(templates)
    return template.format(FREIGHT_TERMS=freight_terms)


def build_route(bl_data: dict, force_pod: bool = False) -> str:
    """
    Build ROUTE (POL/POD) section
    
    Args:
        bl_data: BL extraction data
        force_pod: Whether to use only POD-including templates
        
    Returns:
        Generated route string
    """
    pol = bl_data.get("port_of_loading", "")
    pod = bl_data.get("port_of_discharge", "")
    
    if not pol and not pod:
        return ""
    
    # If only pol exists, use short template
    if pol and not pod:
        return ROUTE_POL_ONLY_TEMPLATE.format(pol=pol)
    
    # If both pol and pod exist, use template that includes pod
    if force_pod:
        templates = [t for t in ROUTE_TEMPLATES if "{pod}" in t]
    else:
        templates = ROUTE_TEMPLATES
    
    template = random.choice(templates)
    
    if "{pod}" in template:
        return template.format(pol=pol, pod=pod)
    else:
        return template.format(pol=pol)


def build_delivery(bl_data: dict) -> str:
    """
    Build DELIVERY section
    
    Args:
        bl_data: BL extraction data
        
    Returns:
        Generated delivery string
    """
    delivery = bl_data.get("place_of_delivery", "")
    destination = bl_data.get("final_destination", "")
    
    if not delivery and not destination:
        return ""
    
    parts = []
    if delivery:
        template = random.choice(DELIVERY_TEMPLATES)
        parts.append(template.format(delivery=delivery))
    if destination:
        template = random.choice(DESTINATION_TEMPLATES)
        parts.append(template.format(destination=destination))
    
    return "\n".join(parts)


def build_shipment_date(bl_data: dict) -> str:
    """
    Build SHIPMENT DATE section
    
    Args:
        bl_data: BL extraction data
        
    Returns:
        Generated shipment_date string
    """
    on_board_date = bl_data.get("on_board_date", "")
    if not on_board_date:
        return ""
    
    template = random.choice(SHIPMENT_DATE_TEMPLATES)
    return template.format(on_board_date=on_board_date)


def build_date_of_issue(bl_data: dict) -> str:
    """
    Build DATE OF ISSUE section
    
    Args:
        bl_data: BL extraction data
        
    Returns:
        Generated date_of_issue string
    """
    date_of_issue = bl_data.get("date_of_issue", "")
    if not date_of_issue:
        return ""
    
    template = random.choice(DATE_OF_ISSUE_TEMPLATES)
    return template.format(date_of_issue=date_of_issue)


def _extract_consignee_name(item_text: str) -> str:
    """Extract company name from consignee item"""
    match = re.search(ENTITY_PARSE_PATTERN, item_text)
    return match.group(1).strip() if match else ""


def _extract_notify_name(item_text: str) -> str:
    """Extract company name from notify item"""
    match = re.search(NOTIFY_PARSE_PATTERN, item_text)
    return match.group(1).strip() if match else ""


def build_requirement_with_gt(bl_data: dict) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generate 46a requirement text and GT (JSON list) from JSON BL data
    
    Args:
        bl_data: BL extraction data (dict)
        
    Returns:
        Tuple of (requirement text, GT list)
    """
    lines = []
    gt_list = []
    
    # 1. Build HEAD
    number_of_documents = bl_data.get("number_of_documents", "")
    head_text, signed_used = build_head(bl_data)
    lines.append(head_text)
    
    # 2. Prepare CORE items
    core_candidates = []
    used_consignee = None
    used_notify = None
    used_freight = None
    used_route = None
    used_delivery = None
    used_shipment_date = None
    consignee_used = False
    notify_used = False
    freight_used = False
    
    if bl_data.get("consignee", "") and random.random() < PROB_CONSIGNEE:
        consignee_text = build_consignee(bl_data)
        core_candidates.append(('consignee', consignee_text))
    
    if bl_data.get("freight_terms", "") and random.random() < PROB_FREIGHT:
        freight_text = build_freight(bl_data)
        core_candidates.append(('freight', freight_text))
    
    # Handle notify_party - check if SAME AS CONSIGNEE
    is_same_as_consignee = bl_data.get("is_same_as_consignee", False)
    
    # If SAME AS CONSIGNEE, always add; otherwise probabilistically
    should_add_notify = is_same_as_consignee or (bl_data.get("notify_party", "") and random.random() < PROB_NOTIFY)
    if should_add_notify:
        notify_text = build_notify(bl_data, is_same_as_consignee=is_same_as_consignee)
        core_candidates.append(('notify', notify_text))
    
    # Shuffle CORE items
    random.shuffle(core_candidates)
    
    # Handle SHOWING to be used only once
    showing_used = False
    for item_type, item_text in core_candidates:
        if SHOWING_KEYWORD in item_text and showing_used:
            # If SHOWING is already used and this item also has SHOWING, replace
            if item_type == 'consignee':
                item_text = build_consignee(bl_data, avoid_showing=True)
            elif item_type == 'freight':
                item_text = build_freight(bl_data, avoid_showing=True)
            elif item_type == 'notify':
                item_text = build_notify(bl_data, avoid_showing=True, is_same_as_consignee=is_same_as_consignee)
        
        if SHOWING_KEYWORD in item_text:
            showing_used = True
        lines.append(item_text)
        
        # Extract actual used info from each item
        if item_type == 'consignee':
            consignee_used = True
            # Check ORDER OF ISSUING BANK / DRAWEE BANK
            if any(kw in item_text for kw in CONSIGNEE_ISSUING_BANK_KEYWORDS):
                used_consignee = CONSIGNEE_ISSUING_BANK
            elif any(kw in item_text for kw in CONSIGNEE_DRAWEE_BANK_KEYWORDS):
                used_consignee = CONSIGNEE_DRAWEE_BANK
            else:
                used_consignee = _extract_consignee_name(item_text)
        elif item_type == 'freight':
            freight_used = True
            used_freight = bl_data.get("freight_terms", "")
        elif item_type == 'notify':
            notify_used = True
            if is_same_as_consignee:
                used_notify = NOTIFY_SAME_AS_CONSIGNEE_VALUE
            elif NOTIFY_TYPE_APPLICANT in item_text:
                if NOTIFY_WITH_ADDRESS_KEYWORD in item_text:
                    used_notify = NOTIFY_TYPE_APPLICANT_WITH_ADDRESS
                else:
                    used_notify = NOTIFY_TYPE_APPLICANT
            elif NOTIFY_SAME_AS_CONSIGNEE_VALUE in item_text:
                used_notify = NOTIFY_SAME_AS_CONSIGNEE_VALUE
            else:
                used_notify = _extract_notify_name(item_text)
    
    # 3. TAIL (maintain order)
    pol = bl_data.get("port_of_loading", "")
    pod = bl_data.get("port_of_discharge", "")
    
    # If pod exists, add probabilistically; if only pol, add probabilistically
    should_add_route = False
    force_pod = False
    
    if pod and random.random() < PROB_ROUTE_WITH_POD:
        should_add_route = True
        force_pod = True
    elif pol and random.random() < PROB_ROUTE_POL_ONLY:
        should_add_route = True
    
    if should_add_route:
        route_text = build_route(bl_data, force_pod=force_pod)
        lines.append(route_text)
        used_route = {
            "port_of_loading": pol,
            "port_of_discharge": pod
        }
        
        # delivery: add probabilistically if place_of_delivery/final_destination exists
        if (bl_data.get("place_of_delivery", "") or bl_data.get("final_destination", "")) and random.random() < PROB_DELIVERY:
            delivery_text = build_delivery(bl_data)
            lines.append(delivery_text)
            used_delivery = {
                "place_of_delivery": bl_data.get("place_of_delivery", ""),
                "final_destination": bl_data.get("final_destination", "")
            }
    
    # shipment_date: add probabilistically if on_board_date exists
    if bl_data.get("on_board_date", "") and random.random() < PROB_SHIPMENT_DATE:
        shipment_date_text = build_shipment_date(bl_data)
        lines.append(shipment_date_text)
        used_shipment_date = bl_data.get("on_board_date", "")
    
    # date_of_issue: add probabilistically if exists
    used_date_of_issue = ""
    if bl_data.get("date_of_issue", "") and random.random() < PROB_DATE_OF_ISSUE:
        date_of_issue_text = build_date_of_issue(bl_data)
        lines.append(date_of_issue_text)
        used_date_of_issue = bl_data.get("date_of_issue", "")
    
    # ========== Generate GT list (based on operator) ==========
    
    # 1. number_of_documents (include if not ZERO or 0)
    if number_of_documents and not any(ignore in number_of_documents for ignore in ORIGINALS_IGNORE_VALUES):
        gt_list.append({
            "key": "number_of_documents",
            "expected_value": number_of_documents,
            "operator": "GTE"
        })
    
    # 2. CLEAN set (only if actually included in generated_clause)
    head_text_upper = head_text.upper()
    clean_in_clause = "CLEAN" in head_text_upper
    on_board_in_clause = "ON BOARD" in head_text_upper or "SHIPPED ON BOARD" in head_text_upper
    
    if clean_in_clause:
        gt_list.append({
            "key": "clean_wording",
            "expected_value": True,
            "operator": "EXISTS"
        })
        gt_list.append({
            "key": "adverse_remarks",
            "expected_value": None,
            "operator": "NEGATION"
        })
    
    # 3. ON BOARD set (only if actually included in generated_clause)
    if on_board_in_clause:
        gt_list.append({
            "key": "on_board_notation",
            "expected_value": True,
            "operator": "EXISTS"
        })
        gt_list.append({
            "key": "exist_on_board_date",
            "expected_value": True,
            "operator": "EXISTS"
        })
    
    if used_shipment_date:
        gt_list.append({
            "key": "on_board_date",
            "expected_value": used_shipment_date,
            "operator": "LTE"
        })
    
    # 4. Consignee (only if actually used)
    if consignee_used:
        if used_consignee == CONSIGNEE_ISSUING_BANK:
            gt_list.append({
                "key": "consignee",
                "expected_value": CONSIGNEE_ISSUING_BANK,
                "operator": "EQUALS"
            })
        elif used_consignee == CONSIGNEE_DRAWEE_BANK:
            gt_list.append({
                "key": "consignee",
                "expected_value": CONSIGNEE_DRAWEE_BANK,
                "operator": "EQUALS"
            })
        else:
            original_consignee = bl_data.get("consignee", {})
            if isinstance(original_consignee, dict):
                consignee_name = original_consignee.get("name", "")
                consignee_address = original_consignee.get("address", "")
            else:
                consignee_name = original_consignee
                consignee_address = ""
            
            gt_list.append({
                "key": "consignee",
                "expected_value": consignee_name,
                "operator": "EQUALS"
            })
            if consignee_address and consignee_address.upper() in "\n".join(lines).upper():
                gt_list.append({
                    "key": "consignee_address",
                    "expected_value": consignee_address,
                    "operator": "CONTAINS"
                })
    
    # 5. Notify Party (only if actually used)
    if notify_used:
        if used_notify == NOTIFY_TYPE_APPLICANT:
            gt_list.append({
                "key": "notify_party",
                "expected_value": "$LC_APPLICANT",
                "operator": "EQUALS"
            })
        elif used_notify == NOTIFY_TYPE_APPLICANT_WITH_ADDRESS:
            gt_list.append({
                "key": "notify_party",
                "expected_value": "$LC_APPLICANT",
                "operator": "EQUALS"
            })
            gt_list.append({
                "key": "notify_party_address",
                "expected_value": "$LC_APPLICANT_ADDRESS",
                "operator": "CONTAINS"
            })
        elif used_notify == NOTIFY_SAME_AS_CONSIGNEE_VALUE:
            gt_list.append({
                "key": "notify_party",
                "expected_value": NOTIFY_SAME_AS_CONSIGNEE_VALUE,
                "operator": "EQUALS"
            })
        else:
            original_notify = bl_data.get("notify_party", "")
            if isinstance(original_notify, dict):
                notify_name = original_notify.get("name", "")
                notify_address = original_notify.get("address", "")
            else:
                notify_name = original_notify
                notify_address = ""
            
            if notify_name:
                gt_list.append({
                    "key": "notify_party",
                    "expected_value": notify_name,
                    "operator": "EQUALS"
                })
            if notify_address and notify_address.upper() in "\n".join(lines).upper():
                gt_list.append({
                    "key": "notify_party_address",
                    "expected_value": notify_address,
                    "operator": "CONTAINS"
                })
    
    # 6. Freight Terms (only if actually used)
    if freight_used:
        gt_list.append({
            "key": "freight_terms",
            "expected_value": used_freight,
            "operator": "CONTAINS"
        })
    
    # 7. Route (pol/pod) - only if actually used
    if used_route:
        if used_route.get("port_of_loading"):
            gt_list.append({
                "key": "port_of_loading",
                "expected_value": used_route["port_of_loading"],
                "operator": "EQUALS"
            })
        if used_route.get("port_of_discharge"):
            gt_list.append({
                "key": "port_of_discharge",
                "expected_value": used_route["port_of_discharge"],
                "operator": "EQUALS"
            })
    
    # 8. Delivery - only if actually used
    if used_delivery:
        delivery_text = "\n".join(lines)
        if used_delivery.get("place_of_delivery"):
            if any(kw in delivery_text for kw in DELIVERY_KEYWORDS):
                gt_list.append({
                    "key": "place_of_delivery",
                    "expected_value": used_delivery["place_of_delivery"],
                    "operator": "EQUALS"
                })
        if used_delivery.get("final_destination"):
            if DESTINATION_KEYWORD in delivery_text:
                gt_list.append({
                    "key": "final_destination",
                    "expected_value": used_delivery["final_destination"],
                    "operator": "EQUALS"
                })
    
    # 9. Signed (existence of signature)
    if signed_used:
        gt_list.append({
            "key": "signed",
            "expected_value": True,
            "operator": "EXISTS"
        })
    
    # 10. Date of Issue (only if actually used)
    if used_date_of_issue:
        gt_list.append({
            "key": "date_of_issue",
            "expected_value": used_date_of_issue,
            "operator": "LTE"
        })
    
    return "\n".join(lines), gt_list