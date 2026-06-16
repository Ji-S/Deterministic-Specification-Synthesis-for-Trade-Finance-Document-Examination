"""Invoice Clause Generator Constants"""

# ============== Probability values ==============
# Invoice Date: explicit date (LTE) vs existence (EXISTS)
PROB_INVOICE_DATE_VAL = 0.5

# Exporter: $LC_BENEFICIARY vs actual name
PROB_EXPORTER_LC_BENEFICIARY = 0.5

# Use exporter name + address together
PROB_EXPORTER_WITH_ADDRESS = 0.5

# Exporter processing probability
PROB_PROCESS_EXPORTER = 0.6  # random.random() > 0.4 → 60%

# Buyer/Consignee: $LC_APPLICANT vs actual name
PROB_BUYER_LC_APPLICANT = 0.5

# Buyer/Consignee name + address together
PROB_BUYER_WITH_ADDRESS = 0.5

# Buyer/Consignee processing probability
PROB_PROCESS_BUYER = 0.6  # random.random() > 0.4 → 60%

# Number handling (LC/Invoice)
PROB_NUMBER_HANDLING = 0.4  # random.random() > 0.6 → 40%

# Invoice number explicit display
PROB_INVOICE_NUMBER_EXPLICIT = 0.5

# Country of Origin
PROB_ORIGIN = 0.4  # random.random() > 0.6 → 40%

# Country of Origin: explicit value (EQUALS) vs existence (EXISTS)
PROB_ORIGIN_VAL = 0.5

# Trade Terms
PROB_TRADE_TERMS = 0.4  # random.random() > 0.6 → 40%

# Trade Terms: explicit value (EQUALS) vs existence (EXISTS)
PROB_TRADE_TERMS_VAL = 0.5

# Goods Description
PROB_GOODS_DESC = 0.5

# Currency/Amount
PROB_TOTAL_AMOUNT = 0.5

# ============== Sentence type classification ==============
SENTENCE_CATEGORIES = {
    "date": ["invoice_date_val", "invoice_date_exists"],
    "party": ["issuer", "issuer_", "buyer/consignee", "buyer/consginee_"],
    "number": ["lc_and_invoice_num", "lc_num_only", "inv_num_only", "inv_num_only_explicit"],
    "origin": ["origin_val", "origin_exist"],
    "trade": ["trade_terms_val", "trade_terms_exist"],
    "goods": ["goods_desc"],
    "amount": ["total_amount", "currency_val"],
    "code": ["hs_code"],
}

# ============== Connectors ==============
CONNECTOR_SAME_CATEGORY = ", "
CONNECTOR_DIFF_CATEGORY = " AND "