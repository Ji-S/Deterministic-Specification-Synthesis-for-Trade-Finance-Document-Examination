"""Invoice Clause Generator Template Definitions"""

# ==========================================
# Template Pool - Classified by Operator Type
# ==========================================

# ==========================
# Templates for EXISTS (only value existence required)
# ==========================
INVOICE_DATE_EXISTS_TEMPLATES = [
    "DATED", "SHOWING INVOICE DATE", "INDICATING DATE OF ISSUE"
]

INVOICE_NUMBER_EXISTS_TEMPLATES = [
    "INDICATING COMMERCIAL INVOICE NO.", "SHOWING INVOICE NUMBER", "BEARING INVOICE NO."
]

ORIGIN_EXIST_TEMPLATES = [
    "AND THE NAME OF COUNTRY OF ORIGIN OF THE GOODS SHIPPED",
    "SHOWING COUNTRY OF ORIGIN",
    "INDICATING ORIGIN OF GOODS"
]

TRADE_TERMS_EXIST_TEMPLATES = [
    "SHOWING TRADE TERMS", "INDICATING TRADE TERMS", "EVIDENCING PRICE TERMS"
]

# ==========================
# Templates for EQUALS (exact value required)
# ==========================
ISSUER_TEMPLATES = [  # $LC_BENEFICIARY from LC
    "ISSUED BY BENEFICIARY", "EXECUTED BY BENEFICIARY", "PREPARED BY BENEFICIARY"
]

ISSUER_WITH_VAL_TEMPLATES = [  # exporter from IV
    "ISSUED BY {val}", "EXECUTED BY {val}", "PREPARED BY {val}"
]

BUYER_CONSIGNEE_TEMPLATES = [  # $LC_APPLICANT from LC
    "MADE OUT TO APPLICANT", "BILLED TO APPLICANT", "CONSIGNED TO APPLICANT"
]

BUYER_CONSIGNEE_WITH_VAL_TEMPLATES = [  # buyer or consignee from IV
    "MADE OUT TO {val}", "CONSIGNED TO {val}", "BILLED TO {val}"
]


ORIGIN_VAL_TEMPLATES = [
    "CERTIFYING MERCHANDISE TO BE OF {val} ORIGIN",
    "SHOWING ORIGIN AS {val}",
    "INDICATING COUNTRY OF ORIGIN AS {val}"
]

TRADE_TERMS_VAL_TEMPLATES = [
    "SHOWING TRADE TERMS {val}", "INDICATING {val}", "EVIDENCING {val}"
]


CURRENCY_VAL_TEMPLATES = [
    "IN {currency}", "EXPRESSED IN {currency}", "DENOMINATED IN {currency}"
]

LC_AND_INVOICE_NUM_TEMPLATES = [
    "INDICATING THIS L/C NO., COMMERCIAL INVOICE NO.",
    "SHOWING THIS L/C NO. AND INVOICE NO.",
    "QUOTING OUR L/C NUMBER AND INVOICE NUMBER"
]


# ==========================
# Templates for CONTAINS (partial match)
# ==========================
LC_NUM_ONLY_TEMPLATES = [
    "INDICATING THIS L/C NO.", "QUOTING OUR L/C NO.", "SHOWING L/C NUMBER"
]

INV_NUM_ONLY_EXPLICIT_TEMPLATES = [
    "INDICATING COMMERCIAL INVOICE NO.{val}", "SHOWING INVOICE NUMBER{val}", "BEARING INVOICE NO.{val}"
]

HS_CODE_TEMPLATES = [
    "INDICATING H.S. CODE {val}", "SHOWING HS CODE {val}", "STATING H.S. CODE {val}"
]


GOODS_DESC_TEMPLATES = [
    "COVERING {val}", "SHOWING {val}", "EVIDENCING SHIPMENT OF {val}", "DESCRIBING GOODS AS {val}"
]
# ============================
# Template for LTE
# ============================
INVOICE_DATE_VAL_TEMPLATES = [  # Explicit date requirement (for LTE)
    "DATED {val}", "ISSUED ON OR BEFORE {val}", "SHOWING DATE {val}"
]

TOTAL_AMOUNT_TEMPLATES = [
    "INDICATING TOTAL AMOUNT OF {currency} {val}",
    "SHOWING INVOICE VALUE {currency} {val}",
    "EVIDENCING AMOUNT NOT EXCEEDING {currency} {val}",
    "INDICATING TOTAL VALUE {currency} {val}"
]