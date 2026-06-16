"""BL Clause Template Definitions"""

# HEAD section templates
ORIGINALS_TEMPLATES = [
    "FULL SET OF",  # Used when "3/3" or "FULL SET" is written
    "COMPLETE SET OF",  # Used when "3/3 COMPLETE SET" is written
    "3/3",  # Used when "3/3 COMPLETE SET" is written
    "3/3 ORIGINAL", # Used when "3/3 COMPLETE SET" is written
    "{n}/{n} ORIGINAL",  # Others
    "{n} ORIGINAL",  # Others
]

CLEAN_AND_BOARD_TEMPLATES = [
    "CLEAN ON BOARD",
    "CLEAN SHIPPED ON BOARD",
]

DOC_TYPE_TEMPLATES = [
    "OCEAN BILLS OF LADING",
    "MARINE BILLS OF LADING",
    "BILLS OF LADING",
    "B/L",
]

SIGNED_DOC_TYPE_TEMPLATES = [
    "SIGNED BILLS OF LADING",
]

# CONSIGNEE section templates
CONSIGNEE_TEMPLATES = [
    "CONSIGNED TO {consignee}",
    "MADE OUT TO {consignee}",
    "ISSUED TO {consignee}",
    "SHOWING {consignee} AS CONSIGNEE",
    "CONSIGNED TO ORDER OF ISSUING BANK",
    "MADE OUT TO ORDER OF ISSUING BANK",
    "CONSIGNED TO ORDER OF DRAWEE BANK",
    "MADE OUT TO ORDER OF DRAWEE BANK",
    "ISSUED TO ISSUING BANK",
    "SHOWING ISSUING BANK AS CONSIGNEE",
]


# NOTIFY section templates
NOTIFY_TEMPLATES = [
    "NOTIFY APPLICANT",
    "APPLICANT TO BE NOTIFIED",
    "{notify_party} TO BE NOTIFIED",
    "SHOWING {notify_party} AS NOTIFY PARTY",
    "NOTIFY {notify_party}",
    "SHOWING APPLICANT AS NOTIFY PARTY",
    "INDICATING APPLICANT AS NOTIFY PARTY",
    "NOTIFY SAME AS CONSIGNEE",  # Used when "same as consignee" is written
]

NOTIFY_OPTIONAL_TEMPLATES = [
    "WITH FULL NAME",
    "WITH FULL NAME AND ADDRESS",
]

# FREIGHT section templates
FREIGHT_TERMS_TEMPLATES = [
    "MARKED {FREIGHT_TERMS}",
    "MARKED {FREIGHT_TERMS}", ## duplicate
    "MARKED '{FREIGHT_TERMS}'",
    "MARKED '{FREIGHT_TERMS}'", ## duplicate
    "SHOWING {FREIGHT_TERMS}",
    "INDICATING {FREIGHT_TERMS}",
    "INDICATING {FREIGHT_TERMS}", ## duplicate
]

# ROUTE section templates
ROUTE_TEMPLATES = [
    "SHIPMENT FROM {pol} TO {pod}",
    "FROM {pol} TO {pod}",
    "PORT OF LOADING {pol} PORT OF DISCHARGE {pod}",
    "EVIDENCING SHIPMENT FROM {pol} TO {pod}",
    "EVIDENCING SHIPMENT FROM {pol}",  # Can be used when only pol exists
]

# DELIVERY section templates
DELIVERY_TEMPLATES = [
    "PLACE OF DELIVERY {delivery}",
    "GOODS TO BE DELIVERED AT {delivery}",
]

DESTINATION_TEMPLATES = [
    "FINAL DESTINATION {destination}",
]

# SHIPMENT DATE section templates
SHIPMENT_DATE_TEMPLATES = [
    "LATEST SHIPMENT DATE {on_board_date}",
    "ON BOARD DATE NOT LATER THAN {on_board_date}",
    "SHIPMENT EFFECTED NOT LATER THAN {on_board_date}",
    "EVIDENCING ON BOARD SHIPMENT ON OR BEFORE {on_board_date}",
]

# DATE OF ISSUE section templates
DATE_OF_ISSUE_TEMPLATES = [
    "DATED NOT LATER THAN {date_of_issue}",
    "ISSUED NOT LATER THAN {date_of_issue}",
    "DATED ON OR BEFORE {date_of_issue}",
    "DATE OF ISSUANCE NOT LATER THAN {date_of_issue}",
]