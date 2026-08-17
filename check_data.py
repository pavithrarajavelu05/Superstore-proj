import pandas as pd

df = pd.read_csv("Sample - Superstore.csv", encoding="latin1")

print("SHAPE:", df.shape)
print("\nCOLUMNS:\n", df.columns.tolist())
print("\nDTYPES:\n", df.dtypes)
print("\nMISSING VALUES:\n", df.isnull().sum())
print("\nHEAD:\n", df.head())
print("\nDATE RANGE:")
df["Order Date"] = pd.to_datetime(df["Order Date"])
print(df["Order Date"].min(), "to", df["Order Date"].max())
print("\nCATEGORICAL SUMMARY:")
for col in ["Category", "Sub-Category", "Region", "Segment"]:
    if col in df.columns:
        print(f"\n{col}:", df[col].unique())