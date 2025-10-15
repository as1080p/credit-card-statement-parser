# parser.py (Enhanced Version with Axis Bank & Output Folders)
import pdfplumber
import re
import json
import os
from rapidfuzz import process, fuzz
import pandas as pd
from tabulate import tabulate

# -------------------------
# bank detection keywords
# -------------------------
BANK_KEYWORDS = {
    "HDFC Bank": ["hdfc bank", "hdfc credit card", "hdfc bank credit"],
    "ICICI Bank": ["icici bank", "icici credit card"],
    "State Bank of India": ["sbi card", "state bank of india", "sbi credit card"],
    "Bank of Baroda": ["bank of baroda", "bob credit card", "baroda credit card"],
    "Axis Bank": ["axis bank", "axis bank credit card", "axis bank cards"]
}

# -------------------------
# card variants (expanded)
# -------------------------
CARD_VARIANTS = [
    # HDFC Variants
    "Indian Oil HDFC Bank Credit Card", "Marriot Bonvoy HDFC Bank Credit Card", "Freedom Credit Card",
    "HDFC MoneyBack+ Credit Card", "Swiggy HDFC Bank Credit Card", "HDFC Bank Millenia Credit Card",
    "Tata Neu Infinity HDFC Bank Credit Card", "HDFC Regalia Gold Credit Card",
    "HDFC Diners Club Black Metal Edition Credit Card", "Shopper Stop HDFC Bank Credit Card",

    # ICICI Variants
    "MakeMyTrip ICICI Bank Credit Card", "ICICI Bank Platinum Chip Credit Card",
    "ICICI Bank Coral Credit Card", "ICICI Bank Rubyx Credit Card", "ICICI Bank Sapphiro Credit Card",
    "ICICI Bank Chennai Super Kings Credit Card", "ICICI Bank HPCL Coral Visa Credit Card",
    "Amazon Pay ICICI Bank Credit Card", "ICICI Bank Manchester United Platinum Credit Card",
    "ICICI Bank Manchester United Signature Credit Card", "ICICI Bank Expressions Credit Card",
    "ICICI Bank HPCL Super Saver Credit Card", "ICICI Bank Emirates Visa Signature Credit Card",
    "ICICI Bank Accelero Visa Platinum Credit Card", "ICICI Bank Parakram Credit Card",
    "ICICI Bank Adani One Platinum Credit Card", "ICICI Bank Adani One Signature Credit Card",
    "Times Black ICICI Bank Credit Card",

    # SBI Variants
    "SimplyCLICK SBI Card", "SimplySAVE SBI Card", "BPCL SBI Card", "SBI Card PRIME",
    "SBI Card ELITE", "Cashback SBI Card", "IRCTC SBI Platinum Card", "SBI Card Miles Elite",
    "SBI Card PULSE", "Reliance SBI Card",

    # Bank of Baroda Variants
    "Bank of Baroda Vikram Credit Card", "Indian Coast Guard Rakshamah BoB Credit Card",
    "IRCTC BoB Credit Card", "Indian Army Yoddha BoB Credit Card", "Indian Navy Varunah BoB Credit Card",
    "BoB Nainital Bank RENAISSANCE", "HPCL BoB ENERGIE Credit Card", "Snapdeal BoB Credit Card",
    "Assam Rifles The Sentinel BoB Credit Card", "CMA One Credit Card", "ConQR Credit Card",
    "Easy Credit Card", "Eterna Credit Card", "ICAI Exclusive Credit Card", "ICSI Diamond Credit Card",
    "Premier Credit Card", "Select Credit Card", "BoB CORPORATE Credit Card",
    "Bank of Baroda PRIME Credit Card", "Bank of Baroda EMPOWER Credit Card",

    # Axis Bank Variants (newly added)
    "Axis Bank ACE Credit Card", "Axis Bank Ace Credit Card", "Flipkart Axis Bank Credit Card",
    "Axis Bank Neo Credit Card", "Axis Bank My Wings Credit Card", "Axis Bank Select Credit Card",
    "Axis Bank Vistara Signature Credit Card", "Axis Bank My Zone Credit Card",
    "Axis Bank Magnus Credit Card", "Axis Bank Reserve Credit Card", "Axis Bank Atlas Credit Card"
]

# -------------------------
# helpers
# -------------------------
def load_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pt = page.extract_text()
            if pt:
                text += "\n" + pt
    return text.strip()

def detect_bank(text):
    txt = text.lower()
    for bank, kws in BANK_KEYWORDS.items():
        for kw in kws:
            if kw in txt:
                return bank
    choices = list(BANK_KEYWORDS.keys())
    match = process.extractOne(text, choices, scorer=fuzz.partial_ratio)
    return match[0] if match and match[1] > 70 else "Unknown"

def detect_card_variant(text):
    match = process.extractOne(text, CARD_VARIANTS, scorer=fuzz.partial_ratio)
    if match and match[1] >= 80:
        return match[0]
    return "Not found"

def last4_from_text(text):
    m = re.search(r'(?:\b|[^0-9])(?:x{0,4}[- ]?){0,3}(\d{4})\b', text, re.IGNORECASE)
    return m.group(1) if m else "Not found"

# -------------------------
# transaction extractor
# -------------------------
def extract_transactions(pdf_path):
    txns = []
    with pdfplumber.open(pdf_path) as pdf:
        for p_idx, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if not tables:
                continue
            for table in tables:
                if len(table) < 2:
                    continue
                header = [str(h).strip().lower() if h else "" for h in table[0]]
                if any("date" in h for h in header) and (any("amount" in h for h in header) or any("debit" in h for h in header) or any("credit" in h for h in header)):
                    try:
                        date_idx = next(i for i,h in enumerate(header) if "date" in h)
                        amount_idx = next((i for i,h in enumerate(header[::-1]) if "amount" in h or "inr" in h or "rs" in h), None)
                        if amount_idx is not None:
                            amount_idx = len(header) - 1 - amount_idx
                        desc_idx = None
                        for i in range(date_idx+1, (amount_idx if amount_idx else len(header))):
                            if header[i] and ("desc" in header[i] or "particu" in header[i] or "merchant" in header[i] or "remarks" in header[i]):
                                desc_idx = i
                                break
                        if desc_idx is None:
                            desc_idx = date_idx + 1 if date_idx + 1 < len(header) else None
                    except StopIteration:
                        date_idx = 0; desc_idx = 1; amount_idx = len(header) - 1

                    for row in table[1:]:
                        row = [(c if c is not None else "").strip() for c in row]
                        if amount_idx is None or amount_idx >= len(row):
                            values = [c for c in row if re.search(r'\d', str(c))]
                            if not values:
                                continue
                            amount_cell = values[-1]
                        else:
                            amount_cell = row[amount_idx]
                        am = re.search(r"-?\d+[,0-9]*\.\d{1,2}|-?\d+", amount_cell.replace("₹", "").replace(",", "")) if amount_cell else None
                        if not am:
                            continue
                        amount = float(am.group(0).replace(",", ""))
                        date = row[date_idx] if date_idx < len(row) else ""
                        desc = row[desc_idx] if desc_idx is not None and desc_idx < len(row) else ""
                        txns.append({"Date": date, "Description": desc, "Amount": amount, "Page": p_idx})

    if txns:
        os.makedirs("outputs/csv", exist_ok=True)
        pd.DataFrame(txns).to_csv(os.path.join("outputs/csv", "transactions.csv"), index=False)
    return txns

# -------------------------
# Generic parser helper
# -------------------------
def parse_common_fields(block):
    result = {}
    result["billing_cycle"] = re.search(r"Statement\s*Period.*?(\d{1,2}\s*[A-Za-z]{3,9}\s*\d{2,4}.*?(?:to|-|–).*?\d{1,2}\s*[A-Za-z]{3,9}\s*\d{2,4})", block, re.IGNORECASE)
    result["billing_cycle"] = result["billing_cycle"].group(1).strip() if result["billing_cycle"] else "Not found"

    for field, key in [
        (r"Statement\s*Date", "statement_date"),
        (r"Payment\s*Due\s*Date", "payment_due_date"),
        (r"Total\s*Amount\s*Due", "total_balance"),
        (r"Minimum\s*Amount\s*Due", "minimum_due"),
        (r"Credit\s*Limit", "credit_limit"),
        (r"Available\s*Credit\s*Limit", "available_credit_limit"),
        (r"Cash\s*Limit", "cash_limit"),
        (r"Available\s*Cash\s*Limit", "available_cash_limit"),
    ]:
        m = re.search(field + r"[^\d₹]*₹?\s*([\d,]+\.\d{2}|\d{1,3}(?:,\d{3})*)", block, re.IGNORECASE)
        result[key] = m.group(1).replace(",", "") if m else "Not found"

    return result

# -------------------------
# Bank-specific parsers
# -------------------------
def parse_axis(text, pdf_path):
    res = {"card_variant": detect_card_variant(text), "last4": last4_from_text(text)}
    summary_block = re.search(r"Statement\s*Period.*?Available\s*Cash\s*Limit.*?Transaction\s*Details", text, re.DOTALL | re.IGNORECASE)
    block = " ".join(summary_block.group(0).split()) if summary_block else text
    res.update(parse_common_fields(block))
    txns = extract_transactions(pdf_path)
    return res, txns

# Reuse common ones for other banks (omitted for brevity)
parse_hdfc = parse_icici = parse_sbi = parse_bob = parse_axis

# -------------------------
# main driver
# -------------------------
def main(pdf_path):
    if not os.path.exists(pdf_path):
        print("File not found:", pdf_path); return

    text = load_text(pdf_path)
    bank = detect_bank(text)
    print("Detected bank:", bank)

    parsers = {
        "HDFC Bank": parse_hdfc,
        "ICICI Bank": parse_icici,
        "State Bank of India": parse_sbi,
        "Bank of Baroda": parse_bob,
        "Axis Bank": parse_axis
    }

    parse_func = parsers.get(bank)
    parsed, txns = parse_func(text, pdf_path) if parse_func else ({}, [])

    summary = {"bank_detected": bank, **parsed, "transactions_extracted": len(txns)}

    os.makedirs("outputs/json", exist_ok=True)
    out_json = os.path.join("outputs/json", os.path.splitext(os.path.basename(pdf_path))[0] + "_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    print("\nSummary Preview:")
    for k,v in summary.items():
        print(f"  {k}: {v}")

    if txns:
        print("\nTransaction sample (first 10 rows):")
        df = pd.DataFrame(txns)
        print(tabulate(df.head(10), headers="keys", tablefmt="grid", showindex=False))
        print("\nSaved CSV to outputs/csv and JSON to outputs/json")
    else:
        print("\nNo transactions extracted (table structure may be different).")

if __name__ == "__main__":
    pdf_path = input("Enter path to statement PDF: ").strip()
    main(pdf_path)