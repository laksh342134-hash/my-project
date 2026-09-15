import pandas as pd


def load_data(filepath):
    if filepath.endswith(".csv"):
        return pd.read_csv(filepath)
    return pd.read_excel(filepath)


def check_missing_values(df):
    return (df.isnull().sum() / len(df) * 100).round(2)


def check_duplicates(df):
    return df.duplicated().sum()


def detect_pii(df):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"

    pii_columns = {}
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().astype(str).head(50)
        email_matches = sample.str.contains(email_pattern, regex=True).sum()
        phone_matches = sample.str.contains(phone_pattern, regex=True).sum()

        if email_matches > 0:
            pii_columns[col] = "Email PII"
        elif phone_matches > 0:
            pii_columns[col] = "Phone PII"
    return pii_columns


def risk_score(missing_pct, has_pii):
    if has_pii and missing_pct < 5:
        return "High"
    if has_pii:
        return "Medium"
    if missing_pct > 20:
        return "Medium"
    return "Low"
