"""Segments and the nation: what is inside a segment, and how does California rank?"""

import pandas as pd
import streamlit as st

from common import (
    ACCENT, ALL_WL, MEASURES, NEUTRAL, SEGMENT_ABOUT, SEGMENT_COLORS, SEGMENTS,
    current_measure, fmt, hbar, load, numbers, pct, show, state_view, takeaway, times,
)

label, measure = current_measure()
key, money = measure["key"], measure["money"]

st.title("Segments and the nation")
segment = st.selectbox("Segment", [ALL_WL] + SEGMENTS, index=1)
name = "working landscapes" if segment == ALL_WL else segment.lower()
color = ACCENT if segment == ALL_WL else SEGMENT_COLORS[segment]
if segment != ALL_WL:
    st.write(SEGMENT_ABOUT[segment])

states = state_view(segment, key)
ca = states.loc["California"]
by_measure = {m["key"]: state_view(segment, m["key"]).loc["California"] for m in MEASURES.values()}

takeaway(
    f"California's {name} supported **{fmt(by_measure['jobs']['value'])}** jobs and "
    f"**{fmt(by_measure['sales']['value'], True)}** in sales in 2024. By {measure['noun']}, California "
    f"ranks **#{ca['rank']:.0f}** among states, with **{pct(ca['us_share'])}** of the US total."
)
for column, (m_label, m) in zip(st.columns(4), MEASURES.items()):
    row = by_measure[m["key"]]
    with column:
        st.metric(m_label, fmt(row["value"], m["money"]), help=m["help"], border=True)
        st.caption(f"#{row['rank']:.0f} among states, {pct(row['us_share'])} of US")

states_tab, industries_tab = st.tabs(["California among the states", "Industries in this segment"])

# ---- California among the states
with states_tab:
    mode = st.segmented_control(
        "Show as",
        ["Total", "Specialization vs US"],
        default="Total",
        help="Large states lead most totals. Specialization shows where a segment is an "
        "unusually large part of the state economy (1x = same as the US).",
    ) or "Total"
    by_total = mode == "Total"
    column, rank_column = ("value", "rank") if by_total else ("spec", "spec_rank")
    ordered = states.sort_values(column, ascending=False)
    shown = ordered.head(15)
    if "California" not in shown.index:
        shown = pd.concat([shown, ordered.loc[["California"]]])

    if by_total:
        st.subheader(f"{name.capitalize()} {measure['noun']}: California and the other leading states")
    else:
        st.subheader(f"Where {name} is an unusually large part of the state economy")
        takeaway(
            f"{name.capitalize()} is **{times(ca['spec'])}** as large a part of California's economy as it "
            f"is of the US economy; California ranks #{ca['spec_rank']:.0f} on this basis."
        )
    show(
        hbar(
            [f"{s} (#{r:.0f})" for s, r in zip(shown.index, shown[rank_column])],
            shown[column].values,
            [f"{fmt(v, money)} · {pct(u)} of US" for v, u in zip(shown["value"], shown["us_share"])]
            if by_total else [times(v) for v in shown["spec"]],
            [color if s == "California" else NEUTRAL for s in shown.index],
            [
                f"<b>{s}</b><br>{fmt(row['value'], money)} {measure['noun']}<br>{pct(row['us_share'])} of the US total "
                f"(rank {row['rank']:.0f} of 51)<br>{times(row['spec'])} the US average (rank {row['spec_rank']:.0f} of 51)"
                for s, row in shown.iterrows()
            ],
            f"{label}, 2024" if by_total else f"Share of state {measure['noun']} compared with the US share",
            reference=None if by_total else (1, "Same as the US (1x)"),
        )
    )
    st.caption("Top 15 shown. Ranks are out of 51: the 50 states plus the District of Columbia.")
    with st.expander("See the numbers"):
        table = states.reset_index().rename(
            columns={"state": "State", "value": f"{label}{' (US$)' if money else ''}",
                     "us_share": "Share of US (%)", "spec": "Specialization vs US",
                     "rank": "Rank", "spec_rank": "Specialization rank"}
        )
        numbers(table, f"{name.replace(' ', '_')}_{key}_by_state.csv")

# ---- industries inside the segment
with industries_tab:
    industries = load()[3]
    if segment != ALL_WL:
        industries = industries[industries["segment"] == segment]
    industries = industries.sort_values(key, ascending=False)
    total = industries[key].sum()
    top = industries.head(15)

    st.subheader(f"Largest industries in California's {name}, by {measure['noun']}")
    takeaway(
        f"The largest industry is **{top['industry'].iloc[0]}** ({fmt(top[key].iloc[0], money)}, "
        f"**{pct(100 * top[key].iloc[0] / total)}** of the segment). The top five industries make up "
        f"{pct(100 * top[key].head(5).sum() / total)}."
    )
    show(
        hbar(
            [i if len(i) <= 48 else i[:46] + "…" for i in top["industry"]],
            top[key].values,
            [fmt(v, money) for v in top[key]],
            [SEGMENT_COLORS[s] for s in top["segment"]],
            [
                f"<b>{row['industry']}</b><br>NAICS {row['naics']} · {row['segment']}<br>"
                f"{fmt(row[key], money)} {measure['noun']}<br>{pct(100 * row[key] / total)} of the segment<br>"
                f"California has {pct(100 * row[key] / row[key + '_us']) if row[key + '_us'] else '–'} of the US total"
                for _, row in top.iterrows()
            ],
            f"{label}, 2024",
        )
    )
    if segment == ALL_WL:
        st.caption("Bar colors show each industry's segment; hover over a bar to see its name.")

    table = pd.DataFrame({
        "Industry": industries["industry"],
        "NAICS code": industries["naics"].astype(str),
        "Segment": industries["segment"],
        "Jobs": industries["jobs"],
        "Sales (US$)": industries["sales"],
        "Earnings (US$)": industries["earnings"],
        "Businesses": industries["businesses"],
        f"Share of segment {measure['noun']} (%)": 100 * industries[key] / total,
        f"California share of US {measure['noun']} (%)": (100 * industries[key] / industries[key + "_us"]).where(industries[key + "_us"] > 0),
    })
    numbers(table, f"{name.replace(' ', '_')}_industries.csv")
    st.caption("Industry detail is available for California as a whole only, not for counties or regions.")
