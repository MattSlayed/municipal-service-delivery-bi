// Render the Operations Map spec outside Power BI, to check it before pasting it into Deneb.
//
//   npm install --no-save vega@5 vega-lite@5
//   node powerbi/deneb/render-test.mjs data/processed/map/2020-12-31.json map.svg
//
// The spec is used unchanged except that Deneb's "dataset" is replaced by the pipeline's map rows
// and "container" sizing (which needs Power BI's visual container) by a fixed size.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as vega from "vega";
import * as vl from "vega-lite";

const [dataPath, outPath = "map.svg"] = process.argv.slice(2);
const specPath = path.join(path.dirname(fileURLToPath(import.meta.url)), "operations-map.vl.json");
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
spec.data = { values: JSON.parse(fs.readFileSync(dataPath, "utf8")) };
spec.width = 900;
spec.height = 760;

const view = new vega.View(vega.parse(vl.compile(spec).spec), { renderer: "none" });
fs.writeFileSync(outPath, await view.toSVG());
console.log(`Wrote ${outPath}; open it in a browser.`);
