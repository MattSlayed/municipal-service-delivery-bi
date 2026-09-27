"""Run the whole pipeline: download → scope → clean → star schema → reference values → report.

Usage: uv run python -m pipeline.run [--force-download]
"""

import argparse

from . import clean, config, download, model, reference, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force-download", action="store_true", help="re-download source files")
    args = parser.parse_args()

    paths = download.download(force=args.force_download)
    raw = clean.load_raw(paths[config.REQUESTS_FILE])
    scoped = clean.select_scope(raw)
    kept, quarantine = clean.clean(scoped)
    summary = report.dq_summary(len(raw), len(scoped), kept, quarantine)
    labelled = model.prepare_labels(kept)

    tables = model.build(labelled, paths[config.HEXAGONS_FILE])
    hexes = tables["dim_hex"]
    unmapped = hexes.loc[hexes["geometry"].isna() & hexes["hex_id"].ne(config.UNLOCATED_HEX), "hex_key"]
    summary.loc[len(summary)] = ["Hexagon missing from the City's polygon file",
                                 int(tables["fact_request"]["hex_key"].isin(unmapped).sum()),
                                 "Kept; not on the map"]
    tables["quarantine"] = quarantine.drop(columns=["created_at", "completed_at"])
    tables["dq_summary"] = summary
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_parquet(config.PROCESSED_DIR / f"{name}.parquet", index=False)

    expected = reference.compute(labelled, len(scoped), quarantine)
    reference.write(expected, config.PROCESSED_DIR / "reference_values.json")
    checksums = {name: download.sha256(path) for name, path in paths.items()}
    report.write_markdown(summary, checksums, expected["transparency"]["reconciles"])

    print(summary.to_string(index=False))
    print(f"\nReconciles: {expected['transparency']['reconciles']}")
    print(f"Tables written to {config.PROCESSED_DIR}")


if __name__ == "__main__":
    main()
