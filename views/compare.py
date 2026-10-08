"""Compare places: where is a segment largest, and where does it matter most locally?"""

import pandas as pd
import plotly.express as px
import streamlit as st

from common import (
    ACCENT, ALL_WL, MEASURES, REDACTION_NOTE, SEGMENT_COLORS, SEGMENTS,
    ca_share, current_measure, fmt, hbar, load_map, numbers, pct, place_view,
    region_counties, show, takeaway, times,
)

NONE = "None reported"
GREY = "#e6e6e6"
BLUES = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # light = low
SPEC_CLASSES = {  # brown below the California average, teal above
    "Under 0.5x": "#8c510a",
    "0.5x to 0.9x": "#d8b365",
    "0.9x to 1.1x (about the same)": "#f5f5f5",
    "1.1x to 2x": "#5ab4ac",
    "Over 2x": "#01665e",
}

label, measure = current_measure()
key, money = measure["key"], measure["money"]

st.title("Compare places")

c1, c2, c3 = st.columns([2, 1, 2])
segment = c1.selectbox("Segment", [ALL_WL] + SEGMENTS)
level = c2.segmented_control("Compare", ["Regions", "Counties"], default="Regions") or "Regions"
mode = c3.segmented_control(
    "Show as",
    ["Total", "Share of local economy", "Specialization"],
    default="Total",
    help="Total = how much. Share = how much it matters locally. Specialization = "
    "local share compared with California's share (1x = same as the state).",
) or "Total"

level = level[:-1].replace("ie", "y")  # "Regions" -> "Region", "Counties" -> "County"
column = {"Total": "value", "Share of local economy": "share", "Specialization": "spec"}[mode]
view = place_view(level, segment, key).sort_values(column, ascending=False)
name = "Working landscapes" if segment == ALL_WL else segment
state_share = ca_share(segment, key)


def show_value(row):
    """The label for one place in the current "Show as" mode."""
    if row["value"] == 0:
        return "none reported"
    return {"value": fmt(row["value"], money), "share": pct(row["share"]), "spec": times(row["spec"])}[column]


def hover(place, row, rank):
    where = f"{place} County" if level == "County" else place
    return (
        f"<b>{where}</b><br>{fmt(row['value'], money)} {measure['noun']}<br>"
        f"{pct(row['share'])} of the local economy<br>{times(row['spec'])} the California average<br>"
        f"Rank {rank} of {len(view)}"
    )


# ---- takeaway
top = view.index[:3]
if mode == "Total":
    takeaway(
        f"**{top[0]}** has the most {name.lower()} {measure['noun']} ({fmt(view['value'].iloc[0], money)}), "
        f"followed by {top[1]} and {top[2]}. The top three account for "
        f"**{pct(100 * view['value'].iloc[:3].sum() / view['value'].sum())}** of the {level.lower()} total."
    )
elif mode == "Share of local economy":
    takeaway(
        f"{name} matters most to the local economy in **{top[0]}**, where it is "
        f"**{pct(view['share'].iloc[0])}** of all {measure['noun']} (California: {pct(state_share)})."
    )
else:
    takeaway(
        f"**{top[0]}** is the most specialized in {name.lower()}, at "
        f"**{times(view['spec'].iloc[0])}** the California average."
    )

suffix = {"Total": "", "Share of local economy": " as a share of each local economy",
          "Specialization": ": specialization compared with California"}[mode]
st.subheader(f"{name} {measure['noun']} by {level.lower()}, 2024{suffix}")

geojson = load_map()
if geojson:
    list_tab, map_tab = st.tabs(["Ranked list", "Map"])
else:
    list_tab, map_tab = st.container(), None

# ---- ranked bars (the main view)
with list_tab:
    shown = view
    if level == "County" and not st.toggle("Show all 58 counties"):
        shown = view.head(20)
        st.caption("Showing the top 20 counties.")
    reference = {
        "Total": None,
        "Share of local economy": (state_share, f"California {pct(state_share)}"),
        "Specialization": (1, "Same as California (1x)"),
    }[mode]
    axis = {"Total": f"{label}, 2024", "Share of local economy": f"Share of all local {measure['noun']}",
            "Specialization": "Local share compared with California's share"}[mode]
    show(
        hbar(
            shown.index,
            shown[column].values,
            [show_value(row) for _, row in shown.iterrows()],
            ACCENT if segment == ALL_WL else SEGMENT_COLORS[segment],
            [hover(place, row, i) for i, (place, row) in enumerate(shown.iterrows(), 1)],
            axis,
            reference=reference,
        )
    )

# ---- county map (same numbers as the list)
if map_tab:
    with map_tab:
        counties = pd.DataFrame(
            [(c, r) for r, members in region_counties().items() for c in members],
            columns=["county", "region"],
        )
        counties["place"] = counties["county" if level == "County" else "region"]
        counties = counties.join(view, on="place")
        ranks = {place: i for i, place in enumerate(view.index, 1)}
        counties["hover"] = [hover(row["place"], row, ranks[row["place"]]) for _, row in counties.iterrows()]

        reported = counties["value"] > 0
        counties["class"] = NONE
        if mode == "Specialization":
            counties.loc[reported, "class"] = pd.cut(
                counties.loc[reported, "spec"], [0, 0.5, 0.9, 1.1, 2, float("inf")], labels=list(SPEC_CLASSES)
            ).astype(str)
            colors = dict(SPEC_CLASSES)
        else:
            # Five groups with roughly equal numbers of places; values span
            # orders of magnitude, so a continuous scale would hide most of them.
            values = view.loc[view["value"] > 0, column]
            edges = sorted(set(values.quantile([0, 0.2, 0.4, 0.6, 0.8, 1])))
            show_edge = (lambda v: fmt(v, money)) if mode == "Total" else pct
            names = [f"{show_edge(a)} to {show_edge(b)}" for a, b in zip(edges, edges[1:])]
            if len(edges) > 1:
                counties.loc[reported, "class"] = pd.cut(
                    counties.loc[reported, column], edges, labels=names, include_lowest=True, ordered=False
                ).astype(str)
            else:
                names = [show_edge(edges[0])]
                counties.loc[reported, "class"] = names[0]
            colors = dict(zip(names, BLUES[-len(names):]))
        colors[NONE] = GREY

        fig = px.choropleth(
            counties,
            geojson=geojson,
            locations="county",
            color="class",
            color_discrete_map=colors,
            category_orders={"class": list(colors)},
            custom_data=["hover"],
        )
        fig.update_traces(hovertemplate="%{customdata[0]}<extra></extra>", marker_line=dict(color="#ffffff", width=0.7))
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            height=620, margin=dict(l=0, r=0, t=0, b=0), dragmode=False,
            legend=dict(title=axis, yanchor="top", y=0.98, xanchor="right", x=0.99),
        )
        show(fig)
        if level == "Region":
            st.caption("Each county is shaded with the value for its whole region.")

with st.expander("See the numbers"):
    table = pd.DataFrame({level: view.index})
    for m_label, m in MEASURES.items():
        unit = " (US$)" if m["money"] else ""
        table[f"{m_label}{unit}"] = place_view(level, segment, m["key"])["value"].reindex(view.index).values
    table[f"Share of local {measure['noun']} (%)"] = view["share"].values
    table["Specialization vs California"] = view["spec"].values
    table["Rank"] = range(1, len(view) + 1)
    numbers(table)

st.caption(REDACTION_NOTE)
if level == "County" and mode != "Total":
    st.caption("Small counties can show very high shares from a handful of employers.")
