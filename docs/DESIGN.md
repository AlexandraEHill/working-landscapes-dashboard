# California Working Landscapes Dashboard: Design Spec

Companion to the UC ANR report *California's Working Landscapes: Evolving Contributions to
National, State, and Regional Economies* (Dompka, Hill, Wilcher, Nov 2025).
Data: Lightcast V2025.1, year 2024 only. Build target: stock Streamlit + Plotly Express.

## 1. Audiences and what each must be able to do in two minutes

| Audience | Arrives with | Leaves with |
|---|---|---|
| Agency / government staff | "How big is this sector?" | A quotable statewide number, its rank among sectors and states, and the source line |
| County / regional economic development staff | One county or one Jobs First region | What their place has, what it specializes in, how it compares with neighbors and the state, and a CSV |

Design consequences: every page opens with one sentence that states the finding; the only
controls are a place picker, a segment picker, and one measure switch; every chart has a
table and a download beneath it.

## 2. App structure (5 pages, `st.navigation`, top-level order as listed)

| # | Page title (nav label) | Question it answers | Main audience |
|---|---|---|---|
| 1 | Overview | How big are California's working landscapes, and what are they made of? | Agency |
| 2 | Your county or region | What does my place have, and what does it specialize in? | Local |
| 3 | Compare places | Where in California is a segment largest, and where does it matter most locally? | Both |
| 4 | Segments and the nation | What is inside a segment, and how does California rank among states? | Agency |
| 5 | About the data | What do these numbers mean and how far can I trust them? | Both |

Why not a separate "California in the nation" page: state rank is always asked about one
segment at a time, so it sits as a tab on the segment page. That keeps the nav to five items.

### Shared elements (defined once in the entrypoint file, so they appear on every page)

- **Measure switch**: `st.segmented_control`, label "Measure", options
  `Jobs | Sales | Earnings | Businesses`, default **Jobs**, key `measure`. Place it in the
  main body above the page content (not the sidebar: the sidebar is collapsed on phones).
  Hide it on "About the data". Default is Jobs, not Sales, because jobs do not double-count
  and are the number local practitioners quote. The Overview hero still shows all four.
- **Caption under the switch** (changes with the measure; text in section 8).
- **Footer on every page**, `st.caption`: "Source: UC ANR, *California's Working
  Landscapes* (2025). Lightcast V2025.1, 2024 data. County and region figures can be
  understated; see About the data."
- **Page pattern, top to bottom**: title, controls, takeaway sentence (`st.markdown`,
  slightly larger text, no box), `st.metric` row, chart(s), `st.expander("See the numbers")`
  holding `st.dataframe` + `st.download_button("Download this table (CSV)")`, caveat caption.
- No sidebar content other than the navigation.

## 3. Page 1: Overview

**Question:** How big are California's working landscapes, and what are they made of?

Layout:

1. Title "California's Working Landscapes, 2024". One-line subtitle: "Nine segments of
   the economy that depend on the state's land and natural resources: farming and the
   businesses that support, process and distribute its products, plus fishing, forestry,
   mining, outdoor recreation and renewable energy."
2. Takeaway (not measure dependent):
   "In 2024, California's working landscapes supported **{jobs}** jobs at **{businesses}**
   businesses, generating **{sales}** in sales and **{earnings}** in worker earnings."
3. Four `st.metric` tiles in `st.columns(4)` (stack 2x2 on phone automatically): Jobs,
   Sales, Earnings, Businesses. Each tile's `delta` slot is not used (no time series).
   Under each value use `help=` with the measure definition (section 8). Below each tile a
   caption: "{share}% of California's total".
4. **Chart 1A: sector ranking.**
   - Title: "Working landscapes rank {rank}th of {n_sectors} California sectors by {measure}"
   - Type: horizontal bar, one bar per high-level sector. x = measure value, y = sector
     name, sorted descending (largest at top).
   - Color: Working Landscapes bar in accent `#00796B`; all other bars neutral `#B8BDC4`.
     Text label on every bar = share of California total (e.g. "5.7%").
   - Hover: sector, value, share of California total, rank.
   - Help text under the title: "Working landscapes industries are removed from their
     usual sectors (for example, food manufacturing leaves Manufacturing) so nothing is
     counted twice."
5. **Chart 1B: the nine segments.**
   - Title: "What the sector is made of: {measure} by segment"
   - Type: horizontal bar, one bar per segment, sorted descending. Bars colored by segment
     (section 7); value labels at bar ends; no legend needed because y labels name each bar.
   - Hover: segment, value, share of working landscapes total, share of California total.
   - Takeaway above it: "**{top_segment}** is the largest segment by {measure}
     ({top_value}). The four agricultural segments together account for **{ag_share}%**
     of working landscapes {measure} ({ag_value})."
   - Help popover "What is a segment?": "A segment is a group of related industries.
     The report sorts about 195 detailed industries into nine segments."
6. **Chart 1C: regions at a glance.**
   - Title: "Working landscapes {measure} by California Jobs First region"
   - Type: horizontal stacked bar, one bar per region (13), x = measure value, color =
     segment, segments stacked in the fixed order of section 7 (agriculture first), regions
     sorted by total descending.
   - Hover: region, segment, value, segment's share of the region's working landscapes total.
   - Takeaway: "**{region_1}** and **{region_2}** are the largest contributors, with
     {combined_value} between them ({combined_share}% of the regional total)."
   - `st.page_link` under the chart: "Look up your county or region" → page 2.
7. Expander "See the numbers": three tables (sectors, segments, region x segment), each
   with a download button.
8. Caveat caption: region figures are sums of county data and can fall short of the
   statewide totals above (redaction).

Statewide figures on this page come from the **states file** (California row), so they
match the report's headline numbers. Chart 1C comes from the county file.

## 4. Page 2: Your county or region

**Question:** What does my place have, and what does it specialize in?

Controls (one row):

- `st.segmented_control` "Look at a": `County | Region`, default **Region**.
- `st.selectbox` "Choose a {county/region}": alphabetical; default **Central San Joaquin**
  (region) / **Fresno** (county). Selectbox is type-to-search.
- When a region is chosen, caption listing its counties: "Central San Joaquin = Fresno,
  Kings, Madera, Tulare counties." When a county is chosen: "{County} is part of the
  {Region} region."
- For the three single-county regions (Kern County, Los Angeles County, Orange County),
  both modes show the same numbers; add caption "This region is a single county."

Layout:

1. Takeaway:
   "In **{place}**, working landscapes account for **{wl_value}** {measure_noun}:
   **{wl_share}%** of the local total, compared with **{ca_share}%** statewide. The
   largest segment is **{top_segment}** ({top_value})."
   If the place has any segment with specialization >= 1.5 and at least 100 jobs, append:
   "Compared with California as a whole, {place} is most specialized in
   **{top_lq_segment}** ({lq}x the state average)."
2. `st.metric` row (4 tiles): the four measures for working landscapes in this place,
   each captioned "{share}% of all {measure_noun} in {place}".
3. **Chart 2A: segment profile.**
   - Title: "{measure} by segment in {place}, 2024"
   - Type: horizontal bar, nine segments, sorted descending, colored by segment, value
     labels at bar ends. Segments with no reported value are listed with the label "not
     reported" and no bar, not dropped. This needs the county file to distinguish redacted from true zero;
     if it cannot, label these "none reported".
   - Hover: segment, value, share of the place's total economy, share of the California
     segment total located here.
4. **Chart 2B: specialization.**
   - Title: "Where {place} is more specialized than California"
   - Type: horizontal dot plot (`px.scatter`, one row per segment) on a **log x axis**
     with tick labels "0.25x, 0.5x, 1x, 2x, 4x, 8x"; a vertical reference line at 1x
     annotated "Same as California". Sort descending by value. Points colored by segment;
     segment names on the y axis.
   - x = specialization = (segment share of place's {measure}) / (segment share of
     California's {measure}).
   - Hover: segment, "{lq}x the California average", local share %, California share %,
     the absolute value.
   - Help popover "How to read this": "A value of 2x means this segment makes up twice
     as large a share of the local economy as it does statewide. 1x means the same as
     California. This is often called a location quotient."
   - Guard: where the segment has fewer than 100 jobs in the place, draw the point hollow
     and add to hover "Small numbers: treat with caution."
5. **Table 2C: full profile** (visible, not in an expander, since this audience wants
   lookup). Rows = nine segments + "All working landscapes" + "All industries". Columns:
   Jobs, Sales, Earnings, Businesses, Share of local {measure}, Specialization vs
   California. Download button: "Download {place} profile (CSV)".
6. If Region mode: expander "Counties in this region" with a horizontal bar of working
   landscapes {measure} by member county, sorted descending, single color.
7. Caveat caption: "County data are subject to confidentiality redaction, so some small
   segments may be understated or missing. A missing value does not mean zero activity."

## 5. Page 3: Compare places

**Question:** Where in California is a segment largest, and where does it matter most locally?

Controls (one row, three items):

- `st.selectbox` "Segment": "All working landscapes" (default) + nine segments.
- `st.segmented_control` "Compare": `Regions | Counties`, default **Regions**.
- `st.segmented_control` "Show as": `Total | Share of local economy | Specialization`,
  default **Total**. Help: "Total = how much. Share = how much it matters locally.
  Specialization = local share compared with California's share (1x = same as the state)."

Layout:

1. Takeaway by "Show as":
   - Total: "**{top_place}** has the most {segment} {measure_noun} ({top_value}),
     followed by {second} and {third}. The top three account for **{top3_share}%** of the
     {geo_level} total."
   - Share: "{segment} matters most to the local economy in **{top_place}**, where it
     is **{top_share}%** of all {measure_noun} (California: {ca_share}%)."
   - Specialization: "**{top_place}** is the most specialized in {segment}, at
     **{lq}x** the California average."
2. **Chart 3A: ranked bar** (always shown; this is the primary geography view).
   - Title: "{segment} {measure} by {region/county}, 2024" (append "as a share of each
     local economy" or "specialization compared with California" per "Show as").
   - Type: horizontal bar, sorted descending. Regions: all 13. Counties: top 20 by
     default with a `st.toggle("Show all 58 counties")`; when all are shown set figure
     height to about 22 px per bar.
   - Color: single color. The segment's own color when one segment is chosen; accent
     `#00796B` for "All working landscapes". In Share and Specialization modes add a
     vertical reference line for the California value (labelled "California {x}%" or "1x").
   - Hover: place, region (in county mode), value, share of local economy, specialization,
     rank "{n} of {N}".
3. **Chart 3B: county map (enhancement, only if `data/` contains a county boundary file).**
   - Shown in a second `st.tab` next to the bar chart: tabs "Ranked list" (default) and
     "Map". If the boundary file is absent, do not render the tabs at all; show 3A alone.
   - `px.choropleth` with county GeoJSON, `fitbounds="locations"`, no basemap. Always
     county-level. In Regions mode each county is colored with **its region's** value and
     the hover names the region, so the map and bar chart agree.
   - Sequential single-hue scale (section 7). Total mode: values span orders of magnitude,
     so bin into 5 quantile classes with a discrete legend rather than a continuous scale.
     Specialization mode: 5 fixed classes (<0.5x, 0.5-0.9x, 0.9-1.1x, 1.1-2x, >2x) on the
     diverging scale. Counties with no reported value: light gray with a "Not
     reported" legend entry.
   - Hover: same as 3A. The map never carries information the bar chart lacks.
4. Expander "See the numbers": table of all places with the four measures for the chosen
   segment, share, specialization, rank. Download button.
5. Caveats: redaction caption (as page 2). In Share/Specialization mode with Counties add:
   "Small counties can show very high shares from a handful of employers."

## 6. Page 4: Segments and the nation

**Question:** What is inside a segment, and how does California rank among states?

Control: `st.selectbox` "Segment": "All working landscapes" + nine segments; default
**Agricultural Production**. (Uses the same session key as page 3 so the choice carries over.)

Top of page:

1. One-sentence segment description taken from the report chapter openers, for example
   "Agricultural production includes crop and animal production: farming and ranching."
   Store these nine sentences in a small dict; wording must be approved by the authors.
2. Takeaway: "California's {segment} segment supported **{jobs}** jobs and **{sales}** in
   sales in 2024. By {measure}, California ranks **#{rank}** among states, with
   **{us_share}%** of the US total."
3. `st.metric` row: four measures for the segment statewide, each captioned
   "#{rank} among states, {us_share}% of US".

Then two `st.tabs`:

**Tab "California among the states"** (default)

- **Chart 4A.** Title: "{segment} {measure}: California and the other leading states".
  Horizontal bar, top 15 states by the measure, sorted descending; if California is outside
  the top 15, append it as a 16th bar with its rank in the label. California bar in the
  segment color, others neutral gray. Bar labels = share of US total ("12.3%").
  Hover: state, value, share of US total, rank of 51.
- `st.segmented_control` "Show as": `Total | Specialization vs US`, default Total.
  Specialization = state's segment share of its own economy / US segment share. Takeaway
  line in that mode: "{segment} is **{lq}x** as large a part of California's economy as it
  is of the US economy; California ranks #{lq_rank} on this basis." Help: "Large states
  lead most totals. Specialization shows where a segment is an unusually large part of the
  state economy."
- Note: "51 = 50 states plus the District of Columbia."
- No US state map: a ranked bar answers "where does California stand" more directly, and
  it avoids a second boundary file.

**Tab "Industries in this segment"**

- **Chart 4B.** Title: "Largest industries in California's {segment} segment, by {measure}".
  Horizontal bar, top 15 NAICS industries, sorted descending, single segment color. y label
  = industry name (truncate at about 45 characters; full name and NAICS code in hover).
  Hover: industry name, NAICS code, value, share of segment, California's share of US for
  that industry.
- Takeaway: "The largest industry is **{top_industry}** ({top_value},
  **{top_share}%** of the segment). The top five industries make up {top5_share}%."
- When "All working landscapes" is selected, color bars by segment and show the legend.
- Table (visible): all industries in the segment with NAICS code, four measures, share of
  segment, California share of US, California rank. Download button.
- Caption: "Industry detail is available for California as a whole only, not for counties
  or regions."

Expander "See the numbers" on the states tab: all 51 with four measures, share of US,
rank, specialization. Download button.

## 7. Page 5: About the data

Plain `st.markdown`, short headed sections, no charts:

1. **What counts as working landscapes**: nine segments, about 195 NAICS industries, list
   of segments with the one-line descriptions; downloadable NAICS-to-segment table.
2. **The four measures**: definitions from section 8, long form.
3. **Sales are not GDP**: "Sales are gross receipts. When a grower sells to a processor
   and the processor sells to a distributor, each sale is counted, so sales add up to more
   than the value of what was finally produced. California's sales across all industries
   total about $7.1 trillion; state GDP is about $4 trillion. Use sales to compare the
   size of sectors, not as a measure of value added."
4. **Why county and region numbers can be low**: confidentiality redaction; regional sums
   may not equal statewide totals; missing is not zero.
5. **Regions**: the 13 California Jobs First regions with their counties (table from the
   crosswalk).
6. **Specialization (location quotient)**: formula in words, a worked example using real
   numbers from one county.
7. **One year only**: 2024; no trends; the 2019 report used different industry codes and
   regions, so figures are not directly comparable.
8. **Source and citation**: suggested citation, link to the report PDF, Lightcast version,
   contact. "Download all dashboard data" button (zip or three CSVs).

## 8. Wording, formatting, color

### Measure labels (use exactly these everywhere)

| Key | Label | Noun in sentences | Axis / unit label | Help text (tooltip) |
|---|---|---|---|---|
| jobs | Jobs | jobs | Jobs, 2024 | Annual average number of jobs, including employees and the self-employed. A job is a position, not a person; part-time and seasonal jobs count. |
| sales | Sales | in sales | Sales, 2024 (US$) | Total annual sales (gross receipts) of businesses. Sales count goods each time they change hands, so they are larger than GDP. |
| earnings | Earnings | in worker earnings | Worker earnings, 2024 (US$) | Wages, salaries, benefits and income of business owners who work for themselves. |
| businesses | Businesses | businesses | Business locations, 2024 | Business locations with a payroll. A company with three sites counts three times; self-employed people without employees are not counted. |

Caption under the measure switch = the help text for the selected measure.

Other fixed vocabulary: "segment" (never "sub-sector"), "sector" for the 19 high-level
groups, "region" = California Jobs First region, "specialization" as the on-screen word
with "(location quotient)" given once in help text, "share of local economy" for a
segment's percent of a place's all-industry total.

### Number formatting (one helper function, used for metrics, labels, hover, sentences)

| Kind | Rule | Examples |
|---|---|---|
| Dollars | 3 significant figures, suffix K/M/B/T, no space | $404B, $71.7B, $668M, $2.38B, $7.1T |
| Counts >= 1,000,000 | 1 decimal + M | 1.5M |
| Counts 10,000 to 999,999 | round to nearest 100, thousands comma | 298,900; 75,500 |
| Counts < 10,000 | exact, thousands comma | 4,300; 918 |
| Shares | 1 decimal + %; "<0.1%" when below 0.05 | 5.7%, 12.3%, <0.1% |
| Specialization | 1 decimal + x; 2 decimals below 1 | 2.4x, 0.65x |
| Ranks | "#1", "7th of 19" | |
| Missing / redacted | "not reported" in text, "–" in tables | |

Tables in "See the numbers" show full unrounded values (CSV always unrounded). Axis ticks
use the same suffix style ($50B, 100K). Never show more precision in a sentence than in
the matching chart label.

### Segment colors

> **As built:** the palette below was replaced after a color-vision check showed Forestry and
> Mining (and the teals against gray) merging under red-green color blindness. The app uses a
> green family for agriculture plus near-black, gray, yellow, pink and blue; see
> `SEGMENT_COLORS` in `common.py`. Other as-built changes: navigation sits in a top bar, chart
> titles are page headings rather than Plotly titles, and zero county values are labelled
> "none reported" because the source file cannot tell redacted from zero.

Agricultural segments are one teal-green family ordered dark to light along the supply
chain; the other five are separate hues. Fixed stacking and legend order as listed.

| Order | Segment | Hex |
|---|---|---|
| 1 | Agricultural Production | `#00441B` |
| 2 | Agricultural Support | `#00796B` |
| 3 | Agricultural Processing | `#35A79C` |
| 4 | Agricultural Distribution | `#9AD9CF` |
| 5 | Forestry | `#882255` |
| 6 | Mining | `#555555` |
| 7 | Renewable Energy | `#E69F00` |
| 8 | Outdoor Recreation | `#D55E00` |
| 9 | Fishing | `#3B4CC0` |

Other colors: accent (all working landscapes, highlighted bar) `#00796B`; neutral
comparison bars `#B8BDC4`; reference lines and annotations `#333333`; "not reported"
`#E6E6E6`. Sequential map scale: Plotly `Teal` binned to 5 classes. Diverging scale for
specialization: `#8C510A, #D8B365, #F5F5F5, #5AB4AC, #01665E` (brown below 1x, teal above).

Rules that keep color from being the only signal:

- Segment colors are used for identity only in three charts (1B, 1C, 2A/2B); elsewhere a
  chart is single-color with one highlighted bar.
- Every colored bar has a text axis label; stacked chart 1C is the only one that relies on
  a legend, and its hover and table give the segment name.
- The four teal shades differ in lightness, not hue, so they stay distinguishable in
  grayscale. The two lightest need a thin `#FFFFFF` bar outline (`marker_line_width=0.5`).
- Before launch, run the palette once through a color-vision simulator (deuteranopia and
  protanopia); the pair to check is Outdoor Recreation vs Renewable Energy.

### Chart conventions

- All charts `st.plotly_chart(fig, use_container_width=True)`; Plotly template
  `plotly_white`; mode bar hidden except "download as PNG".
- Horizontal bars only (long names, phone width). Left margin sized for labels; value
  labels outside bar ends; x axis starts at zero (except the log specialization axis).
- Titles state the finding or the exact content; the year 2024 appears in the title or
  the axis label of every chart.
- No pies, treemaps, dual axes, or animated transitions.
- Phone width: `st.columns` collapse on their own; keep bar counts at or below 20 by
  default; nothing depends on hover (labels and tables carry the values).

## 9. Computation notes for the implementer

- Statewide and national figures: states file. County and region figures: county file.
  Never mix the two in one chart except the labelled California reference line.
- Region value = sum of member counties; region share = sum of segment values / sum of
  county all-industry totals (do not average county percentages).
- Specialization for a place = place segment share / California segment share, where the
  California share comes from the states file. Because place numerators can be redacted,
  this is conservative (understates, never overstates).
- "Share of California segment located here" (hover on 2A) uses the sum of counties as
  the denominator, labelled "share of the county-reported total".
- Sector rank on chart 1A is computed from the data, not hard-coded, and should reproduce
  "7th by sales, 5.7%". Add an automated check that the California working landscapes
  totals reproduce $404B / 1.5M / $103B / 75,500 and fail loudly otherwise.
- Cache loads with `st.cache_data`. Precompute tidy long tables: `place x segment x
  measure`, `state x segment x measure`, `CA industry x measure`, `CA sector x measure`.

## 10. Deliberately left out

- **Trends or change since the 2019 report.** One year of data; different NAICS vintage
  and regions make the two reports non-comparable.
- **Industry (NAICS) detail for counties or regions.** Not in the data.
- **GDP or value added, multipliers, indirect and induced effects.** Data are direct
  sales, jobs, earnings and establishments only.
- **Earnings per job / average wage.** Computable, but jobs mix full-time, seasonal and
  self-employed positions, so the ratio invites wrong wage comparisons. Could be added
  later as a table-only column with a warning.
- **County-to-US specialization.** One benchmark (California) for places and one (US)
  for the state keeps "1x" meaning a single thing on each page.
- **Other states' counties, and a US state map.** Ranked bars answer the national question.
- **Free multi-place selection and scatterplots.** Ranked lists with a highlighted place
  serve the same need with fewer controls.
- **Per-person or per-acre rates.** No population or land-area data in the project.
- **Report case-study sidebars and policy narrative.** Link to the report instead.
- **Custom components, user accounts, saved views.** Stock Streamlit only.
