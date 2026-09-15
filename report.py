import pandas as pd
import sys

from checker import (
    check_duplicates,
    check_missing_values,
    detect_pii,
    load_data,
    risk_score,
)


def generate_report(filepath):
    df = load_data(filepath)
    missing = check_missing_values(df)
    duplicates = check_duplicates(df)
    pii_cols = detect_pii(df)
    
    report_rows = []
    for col in df.columns:
        has_pii = col in pii_cols
        report_rows.append({
            "Column": col,
            "Missing %": missing[col],
            "PII Detected": pii_cols.get(col, "None"),
            "Risk Level": risk_score(missing[col], has_pii)
        })
    
    report_df = pd.DataFrame(report_rows)
    print(f"Total duplicate rows: {duplicates}")
    return report_df

input_path = sys.argv[1] if len(sys.argv) > 1 else "sample_data.csv"
report = generate_report(input_path)
print(report)