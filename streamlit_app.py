import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Dashcam TBW & Capacity Calculator", layout="centered")

st.title("Dashcam MicroSD Card Capacity & TBW Calculator")
st.write(
    "Enter how many streams your Dashcam produces, then for each stream provide the `file size` and `file length` (the app calculates `per day` and `per year` writes and suggests a card size/TBW).")

st.markdown("---")

# Main inputs
streams = st.number_input("Number of streams", min_value=1, max_value=8, value=2, step=1)
st.write("Provide the average `recording file size` and `recording length` for each stream:")

# Per stream inputs
stream_configs = []
for i in range(int(streams)):
    with st.expander(f"Stream {i+1}", expanded=(i == 0)):
        file_size_mb = st.number_input(
            f"File size (MB) — stream {i+1}",
            min_value=0.0,
            value=(315.0 if i == 0 else 50.0),
            step=0.1,
            format="%.1f",
            key=f"fs_{i}",
        )
        file_length_min = st.number_input(
            f"File length (minutes) — stream {i+1}", min_value=1, value=(5 if i == 0 else 1), step=1, key=f"fl_{i}"
        )
        stream_configs.append({"file_size_mb": file_size_mb, "file_length_min": file_length_min})

st.markdown("---")

hours_per_day = st.number_input("Recording hours per day", min_value=0.0, max_value=24.0, value=24.0, step=0.5, format="%.1f")
retention_hours = st.number_input(
    "Wanted Retention Hours",
    min_value=1,
    max_value=168,
    value=24,
    step=1,
    help="Hours of footage to keep on the card before it loops/overwrites",
)
expected_lifetime_years = st.number_input("Wanted card lifetime (years)", min_value=0.5, value=3.0, step=0.5, format="%.1f")
safety_margin_pct = st.slider("Safety margin for TBW (%)", min_value=0, max_value=200, value=20)

# Calculations per stream
rows = []
total_mb_per_hour_all = 0.0
for i, cfg in enumerate(stream_configs, start=1):
    fs = cfg["file_size_mb"]
    fl = cfg["file_length_min"]
    mb_per_min = fs / fl if fl > 0 else 0.0
    mb_per_hour = mb_per_min * 60
    mb_per_day_stream = mb_per_hour * hours_per_day
    total_mb_per_hour_all += mb_per_hour
    rows.append(
        {
            "stream": f"Stream {i}",
            "file_size_MB": fs,
            "file_length_min": fl,
            "MB_per_min": mb_per_min,
            "MB_per_hour": mb_per_hour,
            "MB_per_day": mb_per_day_stream,
        }
    )

# Totals and conversions
total_mb_per_day = sum(r["MB_per_day"] for r in rows)
gb_per_day = total_mb_per_day / 1024
tb_per_year = (gb_per_day * 365) / 1024

# TBW (total bytes written) required for expected lifetime
tbw_required_over_life = tb_per_year * expected_lifetime_years
tbw_with_margin = tbw_required_over_life * (1 + safety_margin_pct / 100.0)

# Retention/card capacity calculations
mb_needed_for_retention = total_mb_per_hour_all * retention_hours
gb_needed_for_retention = mb_needed_for_retention / 1024

def pick_card_size_gb(gb_needed: float) -> int:
    sizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
    for s in sizes:
        if gb_needed <= s:
            return s
    return sizes[-1]

recommended_card_gb = pick_card_size_gb(math.ceil(gb_needed_for_retention))

# Results
st.subheader("Per‑stream breakdown")
df = pd.DataFrame(rows)
if not df.empty:
    df_display = df.copy()
    df_display["file_size_MB"] = df_display["file_size_MB"].map(lambda v: f"{v:,.1f}")
    df_display["MB_per_min"] = df_display["MB_per_min"].map(lambda v: f"{v:,.1f}")
    df_display["MB_per_hour"] = df_display["MB_per_hour"].map(lambda v: f"{v:,.1f}")
    df_display["MB_per_day"] = df_display["MB_per_day"].map(lambda v: f"{v:,.1f}")
    st.table(df_display.set_index("stream"))

st.markdown("---")

st.subheader("Totals & recommendations")
cols = st.columns(3)
cols[0].metric("MB / day", f"{total_mb_per_day:,.0f} MB")
cols[1].metric("GB / day", f"{gb_per_day:,.2f} GB")
cols[2].metric("TB / year", f"{tb_per_year:,.4f} TB")

st.write("### TBW / endurance")
st.write(f"Estimated writes over {expected_lifetime_years} years: **{tbw_required_over_life:,.3f} TB**")
st.write(f"Recommended TBW with {safety_margin_pct}% margin: **{tbw_with_margin:,.3f} TB**")

st.write("### Card capacity for loop/retention")
st.write(f"Data needed to keep {retention_hours} hours: **{gb_needed_for_retention:,.2f} GB**")
st.write(f"Suggested minimum card size (rounded): **{recommended_card_gb} GB**")



# Common card size table for reference
common_sizes = [16, 32, 64, 128, 256, 512, 1024]
capacity_hours = [(s * 1024) / total_mb_per_hour_all if total_mb_per_hour_all > 0 else float("inf") for s in common_sizes]
cap_df = pd.DataFrame({"card_GB": common_sizes, "hours_of_retention": [f"{h:,.1f}" for h in capacity_hours]})
st.table(cap_df.set_index("card_GB"))

st.caption("Outputs: total writes per day / year and suggested card capacity to hold the chosen retention hours. Use the TBW recommendation to compare with card endurance-rated cards.")
