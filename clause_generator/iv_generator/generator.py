"""Invoice Clause Generator - Generate clauses and GT from Invoice data"""

import random
from typing import Any, Dict, List, Tuple

from .templates import (
    BUYER_CONSIGNEE_TEMPLATES,
    BUYER_CONSIGNEE_WITH_VAL_TEMPLATES,
    CURRENCY_VAL_TEMPLATES,
    GOODS_DESC_TEMPLATES,
    HS_CODE_TEMPLATES,
    INV_NUM_ONLY_EXPLICIT_TEMPLATES,
    INVOICE_DATE_EXISTS_TEMPLATES,
    INVOICE_DATE_VAL_TEMPLATES,
    INVOICE_NUMBER_EXISTS_TEMPLATES,
    ISSUER_TEMPLATES,
    ISSUER_WITH_VAL_TEMPLATES,
    LC_AND_INVOICE_NUM_TEMPLATES,
    LC_NUM_ONLY_TEMPLATES,
    ORIGIN_EXIST_TEMPLATES,
    ORIGIN_VAL_TEMPLATES,
    TOTAL_AMOUNT_TEMPLATES,
    TRADE_TERMS_EXIST_TEMPLATES,
    TRADE_TERMS_VAL_TEMPLATES,
)
from .constants import (
    SENTENCE_CATEGORIES,
    CONNECTOR_SAME_CATEGORY,
    CONNECTOR_DIFF_CATEGORY,
    PROB_INVOICE_DATE_VAL,
    PROB_EXPORTER_LC_BENEFICIARY,
    PROB_EXPORTER_WITH_ADDRESS,
    PROB_PROCESS_EXPORTER,
    PROB_BUYER_LC_APPLICANT,
    PROB_BUYER_WITH_ADDRESS,
    PROB_PROCESS_BUYER,
    PROB_NUMBER_HANDLING,
    PROB_INVOICE_NUMBER_EXPLICIT,
    PROB_ORIGIN,
    PROB_ORIGIN_VAL,
    PROB_TRADE_TERMS,
    PROB_TRADE_TERMS_VAL,
    PROB_GOODS_DESC,
    PROB_TOTAL_AMOUNT,
)


def get_category(template_key: str) -> str:
    """Return category based on template key"""
    for category, keys in SENTENCE_CATEGORIES.items():
        if template_key in keys:
            return category
    return "other"


def build_natural_sentence(clause_blocks: List[str], template_keys_used: List[str]) -> str:
    """
    Build natural sentence
    - Same category items connected with commas
    - Different category items connected with AND
    - Convert entire sentence to uppercase
    """
    if not clause_blocks:
        return "COMMERCIAL INVOICE"

    final_clause = "COMMERCIAL INVOICE "
    final_clause += clause_blocks[0]
    prev_category = get_category(template_keys_used[0]) if template_keys_used else None

    for i in range(1, len(clause_blocks)):
        current_category = get_category(template_keys_used[i]) if i < len(template_keys_used) else None

        if current_category == prev_category and current_category is not None:
            connector = CONNECTOR_SAME_CATEGORY
        else:
            connector = CONNECTOR_DIFF_CATEGORY

        final_clause += connector + clause_blocks[i]
        prev_category = current_category

    return final_clause.upper()


def generate_iv_with_gt(iv_data: dict) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generate Commercial Invoice requirement text and GT from Invoice JSON data

    Args:
        iv_data: Invoice extraction data (dict)

    Returns:
        Tuple of (clause text, GT list)
    """
    clause_blocks = []
    gt_schema = []
    template_keys_used = []

    # [1] Handle Invoice Date
    invoice_date = iv_data.get("invoice_date")
    if invoice_date:
        if random.random() < PROB_INVOICE_DATE_VAL:
            template = random.choice(INVOICE_DATE_VAL_TEMPLATES)
            clause_blocks.append(template.format(val=invoice_date))
            gt_schema.append({
                "key": "invoice_date",
                "expected_value": invoice_date.upper() if isinstance(invoice_date, str) else invoice_date,
                "operator": "LTE"
            })
            template_keys_used.append("invoice_date_val")
        else:
            template = random.choice(INVOICE_DATE_EXISTS_TEMPLATES)
            clause_blocks.append(template)
            gt_schema.append({
                "key": "exist_invoice_date",
                "expected_value": True,
                "operator": "EXISTS"
            })
            template_keys_used.append("invoice_date_exists")

    # [2] Handle Exporter
    exporter = iv_data.get("exporter")
    if exporter and random.random() < PROB_PROCESS_EXPORTER:
        exporter_name = exporter.get("name", "") if isinstance(exporter, dict) else exporter
        if exporter_name:
            if random.random() < PROB_EXPORTER_LC_BENEFICIARY:
                # Use $LC_BENEFICIARY
                clause_blocks.append(random.choice(ISSUER_TEMPLATES))
                gt_schema.append({
                    "key": "exporter",
                    "expected_value": "$LC_BENEFICIARY",
                    "operator": "EQUALS"
                })
                template_keys_used.append("issuer")
            else:
                # Use actual exporter name
                template = random.choice(ISSUER_WITH_VAL_TEMPLATES)
                if isinstance(exporter, dict):
                    exporter_name = exporter.get("name", "")
                    exporter_address = exporter.get("address", "")
                    if exporter_name and exporter_address and random.random() < PROB_EXPORTER_WITH_ADDRESS:
                        exporter_val = f"{exporter_name}, {exporter_address}"
                        gt_schema.append({
                            "key": "exporter",
                            "expected_value": exporter_name.upper(),
                            "operator": "EQUALS"
                        })
                        gt_schema.append({
                            "key": "exporter_address",
                            "expected_value": exporter_address.upper(),
                            "operator": "CONTAINS"
                        })
                    else:
                        exporter_val = exporter_name
                        gt_schema.append({
                            "key": "exporter",
                            "expected_value": exporter_name.upper(),
                            "operator": "EQUALS"
                        })
                else:
                    exporter_val = exporter
                    gt_schema.append({
                        "key": "exporter",
                        "expected_value": exporter_val.upper(),
                        "operator": "EQUALS"
                    })
                clause_blocks.append(template.format(val=exporter_val))
                template_keys_used.append("issuer_")

    # [3] Handle Buyer/Consignee (buyer priority)
    buyer = iv_data.get("buyer")
    consignee = iv_data.get("consignee")
    buyer_val = buyer if buyer else consignee

    if buyer_val and random.random() < PROB_PROCESS_BUYER:
        buyer_name = buyer_val.get("name", "") if isinstance(buyer_val, dict) else buyer_val
        if buyer_name:
            if random.random() < PROB_BUYER_LC_APPLICANT:
                # Use $LC_APPLICANT
                clause_blocks.append(random.choice(BUYER_CONSIGNEE_TEMPLATES))
                gt_schema.append({
                    "key": "buyer/consignee",
                    "expected_value": "$LC_APPLICANT",
                    "operator": "EQUALS"
                })
                template_keys_used.append("buyer/consignee")
            else:
                # Use actual buyer name
                template = random.choice(BUYER_CONSIGNEE_WITH_VAL_TEMPLATES)
                if isinstance(buyer_val, dict):
                    buyer_name = buyer_val.get("name", "")
                    buyer_address = buyer_val.get("address", "")
                    if buyer_name and buyer_address and random.random() < PROB_BUYER_WITH_ADDRESS:
                        buyer_full = f"{buyer_name}, {buyer_address}"
                        gt_schema.append({
                            "key": "buyer/consignee",
                            "expected_value": buyer_name.upper(),
                            "operator": "EQUALS"
                        })
                        gt_schema.append({
                            "key": "buyer/consignee_address",
                            "expected_value": buyer_address.upper(),
                            "operator": "CONTAINS"
                        })
                        clause_blocks.append(template.format(val=buyer_full))
                        template_keys_used.append("buyer/consginee_")
                    elif buyer_name:
                        buyer_full = buyer_name
                        gt_schema.append({
                            "key": "buyer/consignee",
                            "expected_value": buyer_name.upper(),
                            "operator": "EQUALS"
                        })
                        clause_blocks.append(template.format(val=buyer_full))
                        template_keys_used.append("buyer/consginee_")
                else:
                    buyer_full = buyer_val
                    gt_schema.append({
                        "key": "buyer/consignee",
                        "expected_value": buyer_full.upper(),
                        "operator": "EQUALS"
                    })
                    clause_blocks.append(template.format(val=buyer_full))
                    template_keys_used.append("buyer/consginee_")

    # [4] Handle numbers (LC/Invoice)
    has_lc = bool(iv_data.get("lc_number"))
    has_inv = bool(iv_data.get("invoice_number"))
    if random.random() < PROB_NUMBER_HANDLING:
        if has_lc and has_inv:
            clause_blocks.append(random.choice(LC_AND_INVOICE_NUM_TEMPLATES))
            gt_schema.append({
                "key": "lc_number",
                "expected_value": "$LC_NUMBER",
                "operator": "EQUALS"
            })
            gt_schema.append({
                "key": "exist_invoice_number",
                "expected_value": True,
                "operator": "EXISTS"
            })
            template_keys_used.append("lc_and_invoice_num")
        elif has_lc:
            clause_blocks.append(random.choice(LC_NUM_ONLY_TEMPLATES))
            gt_schema.append({
                "key": "lc_number",
                "expected_value": "$LC_NUMBER",
                "operator": "EQUALS"
            })
            template_keys_used.append("lc_num_only")
        elif has_inv:
            inv_num = iv_data.get("invoice_number")
            if inv_num and random.random() < PROB_INVOICE_NUMBER_EXPLICIT:
                template = random.choice(INV_NUM_ONLY_EXPLICIT_TEMPLATES)
                clause_blocks.append(template.format(val=f" {inv_num}"))
                gt_schema.append({
                    "key": "invoice_number",
                    "expected_value": inv_num.upper() if isinstance(inv_num, str) else inv_num,
                    "operator": "EQUALS"
                })
                template_keys_used.append("inv_num_only_explicit")
            else:
                clause_blocks.append(random.choice(INVOICE_NUMBER_EXISTS_TEMPLATES))
                gt_schema.append({
                    "key": "exist_invoice_number",
                    "expected_value": True,
                    "operator": "EXISTS"
                })
                template_keys_used.append("invoice_number_exists")

    # [5] Country of Origin
    origin = iv_data.get("country_of_origin")
    if origin and random.random() < PROB_ORIGIN:
        if random.random() < PROB_ORIGIN_VAL:
            template = random.choice(ORIGIN_VAL_TEMPLATES)
            clause_blocks.append(template.format(val=origin))
            gt_schema.append({
                "key": "country_of_origin",
                "expected_value": origin.upper() if isinstance(origin, str) else origin,
                "operator": "EQUALS"
            })
            template_keys_used.append("origin_val")
        else:
            template = random.choice(ORIGIN_EXIST_TEMPLATES)
            clause_blocks.append(template)
            gt_schema.append({
                "key": "exist_country_of_origin",
                "expected_value": True,
                "operator": "EXISTS"
            })
            template_keys_used.append("origin_exist")

    # [6] Trade Terms
    trade_terms = iv_data.get("trade_terms")
    if trade_terms and random.random() < PROB_TRADE_TERMS:
        if random.random() < PROB_TRADE_TERMS_VAL:
            template = random.choice(TRADE_TERMS_VAL_TEMPLATES)
            clause_blocks.append(template.format(val=trade_terms))
            gt_schema.append({
                "key": "trade_terms",
                "expected_value": trade_terms.upper() if isinstance(trade_terms, str) else trade_terms,
                "operator": "EQUALS"
            })
            template_keys_used.append("trade_terms_val")
        else:
            template = random.choice(TRADE_TERMS_EXIST_TEMPLATES)
            clause_blocks.append(template)
            gt_schema.append({
                "key": "exist_trade_terms",
                "expected_value": True,
                "operator": "EXISTS"
            })
            template_keys_used.append("trade_terms_exist")

    # [7] Goods Description and HS Code
    goods_list = iv_data.get("goods_description", [])
    if goods_list and random.random() < PROB_GOODS_DESC:
        descs = [g.get("Descriptions_of_goods", "") for g in goods_list if g.get("Descriptions_of_goods")]
        if descs:
            # goods_description already contains "AND", so no need for connector handling
            combined_desc = ", ".join(descs)  # Connect with commas (AND is handled automatically in sentence)
            template = random.choice(GOODS_DESC_TEMPLATES)
            clause_blocks.append(template.format(val=combined_desc))
            gt_schema.append({
                "key": "goods_description",
                "expected_value": combined_desc.upper() if isinstance(combined_desc, str) else combined_desc,
                "operator": "CONTAINS"
            })
            template_keys_used.append("goods_desc")

        hs_codes = []
        for item in goods_list:
            code = item.get("HS_code")
            if code and code not in hs_codes:
                hs_codes.append(code)

        if hs_codes:
            hs_code_str = ", ".join(hs_codes)
            template = random.choice(HS_CODE_TEMPLATES)
            clause_blocks.append(template.format(val=hs_code_str))
            gt_schema.append({
                "key": "hs_code",
                "expected_value": hs_code_str.upper() if isinstance(hs_code_str, str) else hs_code_str,
                "operator": "CONTAINS"
            })
            template_keys_used.append("hs_code")

    # [8] Currency and Amount
    currency = iv_data.get("currency", "")
    total_amount_raw = iv_data.get("total_amount", "")

    # If total_amount_raw is "USD 362" format, separate currency and amount
    total_amount_val = total_amount_raw
    if currency and total_amount_raw.startswith(currency):
        total_amount_val = total_amount_raw[len(currency):].strip()

    # If currency exists, always add to GT
    if currency:
        gt_schema.append({
            "key": "currency",
            "expected_value": currency.upper() if isinstance(currency, str) else currency,
            "operator": "EQUALS"
        })

        # If total_amount exists, add to clause
        if total_amount_val:
            # if random.random() < PROB_TOTAL_AMOUNT:
            #     template = random.choice(TOTAL_AMOUNT_TEMPLATES)
            #     clause_blocks.append(template.format(currency=currency, val=total_amount_val))
            #     template_keys_used.append("total_amount")
            # else:
            #     clause_blocks.append(f"INDICATING TOTAL VALUE {currency} {total_amount_val}")
            #     template_keys_used.append("total_amount")
            template = random.choice(TOTAL_AMOUNT_TEMPLATES)
            clause_blocks.append(template.format(currency=currency, val=total_amount_val))
            template_keys_used.append("total_amount")

            gt_schema.append({
                "key": "total_amount",
                "expected_value": total_amount_val.upper() if isinstance(total_amount_val, str) else total_amount_val,
                "operator": "LTE"
            })
        else:
            # If only currency exists without total_amount, use currency template
            template = random.choice(CURRENCY_VAL_TEMPLATES)
            clause_blocks.append(template.format(currency=currency))
            template_keys_used.append("currency_val")

    # Build sentence
    final_clause = build_natural_sentence(clause_blocks, template_keys_used)

    # If GT is empty, ensure at least 1 item (fallback)
    if not gt_schema:
        if goods_list:
            descs = [g.get("Descriptions_of_goods", "") for g in goods_list if g.get("Descriptions_of_goods")]
            if descs:
                combined_desc = " AND ".join(descs)
                clause_blocks.append(f"COVERING {combined_desc}")
                gt_schema.append({
                    "key": "goods_description",
                    "expected_value": combined_desc.upper(),
                    "operator": "CONTAINS"
                })
                template_keys_used.append("goods_desc")
        elif origin:
            clause_blocks.append(f"CERTIFYING MERCHANDISE TO BE OF {origin} ORIGIN")
            gt_schema.append({
                "key": "country_of_origin",
                "expected_value": origin.upper(),
                "operator": "EQUALS"
            })
            template_keys_used.append("origin_val")
        elif trade_terms:
            clause_blocks.append(f"SHOWING TRADE TERMS {trade_terms}")
            gt_schema.append({
                "key": "trade_terms",
                "expected_value": trade_terms.upper(),
                "operator": "EQUALS"
            })
            template_keys_used.append("trade_terms_val")

        final_clause = build_natural_sentence(clause_blocks, template_keys_used)

    return final_clause, gt_schema