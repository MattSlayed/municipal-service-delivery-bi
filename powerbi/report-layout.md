# Report layout

Page size 1920 × 1080 (16:9, Desktop's standard page). Every position below was drawn for 1280 × 720 and is scaled by 1.5 here. Positions are in pixels: set them in
**Format visual → General → Properties → Size and position**. Margins are 24 px and gaps 18 px on this page.
Colours come from the theme in [`theme/municipal-operations.json`](theme/municipal-operations.json);
the few set by hand are listed with each visual.

## Page 1: Director overview

The page answers the Director's first question: *do we call in contractors this week, and where?*

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Report Title (card)                                  │ As-at date      │ Threshold     │  y 12
├──────────────────────────────────────────────────────────────────────────────────────┤
│ Contractors needed │ Open now │ Active │ Stuck │ Weeks to clear  (one card, 5 values) │  y 72
├────────────────────────────────────────────────┬─────────────────────────────────────┤
│ Weeks to clear by section (bar)                │ Suburb ranking (table)              │  y 176
│   red = call contractors, blue = field crew,   │                                     │
│   grey = administrative; dashed threshold line ├─────────────────────────────────────┤
│                                                │ Active work with no suburb (card)   │  y 408
├────────────────────────────────────────────────┼─────────────────────────────────────┤
│ Open work each day of 2020: active and stuck   │ Requests in and completions by week │  y 460
│ (stacked area)                                 │ (two lines)                         │
└────────────────────────────────────────────────┴─────────────────────────────────────┘
```

### 1. Theme and page

- **View → Themes → Browse for themes** → `powerbi/theme/municipal-operations.json`.
- Rename the page *Director overview* (double-click its tab).

### 2. Header

| Visual | Position (x, y, w, h) | Fields and settings |
|---|---|---|
| **Card (new)** | 24, 18, 1140, 72 | Data: `Report Title`. Callout value: font 18, left aligned. Turn off the category label and the visual title. |
| **Slicer**: as-at date | 1188, 18, 330, 72 | Field: `as_at[as_at_date]`. Slicer settings → Style: **Before**. Set the date to 31/12/2020. Title: *As at*. |
| **Slicer**: threshold | 1542, 18, 354, 72 | Field: `Threshold[Threshold]` (single-value slider). Title: *Contractor threshold (weeks)*. |

The as-at slicer in *Before* style keeps every date up to the chosen one, so `MAX(as_at_date)`
in the measures is the chosen date.

### 3. Headline numbers

One **Card (new)** at 24, 108, 1872, 138 with five values, in this order:

| Value | Label (rename in the Data well: double-click) | Reference label |
|---|---|---|
| `Flagged Sections` | Sections needing contractors | `Flagged Section Names` |
| `Open Now` | Open now | |
| `Active` | Active (90 days or less) | |
| `Stuck` | Stuck (over 90 days) | |
| `Weeks to Clear` | Weeks to clear, department | |

Format → Layout: 5 columns in one row.

### 4. Weeks to clear by section

**Clustered bar chart** at 24, 264, 1110, 408.

- Y-axis: `dim_section[section]`. X-axis: `Weeks to Clear`. Sort by Weeks to Clear, descending.
- Bars → Color → **fx** → Format style *Field value* → `Section Bar Colour`.
- Data labels on, one decimal.
- Tooltips: `Flag Status`, `Active`, `Avg Weekly Completions`.
- Analytics pane (magnifier icon) → **X-axis constant line** → Add → Value **fx** → `Threshold Value`.
  Colour `#0B0B0B`, style dashed, data label on with the text *Threshold*.
- Title → **fx** → `Weeks to Clear Title`.

Sections with too few completions have no bar: their weeks to clear is blank by design.

### 5. Suburb ranking

**Table** at 1152, 264, 744, 336.

- Columns: `dim_suburb[suburb]`, `Suburb Rank`, `Active`, `Weeks to Clear`.
- Filters on this visual: `Suburb Rank` *is less than or equal to* 10. This also removes blank
  ranks: Unknown suburb, unflagged sections, suburbs with no active work.
- Sort by Suburb Rank, ascending.
- Title → **fx** → `Suburb Table Title`.

Clicking a red bar in the chart filters this table to that section.

### 6. Active work with no suburb

**Card (new)** at 1152, 612, 744, 60. Data: `Unknown Suburb Active`, label *Active work with no
suburb in this selection*. No contractor can be sent to these, so they sit beside the ranking.

### 7. Open work over time

**Stacked area chart** at 24, 690, 924, 372.

- X-axis: `as_at[as_at_date]`. Y-axis: `Active`, `Stuck`.
- Colours: Active `#2A78D6`, Stuck `#EB6834`. Legend on, top left.
- Title: *Open work on each day of 2020: active and stuck*.
- Subtitle: *Requests created before 2020 are not in the data, so open work is understated
  early in the year.*
- **Format → Edit interactions**: select the as-at slicer, then set this chart to **None**, so it
  always shows the whole year.

### 8. Weekly flow

**Line chart** at 966, 690, 930, 372.

- X-axis: `dim_date[week_start]`. Y-axis: `Requests In`, `Completions`.
- Filter on this visual: `week_start` *is on or after* 06/01/2020 **and** *is on or before*
  28/12/2020 (the full Monday-to-Sunday weeks of 2020).
- Colours: Requests In `#4A3AA7`, Completions `#008300`. Legend on, top left.
- Title: *Requests in and completions per week, 2020*.
- Edit interactions: as-at slicer → **None**, as for the area chart.

## Colour rules

- Red `#D03B3B` means one thing: *call contractors*. It is never a series colour, and it always
  comes with the text label from `Flag Status` (tooltip) or the section's name in the headline.
- Blue and orange are active and stuck work wherever they appear; violet and green are requests
  in and completions. A filter never repaints them.
- Every pair was checked for colour-blind separation and contrast with the dataviz validator.
