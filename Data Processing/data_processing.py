from pathlib import Path
import pandas as pd

folder = Path(__file__).parent
input_file = folder / "data_to_process.csv"
output_file = folder / "processed_data.csv"
report_file = folder / "data_report.txt"

df = pd.read_csv(input_file)

# Clean up of text columns
for column in ["customer_name", "product", "category", "status"]:
    df[column] = df[column].fillna("").astype(str).str.strip().str.title()

df["email"] = df["email"].fillna("").astype(str).str.strip().str.lower()

#variables for old sheet
old_rows = len(df)
invalid_price = 0
unknown_statuses = df['status'].value_counts().get('Unknown', 0)
product = {"items": [], "cost": []}
valuable_item = {"item": "", "cost": 0.0}

for placement in range(len(df)):
    if "$" in df["unit_price"][placement] or "-" in df["unit_price"][placement]:
        invalid_price = invalid_price + 1
    df.loc[placement, "unit_price"] = df['unit_price'][placement].translate(str.maketrans({c: "" for c in "-$"}))
    if df["quantity"][placement] >= 1 and df["unit_price"][placement] != "":
        product["cost"].append(round(float(df["unit_price"][placement]) / float(df["quantity"][placement]), 2))
        product["items"].append(df["product"][placement])

for place in range(len(product["items"])):
    if product["cost"][place] > valuable_item["cost"]:
        valuable_item["item"] = product["items"][place]
        valuable_item["cost"] = product["cost"][place]

dates = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
df["order_date"] = dates.dt.strftime("%Y-%m-%d").fillna(df["order_date"])

# Simple checks for missing or questionable email information
df["email_status"] = "OK"
df.loc[df["email"] == "", "email_status"] = "Missing"
df.loc[df["email"] != "",
"email_status"
] = df.loc[df["email"] != "", "email_status"].where(
    df.loc[df["email"] != "", "email"].str.contains("@")
    & df.loc[df["email"] != "", "email"].str.contains(r"\.", regex=True),
    "Check email",
)

df["quantity_status"] = "OK"
df.loc[df["quantity"].isnull(), "quantity_status"] = "Missing"
df.loc[df["quantity"] == 0, "quantity_status"] = "Zero"

df = df.drop_duplicates(subset=["customer_name", "email"])

#output
df.to_csv(output_file, index=False)

#variables for report
new_rows = len(df)
missing_email = df['email_status'].value_counts().get('Missing', 0)
check_email = df['email_status'].value_counts().get('Check email', 0)
missing_quantity = df['quantity_status'].value_counts().get('Missing', 0)
zero_quantity = df['quantity_status'].value_counts().get('Zero', 0)


report_file.write_text(f"""Datasheet Report
----------------------------------
Issues Found
- Duplicate Records: {old_rows - new_rows}
- Missing Values: {missing_quantity + zero_quantity}
- Invalid Emails: {missing_email + check_email}
- Invalid Prices: {invalid_price}
- Unknown Statuses: {unknown_statuses}

Structure: Before | After
Total Records: {old_rows + 1} | {new_rows + 1}
Duplicate Records: {old_rows - new_rows} | {new_rows - new_rows}
Invalid Prices: {invalid_price} | {invalid_price - invalid_price}
Invalid Quantities: Missing: {missing_quantity} | Zero: {zero_quantity}
Invalid Email: Missing: {missing_email} | Check email: {check_email}

Total Revenue: ${round(df["unit_price"].apply(pd.to_numeric, errors='coerce').sum(), 2)}
Most Valuable Product (MVP): {valuable_item["item"]} at ${valuable_item['cost']}

Product Prices: 
""")
for place in range(len(product["items"])):
    with report_file.open(mode="a", encoding="utf-8") as f:
        f.writelines(f"{product['items'][place]} at ${product['cost'][place]}\n")