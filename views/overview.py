"""Overview: how big are California's working landscapes, and what are they made of?"""

import plotly.graph_objects as go
import streamlit as st

from common import (
    ACCENT, AG_SEGMENTS, ALL_WL, MEASURES, NEUTRAL, SEGMENT_COLORS, SEGMENTS, WL_SECTOR,
    california, current_measure, fmt, hbar, numbers, ordinal, pct, places, show, takeaway,
)

label, measure = current_measure()
key, money = measure["key"], measure["money"]
sectors, segments, total = california()
wl = segments.loc[ALL_WL]

st.title("California's Working Landscapes, 2024")
st.write(
    "Nine segments of the economy that depend on the state's land and natural "
    "resources: farming and the businesses that support, process and distribute "
    "its products, plus fishing, forestry, mining, outdoor recreation and "
    "renewable energy."
)
takeaway(
    f"In 2024, California's working landscapes supported **{fmt(wl['jobs'])}** jobs at "
    f"**{fmt(wl['businesses'])}** businesses, generating **{fmt(wl['sales'], True)}** in "
    f"sales and **{fmt(wl['earnings'], True)}** in worker earnings."
)

for column, (name, m) in zip(st.columns(4), MEASURES.items()):
    with column:
        st.metric(name, fmt(wl[m["key"]], m["money"]), help=m["help"], border=True)
        st.caption(f"{pct(100 * wl[m['key']] / total[m['key']])} of California's total")

# ---- working landscapes among all sectors
ranked = sectors[key].sort_values(ascending=False)
rank = list(ranked.index).index(WL_SECTOR) + 1
shares = 100 * ranked / total[key]

st.subheader(f"Working landscapes rank {ordinal(rank)} of {len(ranked)} California sectors by {measure['noun']}")
st.caption(
    "Working landscapes industries are removed from their usual sectors (for example, "
    "food manufacturing leaves Manufacturing), so nothing is counted twice."
)
show(
    hbar(
        ranked.index,
        ranked.values,
        [pct(s) for s in shares],
        [ACCENT if s == WL_SECTOR else NEUTRAL for s in ranked.index],
        [
            f"<b>{s}</b><br>{fmt(v, money)} {measure['noun']}<br>{pct(sh)} of California's total<br>Rank {i} of {len(ranked)}"
            for i, (s, v, sh) in enumerate(zip(ranked.index, ranked.values, shares), 1)
        ],
        f"{label}, 2024 (labels show share of California's total)",
    )
)

# ---- the nine segments
by_segment = segments.loc[SEGMENTS, key].sort_values(ascending=False)
ag = segments.loc[AG_SEGMENTS, key].sum()

st.subheader(f"What the sector is made of: {measure['noun']} by segment")
takeaway(
    f"**{by_segment.index[0]}** is the largest segment by {measure['noun']} "
    f"({fmt(by_segment.iloc[0], money)}). The four agricultural segments together account "
    f"for **{pct(100 * ag / wl[key])}** of the working landscapes total ({fmt(ag, money)})."
)
with st.popover("What is a segment?"):
    st.write(
        "A segment is a group of related industries. The report sorts about 190 "
        "detailed industries into nine segments. See *Segments and the nation* for "
        "the industries inside each one."
    )
show(
    hbar(
        by_segment.index,
        by_segment.values,
        [fmt(v, money) for v in by_segment.values],
        [SEGMENT_COLORS[s] for s in by_segment.index],
        [
            f"<b>{s}</b><br>{fmt(v, money)} {measure['noun']}<br>"
            f"{pct(100 * v / wl[key])} of working landscapes<br>{pct(100 * v / total[key])} of California's total"
            for s, v in by_segment.items()
        ],
        f"{label}, 2024",
    )
)

# ---- regions
region_segments, _ = places("Region")
pivot = region_segments.pivot(index="place", columns="segment", values=key)
pivot = pivot.sort_values(ALL_WL, ascending=False)
top_two = pivot[ALL_WL].iloc[:2]

st.subheader(f"Working landscapes {measure['noun']} by California Jobs First region")
takeaway(
    f"**{top_two.index[0]}** and **{top_two.index[1]}** are the largest contributors, with "
    f"{fmt(top_two.sum(), money)} between them ({pct(100 * top_two.sum() / pivot[ALL_WL].sum())} "
    "of the regional total)."
)
fig = go.Figure()
for segment in SEGMENTS:
    fig.add_bar(
        name=segment,
        y=pivot.index,
        x=pivot[segment],
        orientation="h",
        marker=dict(color=SEGMENT_COLORS[segment], line=dict(color="#ffffff", width=1)),
        hovertext=[
            f"<b>{region}</b><br>{segment}: {fmt(v, money)}<br>{pct(100 * v / whole)} of the region's working landscapes"
            for region, v, whole in zip(pivot.index, pivot[segment], pivot[ALL_WL])
        ],
        hoverinfo="text",
    )
fig.add_scatter(
    y=pivot.index, x=pivot[ALL_WL], mode="text", text=[f"  {fmt(v, money)}" for v in pivot[ALL_WL]],
    textposition="middle right", showlegend=False, hoverinfo="skip", cliponaxis=False,
)
fig.update_layout(
    barmode="stack",
    height=560,
    template="plotly_white",
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", yanchor="top", y=-0.08, x=0, traceorder="normal"),
    xaxis=dict(title=f"{label}, 2024", showticklabels=False, showgrid=False, fixedrange=True,
               range=[0, pivot[ALL_WL].max() * 1.25]),
    yaxis=dict(autorange="reversed", automargin=True, fixedrange=True, ticksuffix="  "),
)
show(fig)
st.caption(
    "Region figures are sums of county data and can fall short of the statewide totals "
    "above, because some county values are withheld for confidentiality."
)
st.page_link("views/place.py", label="Look up your county or region", icon=":material/arrow_forward:")

with st.expander("See the numbers"):
    st.markdown("**California sectors**")
    numbers(sectors.sort_values(key, ascending=False).reset_index().rename(
        columns={"sector": "Sector", "jobs": "Jobs", "sales": "Sales (US$)",
                 "earnings": "Earnings (US$)", "businesses": "Businesses"}), "california_sectors.csv")
    st.markdown("**Working landscapes segments**")
    numbers(segments.reset_index().rename(
        columns={"segment": "Segment", "jobs": "Jobs", "sales": "Sales (US$)",
                 "earnings": "Earnings (US$)", "businesses": "Businesses"}), "california_segments.csv")
    st.markdown(f"**{label} by region and segment**")
    numbers(pivot[SEGMENTS + [ALL_WL]].reset_index().rename(columns={"place": "Region"}),
            f"regions_by_segment_{key}.csv")
