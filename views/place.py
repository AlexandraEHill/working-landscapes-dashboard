"""Your county or region: what does my place have, and what does it specialize in?"""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (
    ACCENT, ALL_WL, INK, MEASURES, REDACTION_NOTE, SEGMENT_COLORS, SEGMENTS,
    ca_share, current_measure, fmt, hbar, numbers, pct, places, region_counties,
    show, takeaway, times,
)

label, measure = current_measure()
key, money = measure["key"], measure["money"]
regions = region_counties()
county_region = {c: r for r, counties in regions.items() for c in counties}

st.title("Your county or region")

left, right = st.columns([1, 2])
with left:
    level = st.segmented_control("Look at a", ["Region", "County"], default="Region") or "Region"
with right:
    if level == "Region":
        options = sorted(regions)
        place = st.selectbox("Choose a region", options, index=options.index("Central San Joaquin"))
    else:
        options = sorted(county_region)
        place = st.selectbox("Choose a county", options, index=options.index("Fresno"))

if level == "Region":
    members = regions[place]
    if len(members) == 1:
        st.caption("This region is a single county.")
    else:
        st.caption(f"{place} = {', '.join(members)} counties.")
else:
    st.caption(f"{place} County is part of the {county_region[place]} region.")

segments, totals = places(level)
mine = segments[segments["place"] == place].set_index("segment")
total = totals.loc[place]
share = 100 * mine[key] / total[key]
spec = pd.Series({s: share[s] / ca_share(s, key) for s in mine.index})
wl = mine.loc[ALL_WL]
ranked = mine.loc[SEGMENTS, key].sort_values(ascending=False)

# ---- takeaway and headline numbers
sentence = (
    f"In **{place}**, working landscapes account for **{fmt(wl[key], money)}** {measure['phrase']}: "
    f"**{pct(share[ALL_WL])}** of the local total, compared with **{pct(ca_share(ALL_WL, key))}** "
    f"statewide. The largest segment is **{ranked.index[0]}** ({fmt(ranked.iloc[0], money)})."
)
# Only call out a specialization when it rests on a meaningful number of jobs.
solid = spec[SEGMENTS][mine.loc[SEGMENTS, "jobs"] >= 100]
if len(solid) and solid.max() >= 1.5:
    sentence += (
        f" Compared with California as a whole, {place} is most specialized in "
        f"**{solid.idxmax()}** ({times(solid.max())} the state average)."
    )
takeaway(sentence)

for column, (name, m) in zip(st.columns(4), MEASURES.items()):
    with column:
        st.metric(f"Working landscapes {name.lower()}", fmt(wl[m["key"]], m["money"]), help=m["help"], border=True)
        st.caption(f"{pct(100 * wl[m['key']] / total[m['key']])} of all {m['noun']} in {place}")

# ---- segment profile
all_counties = places("County")[0]
statewide = all_counties.groupby("segment")[key].sum()

st.subheader(f"{label} by segment in {place}, 2024")
show(
    hbar(
        ranked.index,
        ranked.values,
        [fmt(v, money) if v > 0 else "none reported" for v in ranked.values],
        [SEGMENT_COLORS[s] for s in ranked.index],
        [
            f"<b>{s}</b><br>{fmt(v, money)} {measure['noun']}<br>{pct(share[s])} of the local economy<br>"
            f"{pct(100 * v / statewide[s])} of the county-reported California total for this segment"
            for s, v in ranked.items()
        ],
        f"{label}, 2024",
    )
)

# ---- specialization
st.subheader(f"Where {place} is more specialized than California")
with st.popover("How to read this"):
    st.write(
        "A value of 2x means this segment makes up twice as large a share of the "
        "local economy as it does statewide. 1x means the same as California. "
        "Economists call this a location quotient. Hollow dots mark segments with "
        "fewer than 100 local jobs, where the comparison is less reliable."
    )
dots = spec[SEGMENTS][spec[SEGMENTS] > 0].sort_values(ascending=False)
small = mine.loc[dots.index, "jobs"] < 100
low, high = min(dots.min(), 0.5) / 1.4, max(dots.max(), 2) * 1.6
ticks = [t for t in (0.03, 0.06, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64) if low <= t <= high]
fig = go.Figure(
    go.Scatter(
        x=dots.values,
        y=dots.index,
        mode="markers+text",
        text=[f"  {times(v)}" for v in dots.values],
        textposition="middle right",
        cliponaxis=False,
        marker=dict(
            size=16,
            color=[SEGMENT_COLORS[s] for s in dots.index],
            symbol=["circle-open" if s else "circle" for s in small],
            line=dict(width=2.5, color=[SEGMENT_COLORS[s] for s in dots.index]),
        ),
        hovertext=[
            f"<b>{s}</b><br>{times(v)} the California average<br>Local share: {pct(share[s])}<br>"
            f"California share: {pct(ca_share(s, key))}<br>{fmt(mine.loc[s, key], money)} {measure['noun']}"
            + ("<br>Small numbers: treat with caution." if small[s] else "")
            for s, v in dots.items()
        ],
        hoverinfo="text",
    )
)
fig.add_vline(x=1, line=dict(color=INK, width=1, dash="dot"))
fig.add_annotation(x=0, xref="x", y=1, yref="paper", yanchor="bottom", showarrow=False,
                   text="Same as California", font=dict(size=12, color=INK))
fig.update_layout(
    height=max(220, 34 * len(dots) + 90),
    template="plotly_white",
    margin=dict(l=10, r=10, t=30, b=10),
    hoverlabel=dict(align="left"),
    xaxis=dict(type="log", range=[math.log10(low), math.log10(high)], tickvals=ticks,
               ticktext=[f"{t:g}x" for t in ticks], fixedrange=True,
               title=f"Share of local {measure['noun']} compared with California's share"),
    yaxis=dict(autorange="reversed", automargin=True, fixedrange=True, ticksuffix="  "),
)
show(fig)
missing = [s for s in SEGMENTS if s not in dots.index]
if missing:
    st.caption(f"Not shown (none reported): {', '.join(missing)}.")

# ---- full profile table
st.subheader(f"Full profile: {place}")
profile = mine.loc[SEGMENTS + [ALL_WL], ["jobs", "sales", "earnings", "businesses"]].copy()
profile[f"Share of local {measure['noun']} (%)"] = share
profile["Specialization vs California"] = spec
profile.loc["All industries", ["jobs", "sales", "earnings", "businesses"]] = total.values
profile.loc["All industries", f"Share of local {measure['noun']} (%)"] = 100
profile = profile.reset_index().rename(
    columns={"segment": "Segment", "jobs": "Jobs", "sales": "Sales (US$)",
             "earnings": "Earnings (US$)", "businesses": "Businesses"}
)
numbers(profile, f"{place.replace(' ', '_').lower()}_profile.csv", f"Download {place} profile (CSV)")

if level == "Region" and len(regions[place]) > 1:
    with st.expander("Counties in this region"):
        counties = all_counties[(all_counties["segment"] == ALL_WL) & all_counties["place"].isin(regions[place])]
        counties = counties.set_index("place")[key].sort_values(ascending=False)
        show(
            hbar(
                counties.index, counties.values, [fmt(v, money) for v in counties.values], ACCENT,
                [f"<b>{c} County</b><br>{fmt(v, money)} working landscapes {measure['noun']}" for c, v in counties.items()],
                f"Working landscapes {measure['noun']}, 2024",
            )
        )

st.caption(REDACTION_NOTE)
