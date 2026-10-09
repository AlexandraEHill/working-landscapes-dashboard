"""About the data: what the numbers mean and how far to trust them."""

import pandas as pd
import streamlit as st

from common import (
    ALL_WL, MEASURES, REPORT_URL, SEGMENT_ABOUT, SEGMENTS,
    ca_share, california, fmt, load, numbers, pct, place_view, region_counties, times,
)

county_segments, county_totals, states, industries = load()
_, ca_segments, ca_total = california()

st.title("About the data")
st.write(
    "This dashboard is a companion to the UC Agriculture and Natural Resources report "
    "*California's Working Landscapes: Evolving Contributions to National, State, and "
    "Regional Economies* (Dompka, Hill and Wilcher, 2025). It shows the same data as the "
    "report, for the year 2024."
)
st.link_button("Read the full report", REPORT_URL, icon=":material/open_in_new:")

st.header("What counts as working landscapes")
st.write(
    f"The report groups {len(industries)} detailed industries (NAICS codes) into nine "
    "segments. Those industries are taken out of their usual sectors, so the working "
    "landscapes sector can be compared with the rest of the economy without counting "
    "anything twice."
)
for segment in SEGMENTS:
    st.markdown(f"- **{segment}.** {SEGMENT_ABOUT[segment]}")
numbers(
    industries[["industry", "naics", "segment"]].rename(
        columns={"industry": "Industry", "naics": "NAICS code", "segment": "Segment"}
    ).astype({"NAICS code": str}),
    limit=10,
    key="industry_list",
)

st.header("The four measures")
for label, m in MEASURES.items():
    st.markdown(f"- **{label}.** {m['help']}")

st.header("Sales are not GDP")
st.write(
    "Sales are gross receipts. When a grower sells to a processor and the processor "
    "sells to a distributor, each sale is counted, so sales add up to more than the "
    "value of what was finally produced. California's sales across all industries "
    f"total about {fmt(ca_total['sales'], True).replace('$', chr(92) + '$')}, while state GDP is about "
    "\\$4 trillion. Use sales to compare the size of sectors, not as a measure of value added."
)

st.header("Why county and region numbers can be low")
gap = ca_segments.loc[ALL_WL, "businesses"] - county_segments["businesses"].sum()
st.write(
    "Figures for small industries in a single county are sometimes withheld to protect "
    "the confidentiality of individual businesses. County and region figures here are "
    "added up from what is reported, so they can be lower than the truth, and regional "
    "figures do not always add up to the statewide totals. For example, the counties "
    f"together report about {fmt(gap)} fewer working landscapes businesses than the "
    "statewide figure. Where the dashboard says \"none reported\", it does not mean "
    "there is no activity."
)

st.header("Regions")
st.write(
    "Counties are grouped into the 13 California Jobs First regions, which bring "
    "together counties with shared economic ties."
)
st.table(
    pd.DataFrame(
        [(region, ", ".join(counties)) for region, counties in sorted(region_counties().items())],
        columns=["Region", "Counties"],
    ).set_index("Region")
)

st.header("Specialization (location quotient)")
example = place_view("County", "Agricultural Production", "jobs").loc["Fresno"]
st.write(
    "Specialization compares how large a segment is in a local economy with how large "
    "it is in California as a whole. It is the segment's share of the local total "
    "divided by the segment's share of the California total."
)
st.write(
    f"For example, agricultural production provides {pct(example['share'])} of jobs in "
    f"Fresno County and {pct(ca_share('Agricultural Production', 'jobs'))} of jobs in "
    f"California, so Fresno County's specialization is {times(example['spec'])}. "
    "A value of 1x means the same as the state. On the *Segments and the nation* page "
    "the same calculation compares each state with the United States."
)
st.write(
    "Because county figures can be understated, specialization for a county or region "
    "is, if anything, too low. In very small counties a handful of employers can "
    "produce a very high value."
)

st.header("One year only")
st.write(
    "All figures are for 2024. The dashboard does not show trends. The 2019 edition of "
    "the report used an older set of industry codes and different regions, so its "
    "figures are not directly comparable."
)

st.header("Accessibility")
st.markdown(
    "This dashboard is designed to follow the Web Content Accessibility Guidelines "
    "(WCAG) 2.1, Level AA.\n\n"
    "If you have trouble using any part of the dashboard, or need the information in "
    "another format, please contact the author at "
    "[alihill@berkeley.edu](mailto:alihill@berkeley.edu) or see "
    "[UC ANR Digital Accessibility](https://ucanr.edu/dept/digital-accessibility)."
)

st.header("Source and citation")
st.markdown(
    "Data come from Lightcast (version 2025.1), which combines the Quarterly Census of "
    "Employment and Wages with other federal sources and covers employees, the "
    "self-employed and proprietors.\n\n"
    "Suggested citation: Dompka, A., Hill, A. E., and Wilcher, A. (2025). *California's "
    "Working Landscapes: Evolving Contributions to National, State, and Regional "
    f"Economies.* University of California Agriculture and Natural Resources. {REPORT_URL}"
)
