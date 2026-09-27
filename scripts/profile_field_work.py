# Profile the City of Cape Town service-request dataset (download sr_hex.csv.gz first; see docs/research/data-profile.md).
import pandas as pd
df = pd.read_csv("sr_hex.csv.gz", dtype=str)
for c in ["creation_timestamp","completion_timestamp"]:
    df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
ws = df[df.directorate=="WATER AND SANITATION"].copy()
field = ["SEWER","WATER","WATER MANAGEMENT DEVICE","SEWER - INFORMAL SETTLEMENTS","WATER  - INFORMAL SETTLEMENTS"]
f = ws[ws.code_group.isin(field)].copy()
print("field-work rows", len(f), "share of W&S %.1f%%" % (100*len(f)/len(ws)))
print("latlong null % (field):", round(f.latitude.isna().mean()*100,1), " h3 '0' %:", round((f.h3_level8_index=='0').mean()*100,1))
f["days"]=(f.completion_timestamp-f.creation_timestamp).dt.total_seconds()/86400
g=f.groupby("section").agg(n=("days","size"),median=("days","median"),p90=("days",lambda s:s.quantile(.9))).sort_values("n",ascending=False)
print(g.round(1).head(8).to_string())
print("\nby code_group:"); print(f.groupby("code_group").days.agg(["size","median",lambda s:s.quantile(.9)]).round(1).to_string())
# open at month-ends
for d in ["2020-03-31","2020-06-30","2020-09-30","2020-12-31"]:
    t=pd.Timestamp(d+" 23:59:59",tz="Africa/Johannesburg")
    o=((f.creation_timestamp<=t)&((f.completion_timestamp>t)|f.completion_timestamp.isna())).sum()
    print("open at",d,o)
print("duplicates same code+hex+day:", f.assign(day=f.creation_timestamp.dt.date).duplicated(["code","h3_level8_index","day"]).sum())
