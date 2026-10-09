"""California's Working Landscapes dashboard.

Run locally with:  streamlit run app.py
Each page lives in the views/ folder; shared helpers are in common.py.
"""

import streamlit as st

from common import MEASURES

st.set_page_config(page_title="California's Working Landscapes", page_icon="🌾", layout="wide")

# Tables come with a small hover toolbar that includes "Download as CSV".
# The data cannot be redistributed, so hide that toolbar everywhere.
st.html(
    """<style>
    [data-testid='stElementToolbar'] { display: none; }
    /* text for screen readers only (chart descriptions) */
    .sr-only { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
               overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
    </style>"""
)

page = st.navigation(
    [
        st.Page("views/overview.py", title="Overview", icon=":material/home:", default=True),
        st.Page("views/place.py", title="Your county or region", icon=":material/location_on:"),
        st.Page("views/compare.py", title="Compare places", icon=":material/map:"),
        st.Page("views/segments.py", title="Segments and the nation", icon=":material/category:"),
        st.Page("views/about.py", title="About the data", icon=":material/info:"),
    ],
    position="top",
)

# One measure switch shared by every page. The choice is copied into
# "measure_label" so it survives a visit to the About page, which hides it.
if page.title != "About the data":
    choice = st.segmented_control(
        "Measure",
        list(MEASURES),
        default=st.session_state.get("measure_label", "Jobs"),
        help="Every chart on the page switches to the measure you pick here.",
    )
    st.session_state["measure_label"] = choice or "Jobs"
    st.caption(MEASURES[st.session_state["measure_label"]]["help"])

# Give each page its own browser tab title, so screen reader users can tell them apart.
st.set_page_config(page_title=f"{page.title} | California's Working Landscapes")

page.run()

st.divider()
st.caption(
    "Source: UC Agriculture and Natural Resources, *California's Working Landscapes: "
    "Evolving Contributions to National, State, and Regional Economies* (2025). "
    "Lightcast V2025.1, 2024 data. County and region figures can be understated; "
    "see About the data."
)
