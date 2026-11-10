from pathlib import Path
import pandas as pd

folder = Path(__file__).parent
input_file = folder / "messy_customers.csv"
output_file = folder / "organized_customers.csv"
report_file = folder / "report.txt"

df = pd.read_csv(input_file)

# Clean up of text columns
for column in ["first_name", "last_name", "city"]:
    df[column] = df[column].fillna("").astype(str).str.strip().str.title()

df["email"] = df["email"].fillna("").astype(str).str.strip().str.lower()

state_names = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
    "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC",
}

df["state"] = (
    df["state"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
    .replace(state_names)
    .str.upper()
)

# Standardized phone numbers w/ 10 digits
def clean_phone(phone):
    if pd.isna(phone):
        return ""

    digits = "".join(character for character in str(phone) if character.isdigit())

    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    return str(phone).strip()


df["phone"] = df["phone"].apply(clean_phone)

# Standardized dates
dates = pd.to_datetime(df["signup_date"], format="mixed", errors="coerce")
df["signup_date"] = dates.dt.strftime("%Y-%m-%d").fillna(df["signup_date"])

# Simple checks for missing or questionable email information
df["email_status"] = "OK"
df.loc[df["email"] == "", "email_status"] = "Missing"
df.loc[
    df["email"] != "",
    "email_status"
] = df.loc[df["email"] != "", "email_status"].where(
    df.loc[df["email"] != "", "email"].str.contains("@")
    & df.loc[df["email"] != "", "email"].str.contains(r"\.", regex=True),
    "Check email",
)

df["phone_status"] = "Present"
df.loc[df["phone"] == "", "phone_status"] = "Missing"

# Customer sorting...
df = df.sort_values(
    by=["state", "city", "last_name"],
    na_position="last"
)

df.to_csv(output_file, index=False)

print("CSV organization complete!")
print(f"Saved to: {output_file}")
try:
    report_file.touch()
except FileExistsError:
    pass
report_file.write_text(f"""REPORT:
----------------------------------
Customers processed: {len(df["customer_id"])}
Emails missing: {(df['email_status'] == 'Missing').sum()}
Phone Numbers missing: {(df['phone_status'] == 'Missing').sum()}""")
print(f"Report saved to: {report_file}")