# Count how many field-work rows each proposed cleaning rule would touch (download sr_hex.csv.gz first).
import pandas as pd
df = pd.read_csv("sr_hex.csv.gz", dtype=str)
raw=len(df)
print("raw rows", raw)
print("exact duplicate rows (all columns):", df.duplicated().sum())
print("duplicate notification_number:", df.notification_number.duplicated().sum())
for c in ["creation_timestamp","completion_timestamp"]:
    df[c+"_p"] = pd.to_datetime(df[c], utc=True, errors="coerce")
print("unparseable creation:", df.creation_timestamp_p.isna().sum(), " unparseable completion (non-null raw):", (df.completion_timestamp.notna() & df.completion_timestamp_p.isna()).sum())
ws = df[df.directorate=="WATER AND SANITATION"]
field = ["SEWER","WATER","WATER MANAGEMENT DEVICE","SEWER - INFORMAL SETTLEMENTS","WATER  - INFORMAL SETTLEMENTS"]
f = ws[ws.code_group.isin(field)].copy()
print("\nfield scope rows", len(f))
print("field: dup notification_number", f.notification_number.duplicated().sum())
d=(f.completion_timestamp_p-f.creation_timestamp_p).dt.total_seconds()
print("field: completed before created", (d<0).sum())
print("field: completed within 60s of creation", ((d>=0)&(d<60)).sum())
print("field: completed within 5 min", ((d>=0)&(d<300)).sum())
print("field: duration > 365 days", (d>365*86400).sum())
print("field: missing code", f.code.isna().sum(), " missing section", f.section.isna().sum())
print("field: lat null", f.latitude.isna().sum(), " h3=='0'", (f.h3_level8_index=="0").sum(), " both", (f.latitude.isna() & (f.h3_level8_index=="0")).sum())
lat=pd.to_numeric(f.latitude,errors="coerce"); lon=pd.to_numeric(f.longitude,errors="coerce")
print("field: coords outside Cape Town bbox", ((lat.notna()) & ~((lat.between(-34.4,-33.4)) & (lon.between(18.2,19.1)))).sum())
f["day"]=f.creation_timestamp_p.dt.tz_convert("Africa/Johannesburg").dt.date
loc=f[f.h3_level8_index!="0"]
rep=loc.duplicated(["code","h3_level8_index","day"])
print("\nlikely repeats (located rows only):", rep.sum(), "of", len(loc), "= %.1f%%" % (100*rep.mean()))
top=loc[rep].code.value_counts().head(8)
print(top.to_string())
# short-closure by code
short=f[(d>=0)&(d<300)]
print("\n<5 min closures by code:"); print(short.code.value_counts().head(8).to_string())
