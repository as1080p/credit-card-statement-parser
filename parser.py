import pdfplumber
import re
import pandas as pd
import json

# -------------------------------------------------
# STEP 1 — Extract all text and tables
# -------------------------------------------------
def extract_text_and_tables(pdf_path):
    all_text = ""
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            all_text += page.extract_text() or ""
            for table in page.extract_tables():
                df = pd.DataFrame(table)
                all_tables.append(df)
    all_text = re.sub(r"\s+", " ", all_text.strip())
    return all_text.lower(), all_tables


# -------------------------------------------------
# STEP 2 — Keyword-based field extraction
# -------------------------------------------------
def extract_field(text, field_keywords):
    for keyword in field_keywords:
        pattern = rf"{keyword}[:\-\s₹]*([\d,]+(?:\.\d{{2}})?|\d{{1,2}}\s?\w+\s?\d{{4}})"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


# -------------------------------------------------
# STEP 3 — Extract statement-level fields
# -------------------------------------------------
def extract_data_points(text):
    data = {}

    fields = {
        "Payment Due Date": ["payment due date", "due date"],
        "Total Amount Due": ["total amount due", "closing balance", "amount payable"],
        "Minimum Amount Due": ["minimum amount due"],
        "Credit Limit": ["credit limit", "total credit limit"],
        "Available Credit": ["available credit", "remaining credit"],
        "Opening Balance": ["opening balance", "previous balance"]
    }

    for field, keywords in fields.items():
        data[field] = extract_field(text, keywords)

    # --- Add cardholder details ---
    name_match = re.search(r"(?:name|cardholder name)[:\-\s]+([a-z\s]+)", text, re.IGNORECASE)
    pincode_match = re.search(r"\b\d{6}\b", text)
    if name_match:
        data["Cardholder Name"] = name_match.group(1).strip().title()
    if pincode_match:
        data["Pincode"] = pincode_match.group(0)

    return data


# -------------------------------------------------
# STEP 4 — Extract transaction table (date, desc, amount)
# -------------------------------------------------
def extract_transaction_amounts(tables):
    debit_total, credit_total = 0.0, 0.0
    transactions = []

    for page_idx, df in enumerate(tables):
        if df.empty or df.shape[1] < 2:
            continue

        headers = " ".join(df.iloc[0].astype(str).str.lower())
        if "amount" in headers and ("date" in headers or "description" in headers):
            for i, row in df.iterrows():
                values = [str(v).strip() for v in row if pd.notna(v)]
                if len(values) < 2:
                    continue

                date = str(values[0])
                desc = str(values[1])
                amount_str = str(values[-1]).replace(",", "").replace("₹", "")

                try:
                    amt = float(re.findall(r"[-+]?\d*\.\d+|\d+", amount_str)[0])
                except:
                    continue

                # Determine type
                tx_type = "Debit"
                if re.search(r"(credit|refund|payment|received)", " ".join(values).lower()):
                    tx_type = "Credit"

                transactions.append({
                    "Date": date,
                    "Description": desc,
                    "Amount": amt,
                    "Type": tx_type,
                    "Table_Index": page_idx
                })

                if tx_type == "Debit":
                    debit_total += amt
                else:
                    credit_total += amt

    return debit_total, credit_total, transactions


# -------------------------------------------------
# STEP 5 — Validation logic
# -------------------------------------------------
def validate_statement(data, debit_total, credit_total):
    validations = {}
    try:
        total_due = float(data.get("Total Amount Due", "0").replace(",", ""))
        credit_limit = float(data.get("Credit Limit", "0").replace(",", ""))
        available_credit = float(data.get("Available Credit", "0").replace(",", ""))
        opening_balance = float(data.get("Opening Balance", "0").replace(",", "")) if data.get("Opening Balance") else 0.0

        # Rule 1 — Available Credit = Credit Limit - Outstanding Balance
        validations["Available Credit Validation"] = abs((credit_limit - total_due) - available_credit) < 1

        # Rule 2 — Closing Balance = Opening + Credit - Debit
        closing_calc = opening_balance + credit_total - debit_total
        validations["Closing Balance Validation"] = abs(closing_calc - total_due) < 1_000

    except Exception as e:
        validations["Error"] = str(e)

    return validations


# -------------------------------------------------
# STEP 6 — Minimum Due Table
# -------------------------------------------------
def build_min_due_summary(data):
    try:
        total_due = float(data.get("Total Amount Due", "0").replace(",", ""))
        min_due_pdf = float(data.get("Minimum Amount Due", "0").replace(",", ""))
    except:
        total_due, min_due_pdf = 0, 0

    est_min_due = round(total_due * 0.05, 2)
    df = pd.DataFrame([{
        "Total Due": total_due,
        "Minimum Due (from PDF)": min_due_pdf,
        "Expected Min Due (5%)": est_min_due,
        "Deviation": round(abs(min_due_pdf - est_min_due), 2)
    }])
    df.to_csv("minimum_due_summary.csv", index=False)
    return df


# -------------------------------------------------
# STEP 7 — Main Runner
# -------------------------------------------------
def main(pdf_path):
    text, tables = extract_text_and_tables(pdf_path)
    data = extract_data_points(text)
    debit_total, credit_total, transactions = extract_transaction_amounts(tables)
    validations = validate_statement(data, debit_total, credit_total)

    # Write outputs
    pd.DataFrame(transactions).to_csv("transactions.csv", index=False)
    build_min_due_summary(data)

    data["Total Debit Amount"] = f"{debit_total:,.2f}"
    data["Total Credit Amount"] = f"{credit_total:,.2f}"

    print("\n📄 Extracted Fields:")
    print(json.dumps(data, indent=4))

    print("\n🧾 Validation Results:")
    for k, v in validations.items():
        print(f"{k}: {'✅ Pass' if v else '⚠️ Fail'}")

    pd.DataFrame([data]).to_csv("statement_summary.csv", index=False)


if __name__ == "__main__":
    pdf_file = "data/axisBank_statement.pdf"  # change this to your test file path
    main(pdf_file)
