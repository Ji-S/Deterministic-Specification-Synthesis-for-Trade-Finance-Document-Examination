"""BL Clause Generator Constants"""

# ============== ORIGINALS related constants ==============
# Templates used for "3/3" format
ORIGINALS_3_3_OPTIONS = [
    "FULL SET OF",
    "COMPLETE SET OF",
    "3/3",
    "3/3 ORIGINAL",
]

# Suffix used for other numbers
ORIGINALS_SUFFIX_OPTIONS = ["", " ORIGINAL"]

# Conditions to ignore number_of_documents
ORIGINALS_IGNORE_VALUES = ["ZERO", "0"]

# ============== Probability values ==============
# Probability of adding CLEAN_ON_BOARD
PROB_CLEAN_ON_BOARD = 0.6

# Probability of adding CORE items
PROB_CONSIGNEE = 0.9
PROB_FREIGHT = 0.9
PROB_NOTIFY = 0.8

# Probability of including address in NOTIFY (name only)
PROB_NOTIFY_NAME_ONLY = 0.05

# Probability of adding NOTIFY optional template
PROB_NOTIFY_OPTIONAL = 0.4

# Probability of adding ROUTE
PROB_ROUTE_WITH_POD = 0.4
PROB_ROUTE_POL_ONLY = 0.4

# Probability of adding DELIVERY (when using ROUTE)
PROB_DELIVERY = 0.5

# Probability of adding SHIPMENT DATE
PROB_SHIPMENT_DATE = 0.25

# Probability of adding DATE OF ISSUE
PROB_DATE_OF_ISSUE = 0.25

# ============== CONSIGNEE related constants ==============
# Probability of including address in CONSIGNEE
PROB_CONSIGNEE_WITH_ADDRESS = 0.5

# Bank related consignee variables
CONSIGNEE_ISSUING_BANK = "$LC_ISSUING_BANK"
CONSIGNEE_DRAWEE_BANK = "$LC_DRAWEE_BANK"

# Bank related check strings
CONSIGNEE_ISSUING_BANK_KEYWORDS = ["ISSUING BANK"]
CONSIGNEE_DRAWEE_BANK_KEYWORDS = ["DRAWEE BANK"]

# ============== NOTIFY related constants ==============
# SAME AS CONSIGNEE special case
NOTIFY_SAME_AS_CONSIGNEE = "NOTIFY SAME AS CONSIGNEE"
NOTIFY_SAME_AS_CONSIGNEE_VALUE = "SAME AS CONSIGNEE"

# NOTIFY types
NOTIFY_TYPE_APPLICANT = "APPLICANT"
NOTIFY_TYPE_APPLICANT_WITH_ADDRESS = "APPLICANT_WITH_ADDRESS"

# NOTIFY optional template check
NOTIFY_WITH_ADDRESS_KEYWORD = "WITH FULL NAME AND ADDRESS"

# ============== Template filtering keyword ==============
# For excluding SHOWING templates
SHOWING_KEYWORD = "SHOWING"

# ============== Fallback template for POL only ==============
ROUTE_POL_ONLY_TEMPLATE = "EVIDENCING SHIPMENT FROM {pol}"

# ============== DELIVERY check keywords ==============
DELIVERY_KEYWORDS = ["PLACE OF DELIVERY", "GOODS TO BE DELIVERED AT"]
DESTINATION_KEYWORD = "FINAL DESTINATION"

# ============== Regex patterns ==============
# TEL/FAX removal pattern
TEL_FAX_PATTERN = r'\s*TEL[:\)]*\+?[\d\-()]*|\s*FAX[:\)]*\+?[\d\-()]*'

# consignee/notify parsing patterns
ENTITY_PARSE_PATTERN = r'(?:CONSIGNED TO|MADE OUT TO|ISSUED TO|SHOWING)\s+([A-Z][A-Z\s.,\d]+?)(?:\s+WITH|\s+AS|$)'
NOTIFY_PARSE_PATTERN = r'(?:NOTIFY|SHOWING|TO BE NOTIFIED)\s+([A-Z][A-Z\s.,\d]+?)(?:\s+WITH|\s+AS|TO BE|$)'