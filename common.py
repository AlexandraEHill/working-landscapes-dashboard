"""Shared data, wording, number formatting and chart helpers for every page."""

import json
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"

# ---------------------------------------------------------------- wording

ALL_WL = "All working landscapes"
WL_SECTOR = "Working Landscapes"
REPORT_URL = "https://ucanr.edu/working-landscapes-2025"

# label -> column name, wording, and whether the value is in dollars
MEASURES = {
    "Jobs": {
        "key": "jobs",
        "noun": "jobs",
        "phrase": "jobs",
        "money": False,
        "help": "Annual average number of jobs, including employees and the "
        "self-employed. A job is a position, not a person; part-time and "
        "seasonal jobs count.",
    },
    "Sales": {
        "key": "sales",
        "noun": "sales",
        "phrase": "in sales",
        "money": True,
        "help": "Total annual sales (gross receipts) of businesses. Sales count "
        "goods each time they change hands, so they are larger than GDP.",
    },
    "Earnings": {
        "key": "earnings",
        "noun": "worker earnings",
        "phrase": "in worker earnings",
        "money": True,
        "help": "Wages, salaries, benefits and the income of business owners "
        "who work for themselves.",
    },
    "Businesses": {
        "key": "businesses",
        "noun": "businesses",
        "phrase": "businesses",
        "money": False,
        "help": "Business locations with a payroll. A company with three sites "
        "counts three times; self-employed people without employees are not "
        "counted.",
    },
}
KEYS = [m["key"] for m in MEASURES.values()]

# Fixed order (agriculture first) and fixed colors: a segment keeps its color
# on every chart. The four agricultural segments share one green family.
# Checked so that no two colors merge under red-green color blindness.
SEGMENT_COLORS = {
    "Agricultural Production": "#0b3d0b",
    "Agricultural Support": "#1f7a1f",
    "Agricultural Processing": "#5cb85c",
    "Agricultural Distribution": "#bfe5b0",
    "Forestry": "#1a1a1a",
    "Mining": "#555555",
    "Renewable Energy": "#f0e442",
    "Outdoor Recreation": "#cc79a7",
    "Fishing": "#3b4cc0",
}
SEGMENTS = list(SEGMENT_COLORS)
AG_SEGMENTS = SEGMENTS[:4]
ACCENT = "#1f7a1f"
NEUTRAL = "#b8bdc4"
INK = "#333333"

# Short descriptions written for this dashboard from the industry lists.
SEGMENT_ABOUT = {
    "Agricultural Production": "Farming and ranching: growing crops and raising "
    "animals, plus planting, harvesting and post-harvest work.",
    "Agricultural Support": "Businesses that serve farms: farm labor contractors, "
    "farm management, farm supply stores, and agricultural and environmental "
    "consulting.",
    "Agricultural Processing": "Turning farm products into food and drink: "
    "wineries, bakeries, breweries, canning, dairy and meat processing.",
    "Agricultural Distribution": "Getting food and farm products to buyers: "
    "grocery and produce wholesalers and specialty food and drink retailers.",
    "Forestry": "Timber and logging, plus the wood and paper products made from "
    "them and the wholesalers that sell them.",
    "Mining": "Oil and gas extraction, quarrying and mineral mining, with related "
    "products such as concrete and the services that support them.",
    "Renewable Energy": "Electricity generated from solar, wind, hydroelectric, "
    "geothermal and biomass sources.",
    "Outdoor Recreation": "Recreation that depends on the outdoors: parks, "
    "campgrounds and RV parks, ski areas, zoos and botanical gardens, and "
    "sightseeing.",
    "Fishing": "Commercial fishing, seafood processing and seafood wholesalers.",
}

REDACTION_NOTE = (
    "County data are subject to confidentiality redaction, so some small segments "
    "may be understated or missing. \"None reported\" does not mean zero activity."
)

# ---------------------------------------------------------------- data


@st.cache_data
def load():
    """Read the CSVs once and return the tables every page uses."""
    county_segments = pd.read_csv(DATA / "county_segments.csv")
    county_totals = pd.read_csv(DATA / "county_totals.csv")
    states = pd.read_csv(DATA / "state_sectors.csv")
    industries = pd.read_csv(DATA / "ca_industries.csv")
    return county_segments, county_totals, states, industries


@st.cache_data
def load_county_industries():
    """Working landscapes industries (NAICS) for each county."""
    return pd.read_csv(DATA / "county_industries.csv")


@st.cache_data
def load_map():
    path = DATA / "ca_counties.geojson"
    return json.loads(path.read_text()) if path.exists() else None


def california():
    """Statewide numbers from the state-level file (these match the report).

    Returns (sectors, segments, total): sales, jobs etc. for each of the 19
    sectors, for each of the nine segments plus ALL_WL, and for all industries.
    """
    states = load()[2]
    ca = states[states["state"] == "California"]
    sectors = ca.groupby("sector")[KEYS].sum()
    segments = ca[ca["sector"] == WL_SECTOR].groupby("segment")[KEYS].sum()
    segments = segments.reindex(SEGMENTS)
    segments.loc[ALL_WL] = segments.sum()
    return sectors, segments, sectors.sum()


def places(level):
    """County or region numbers from the county-level file.

    level is "County" or "Region". Returns (segments, totals): segments has
    one row per place and segment (including ALL_WL); totals has one row per
    place with its all-industry totals.
    """
    county_segments, county_totals, _, _ = load()
    col = level.lower()
    seg = county_segments.groupby([col, "segment"])[KEYS].sum()
    whole = seg.groupby(level=0).sum()
    whole["segment"] = ALL_WL
    whole = whole.set_index("segment", append=True)
    seg = pd.concat([seg, whole]).reset_index().rename(columns={col: "place"})
    totals = county_totals.groupby(col)[KEYS].sum()
    totals.index.name = "place"
    return seg, totals


def place_view(level, segment, key):
    """One row per place for one segment: value, local share (%), specialization."""
    seg, totals = places(level)
    rows = seg[seg["segment"] == segment].set_index("place")
    out = pd.DataFrame({"value": rows[key]})
    out["share"] = 100 * out["value"] / totals[key]
    out["spec"] = out["share"] / ca_share(segment, key)
    return out


def ca_share(segment, key):
    """A segment's share (%) of California's all-industry total."""
    _, segments, total = california()
    return 100 * segments.loc[segment, key] / total[key]


def state_view(segment, key):
    """One row per state for one segment: value, share of US, specialization, ranks."""
    states = load()[2]
    wl = states[states["sector"] == WL_SECTOR]
    if segment != ALL_WL:
        wl = wl[wl["segment"] == segment]
    out = pd.DataFrame({"value": wl.groupby("state")[key].sum()})
    all_industries = states.groupby("state")[key].sum()
    out["us_share"] = 100 * out["value"] / out["value"].sum()
    us_segment_share = out["value"].sum() / all_industries.sum()
    out["spec"] = (out["value"] / all_industries) / us_segment_share
    out["rank"] = out["value"].rank(ascending=False, method="min").astype(int)
    out["spec_rank"] = out["spec"].rank(ascending=False, method="min").astype(int)
    return out.sort_values("value", ascending=False)


def region_counties():
    """Region name -> list of its counties."""
    totals = load()[1]
    return totals.groupby("region")["county"].apply(list).to_dict()


# ---------------------------------------------------------------- formatting


def fmt(value, money=False):
    """Short readable number: $404B, 1.5M, 298,900, 918."""
    if pd.isna(value):
        return "–"
    if money:
        for size, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
            if abs(value) >= size:
                return f"${float(f'{value / size:.3g}'):g}{suffix}"
        return f"${value:,.0f}"
    if abs(value) >= 1e6:
        return f"{value / 1e6:.1f}M"
    if abs(value) >= 1e4:
        return f"{round(value, -2):,.0f}"
    return f"{value:,.0f}"


def pct(value):
    if pd.isna(value):
        return "–"
    return "<0.1%" if 0 < value < 0.05 else f"{value:.1f}%"


def times(value):
    """Specialization: 2.4x, 0.65x."""
    if pd.isna(value):
        return "–"
    return f"{value:.1f}x" if value >= 1 else f"{value:.2f}x"


def ordinal(n):
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def current_measure():
    """The measure chosen in the switch at the top of the app."""
    label = st.session_state.get("measure_label", "Jobs")
    return label, MEASURES[label]


# ---------------------------------------------------------------- charts


def hbar(labels, values, texts, colors, hovers, axis_title, reference=None, height=None):
    """Sorted horizontal bar chart. Pass rows largest-first; values are labelled
    at the bar ends, so the x axis shows no tick numbers.

    reference: optional (x, text) for a vertical comparison line.
    """
    labels, values = list(labels), list(values)
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            text=list(texts),
            textposition="outside",
            cliponaxis=False,
            marker=dict(color=colors, line=dict(color="#ffffff", width=1)),
            hovertext=list(hovers),
            hoverinfo="text",
        )
    )
    if reference:
        fig.add_vline(x=reference[0], line=dict(color=INK, width=1, dash="dot"))
        fig.add_annotation(
            x=reference[0], y=1, yref="paper", yanchor="bottom", showarrow=False,
            text=reference[1], font=dict(size=12, color=INK),
        )
    top = max(values + [reference[0]] if reference else values, default=0)
    fig.update_layout(
        height=height or max(220, 30 * len(labels) + 90),
        margin=dict(l=10, r=30, t=30, b=10),
        template="plotly_white",
        bargap=0.25,
        hoverlabel=dict(align="left"),
        xaxis=dict(
            title=axis_title, showticklabels=False, showgrid=False, zeroline=True,
            zerolinecolor="#d0d0d0", range=[0, top * 1.3 if top else 1], fixedrange=True,
        ),
        yaxis=dict(autorange="reversed", automargin=True, fixedrange=True, ticksuffix="  "),
    )
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def numbers(table):
    """A formatted, sortable table."""
    config = {}
    shown = table.copy()
    for col in table.columns:
        if not pd.api.types.is_numeric_dtype(table[col]):
            continue
        if "%" in col:
            config[col] = st.column_config.NumberColumn(format="%.1f%%")
        elif "pecialization" in col and "rank" not in col:
            config[col] = st.column_config.NumberColumn(format="%.2f×")
        elif "ank" not in col:
            config[col] = st.column_config.NumberColumn(format="localized")
            shown[col] = shown[col].round(0)
    st.dataframe(shown, hide_index=True, column_config=config, width="stretch")


def takeaway(text):
    """The plain-language finding that opens each section."""
    html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text).replace("$", "&#36;")
    st.markdown(f"<p style='font-size:1.15rem;line-height:1.5'>{html}</p>", unsafe_allow_html=True)
