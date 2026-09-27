# Profile the City of Cape Town service-request dataset (download sr_hex.csv.gz first; see docs/research/data-profile.md).
import pandas as pd
df = pd.read_csv("sr_hex.csv.gz", dtype=str)
print("rows", len(df)); print("cols", list(df.columns))
for c in ["creation_timestamp","completion_timestamp"]:
    df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
print("created range", df.creation_timestamp.min(), "->", df.creation_timestamp.max())
print("completed range", df.completion_timestamp.min(), "->", df.completion_timestamp.max())
print("\nnull %:"); print((df.isna().mean()*100).round(1).to_string())
print("\ndirectorate:"); print(df.directorate.value_counts(dropna=False).head(15).to_string())
ws = df[df.directorate=="WATER AND SANITATION"].copy()
print("\nW&S rows", len(ws))
print("W&S open (no completion):", ws.completion_timestamp.isna().sum())
ws["days"] = (ws.completion_timestamp-ws.creation_timestamp).dt.total_seconds()/86400
print("W&S days to complete: median %.2f  p90 %.1f  neg %d" % (ws.days.median(), ws.days.quantile(.9), (ws.days<0).sum()))
print("\nW&S department:"); print(ws.department.value_counts(dropna=False).head(10).to_string())
print("\nW&S branch:"); print(ws.branch.value_counts(dropna=False).head(12).to_string())
print("\nW&S section count:", ws.section.nunique())
print(ws.section.value_counts().head(12).to_string())
print("\nW&S code_group:"); print(ws.code_group.value_counts(dropna=False).head(10).to_string())
print("\nW&S code top 15:"); print(ws.code.value_counts(dropna=False).head(15).to_string())
print("\nW&S cause_code top 10:"); print(ws.cause_code.value_counts(dropna=False).head(10).to_string())
print("\nW&S suburbs", ws.official_suburb.nunique(), " hexes", ws.h3_level8_index.nunique(), " h3 '0' share", (ws.h3_level8_index=="0").mean().round(3))
print("\nW&S monthly created:"); print(ws.set_index("creation_timestamp").resample("MS").size().to_string())
