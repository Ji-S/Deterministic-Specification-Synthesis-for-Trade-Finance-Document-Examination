# clause_generator - Clause Data Generator

This module generates synthetic clause data for Bill of Lading (BL) and Commercial Invoice (IV) documents, along with Ground Truth (GT) labels.


## Directory Structure

```
clause_generator/
├── main.py                 # CLI entry point
├── bl_generator/           # Bill of Lading generator
│   ├── generator.py        # BL clause generation logic
│   ├── templates.py        # BL clause templates
│   └── constants.py        # BL constants and probabilities
├── iv_generator/           # Invoice generator
│   ├── generator.py        # IV clause generation logic
│   ├── templates.py        # IV clause templates
│   └── constants.py        # IV constants and probabilities
├── merge_bl_iv.py          # Merge logic (invoked via `main.py merge`)
└── __init__.py
```

## Features

### BL Generator (`bl_generator/`)
Generates Bill of Lading clauses with the following components:
- **HEAD**: Originals count, Clean on Board wording, Document type
- **CORE**: Consignee, Notify Party, Freight terms
- **TAIL**: Route (POL/POD), Delivery, Shipment date, Issue date

### IV Generator (`iv_generator/`)
Generates Commercial Invoice clauses with:
- Invoice date
- Exporter/Buyer information
- LC number and Invoice number
- Country of origin
- Trade terms (FOB, CIF, etc.)
- Goods description and HS codes
- Currency and total amount

### Merge Tool (`merge_bl_iv.py`)
Combines BL and IV generated data into a single file with:
- `++` separator between BL and IV clauses
- Combined GT array with `doc` field indicating source ("BL" or "IV")

### GT Operators
| Operator | Description | Example |
|----------|-------------|---------|
| `EXISTS` | Check if wording exists | `"clean_wording": true` |
| `EQUALS` | Exact match | Company names, ports |
| `CONTAINS` | Partial match | Addresses, descriptions |
| `LTE` | Less than or equal | Dates, amounts |
| `GTE` | Greater than or equal | Document counts |
| `NEGATION` | Check absence | `adverse_remarks: null` |

## Usage

All commands share a single entry point: `python3 -m clause_generator.main <command>`.

### Generate BL Data
```bash
# Using default paths (dataset/BL → dataset/generated/BL)
python3 -m clause_generator.main generate --type bl

# Custom paths
python3 -m clause_generator.main generate --type bl --input-dir /path/to/bl --output-dir /path/to/output
```

### Generate IV Data
```bash
# Using default paths (dataset/IV → dataset/generated/IV)
python3 -m clause_generator.main generate --type iv

# Custom paths
python3 -m clause_generator.main generate --type iv --input-dir /path/to/iv --output-dir /path/to/output
```

### Merge BL and IV
```bash
# Using default paths
python3 -m clause_generator.main merge

# Custom paths
python3 -m clause_generator.main merge --bl-dir dataset/generated/BL --iv-dir dataset/generated/IV --output-dir dataset/generated/merged

# Merge specific files
python3 -m clause_generator.main merge --bl-file dataset/generated/BL/dummy_01_BL.json --iv-file dataset/generated/IV/dummy_01_IV.json --output dataset/generated/merged/dummy_01_merged.json
```

## Configuration

### Probability Settings
Edit `constants.py` files to adjust generation probabilities:

**BL (`bl_generator/constants.py`):**
- `PROB_CLEAN_ON_BOARD`: Probability of adding "CLEAN ON BOARD" (default: 0.6)
- `PROB_CONSIGNEE`: Probability of including consignee (default: 0.9)
- `PROB_NOTIFY`: Probability of including notify party (default: 0.8)
- `PROB_ROUTE_WITH_POD`: Probability of including route with POD (default: 0.4)

**IV (`iv_generator/constants.py`):**
- `PROB_INVOICE_DATE_VAL`: Probability of explicit date vs EXISTS (default: 0.5)
- `PROB_EXPORTER_LC_BENEFICIARY`: Probability of using `$LC_BENEFICIARY` (default: 0.5)
- `PROB_PROCESS_EXPORTER`: Probability of including exporter (default: 0.6)

### Templates
Edit `templates.py` files to customize clause patterns:
- Add new sentence patterns
- Modify existing templates
- Configure template variations

## Input Format

The input JSON files should follow the same structure as the sample files in the `dataset/` directory:

- **BL Input**: See `dataset/BL/dummy_01_BL.json` for the expected format
- **IV Input**: See `dataset/IV/dummy_01_IV.json` for the expected format

Key fields:
- `im_path`: Path to the document image
- `full_bl_extraction` / `full_iv_extraction`: Extracted data from the document
- `consignee`, `notify_party`, `exporter`, `buyer`: Party information (name, address)

## Reference Variables

When generating GT, the following reference variables are used:

| Variable | Description |
|----------|-------------|
| `$LC_APPLICANT` | The applicant |
| `$LC_APPLICANT_ADDRESS` | The applicant address |
| `$LC_ISSUING_BANK` | The bank that issued the LC |
| `$LC_DRAWEE_BANK` | The drawee bank |
| `$LC_BENEFICIARY` | The beneficiary (exporter) |
| `$LC_NUMBER` | The LC number |



## Supplementary Table: Template library composition

```
─────────────────────────────────────────────────
Document  Section            #templates
BL        ORIGINALS              6 (4 + 2(original pattern))
BL        CLEAN_AND_BOARD        2
BL        DOC_TYPE               4
BL        SIGNED_DOC_TYPE        1
BL        CONSIGNEE             10
BL        NOTIFY                 8
BL        NOTIFY_OPTIONAL        2
BL        FREIGHT_TERMS          4
BL        ROUTE                  5
BL        DELIVERY               2
BL        DESTINATION            1
BL        SHIPMENT_DATE          4
BL        DATE_OF_ISSUE          4
─────────────────────────────────────────────────
BL subtotal                     53

IV    INVOICE_DATE_EXISTS                3        
IV    INVOICE_NUMBER_EXISTS              3        
IV    ORIGIN_EXIST                       3     
IV    TRADE_TERMS_EXIST                  3         
IV    ISSUER                             3       
IV    ISSUER_WITH_VAL                    3        
IV    BUYER_CONSIGNEE                    3      
IV    BUYER_CONSIGNEE_WITH_VAL           3       
IV    INVOICE_DATE_VAL                   3        
IV    ORIGIN_VAL                         3       
IV    TRADE_TERMS_VAL                    3       
IV    GOODS_DESC                         4       
IV    TOTAL_AMOUNT                       4 (3 + 1 total amount)     
IV    CURRENCY_VAL                       3        
IV    LC_AND_INVOICE_NUM                 3      
IV    LC_NUM_ONLY                        3        
IV    INV_NUM_ONLY_EXPLICIT              3         
IV    HS_CODE                            3       
──────────────────────────────────────────────────────────────
IV subtotal                            56
```
