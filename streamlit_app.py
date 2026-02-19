import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Dashcam MicroSD Calculator", layout="centered")

st.title("Dashcam MicroSD Card Capacity & TBW Calculator")
st.markdown(
    """
    Enter how many streams your dashcam produces and set each stream's parameters so the calculator can estimate writes and suggest an appropriate card.

    - **Name**: optional label to identify the stream (e.g. `Front`, `Rear (timelapse)`).
    - **File size (MB)** and **File length (minutes)** - these describe a single recorded file. 
    - **Recording hours per day** - how many hours/day that stream actually writes data (use `0` to disable a stream).

    The app calculates per-stream bitrate (MB/s and Mbps), MB/day, GB/day, TB/year, estimated TBW for the chosen lifetime, and a recommended card size for the selected retention hours (uses a 24-hour average).

    Tip: if your camera has a higher quality mode and a "timelapse" or "parking" mode, enter them as two seperate streams and give them distinct names.

    #### For example: 
    - My dash cam records at 315 MB/5 minutes for both the front and rear cameras when driving. (I checked this by checking the file size on the SD card)
    - When the car is parked, the front camera records a timelapse at ~445 MB/hour and the rear camera records a timelapse at ~140 MB/hour
    Thus I entered these 4 seperate "streams" with their respective recording hours per day. For my example below I am saying I drive 1/hour day (so 1 hr/day for the normal streams) and the car is parked the rest of the time (so 23 hr/day for the timelapse streams)

    Use the **Load example** button to populate my 4-stream example (2 normal streams at 1 hr/day + 2 timelapse streams at 23 hr/day).
    """
)


st.markdown("---")

# Main inputs
if st.button("Load example: 4-stream (2 normal + 2 timelapse)"):
    # configure 4 streams: front/rear normal (1 hr/day) + front/rear timelapse (23 hr/day)
    st.session_state["num_streams"] = 4
    # Front normal
    st.session_state["name_0"] = "Front (normal)"
    st.session_state["fs_0"] = 315.0
    st.session_state["fl_0"] = 5
    st.session_state["hours_0"] = 1.0
    # Rear normal
    st.session_state["name_1"] = "Rear (normal)"
    st.session_state["fs_1"] = 315.0
    st.session_state["fl_1"] = 5
    st.session_state["hours_1"] = 1.0
    # Front timelapse
    st.session_state["name_2"] = "Front (timelapse)"
    st.session_state["fs_2"] = 445.0
    st.session_state["fl_2"] = 60
    st.session_state["hours_2"] = 23.0
    # Rear timelapse
    st.session_state["name_3"] = "Rear (timelapse)"
    st.session_state["fs_3"] = 140.0
    st.session_state["fl_3"] = 60
    st.session_state["hours_3"] = 23.0

streams = st.number_input("Number of streams", min_value=1, max_value=8, value=st.session_state.get("num_streams", 2), step=1, key="num_streams")

st.write("Provide the average `recording file size` and `recording length` for each stream; set `recording hours per day` for each stream individually.")

# Per-stream inputs
stream_configs = []
for i in range(int(streams)):
    with st.expander(f"Stream {i+1}", expanded=(i == 0)):
        # user-visible name for the stream
        name = st.text_input(f"Name — stream {i+1}", value=st.session_state.get(f"name_{i}", f"Stream {i+1}"), key=f"name_{i}")

        file_size_mb = st.number_input(
            f"File size (MB) - stream {i+1}",
            min_value=0.0,
            value=(315.0 if i == 0 else 50.0),
            step=0.1,
            format="%.1f",
            key=f"fs_{i}",
        )
        file_length_min = st.number_input(
            f"File length (minutes) - stream {i+1}",
            min_value=1,
            value=(5 if i == 0 else 1),
            step=1,
            key=f"fl_{i}",
        )

        recording_hours = st.number_input(
            f"Recording hours per day - stream {i+1}",
            min_value=0.0,
            max_value=24.0,
            value=(24.0 if i == 0 else 0.0),
            step=0.5,
            format="%.1f",
            key=f"hours_{i}",
            help=(
                "Hours per day this stream writes data (use 0 for disabled stream). "
                "If you have a timelapse-only stream, set `file_length=60` and set `file_size` to the MB written per hour "
                "(e.g. 445 MB for 1 hour). The calculator will convert that into an equivalent bitrate."
            ),
        )

        stream_configs.append({
            "name": name,
            "file_size_mb": file_size_mb,
            "file_length_min": file_length_min,
            "hours_per_day": recording_hours,
        })

st.markdown("---")

st.info("Recording hours per day are specified per-stream (normal vs timelapse). Adjust hours inside each stream's section.")
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
total_mb_per_day = 0.0
for i, cfg in enumerate(stream_configs, start=1):
    name = cfg.get("name", f"Stream {i}")
    fs = cfg["file_size_mb"]
    fl = cfg["file_length_min"]
    hours = float(cfg.get("hours_per_day", 0.0))

    mb_per_min = fs / fl if fl > 0 else 0.0
    mb_per_hour = mb_per_min * 60
    mb_per_sec = mb_per_hour / 3600.0
    mbps = mb_per_sec * 8.0  # megabits per second

    # MB written per day for this stream = mb_per_hour * hours_per_day
    mb_per_day_stream = mb_per_hour * hours
    avg_mb_per_hour = mb_per_day_stream / 24.0

    total_mb_per_day += mb_per_day_stream

    rows.append(
        {
            "stream": name,
            "file_size_MB": fs,
            "file_length_min": fl,
            "MB_per_min": mb_per_min,
            "MB_per_hour": mb_per_hour,
            "MB_per_sec": mb_per_sec,
            "Mbps": mbps,
            "recording_hours_per_day": hours,
            "MB_per_day": mb_per_day_stream,
            "avg_MB_per_hour": avg_mb_per_hour,
        }
    )

# Totals and conversions
total_mb_per_day = sum(r["MB_per_day"] for r in rows)
gb_per_day = total_mb_per_day / 1024
tb_per_year = (gb_per_day * 365) / 1024

# TBW (total bytes written) required for expected lifetime
tbw_required_over_life = tb_per_year * expected_lifetime_years
tbw_with_margin = tbw_required_over_life * (1 + safety_margin_pct / 100.0)

# Retention/card capacity calculations (uses 24h average MB/hour)
avg_mb_per_hour_all = total_mb_per_day / 24.0 if total_mb_per_day > 0 else 0.0
mb_needed_for_retention = avg_mb_per_hour_all * retention_hours
gb_needed_for_retention = mb_needed_for_retention / 1024

def pick_card_size_gb(gb_needed: float) -> int:
    sizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
    for s in sizes:
        if gb_needed <= s:
            return s
    return sizes[-1]

recommended_card_gb = pick_card_size_gb(math.ceil(gb_needed_for_retention))

# Results
st.subheader("Per-stream breakdown")
df = pd.DataFrame(rows)
if not df.empty:
    df_display = df.copy()
    df_display["file_size_MB"] = df_display["file_size_MB"].map(lambda v: f"{v:,.1f}")
    df_display["MB_per_min"] = df_display["MB_per_min"].map(lambda v: f"{v:,.1f}")
    df_display["MB_per_hour"] = df_display["MB_per_hour"].map(lambda v: f"{v:,.1f}")
    df_display["recording_hours_per_day"] = df_display["recording_hours_per_day"].map(lambda v: f"{v:,.1f}")
    df_display["MB_per_day"] = df_display["MB_per_day"].map(lambda v: f"{v:,.1f}")
    st.table(df_display.set_index("stream"))

st.markdown("---")

st.subheader("Totals & Recommendations")
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



# Common card size table
common_sizes = [16, 32, 64, 128, 256, 512, 1024]
capacity_hours = [(s * 1024) / avg_mb_per_hour_all if avg_mb_per_hour_all > 0 else float("inf") for s in common_sizes]
cap_df = pd.DataFrame({"card_GB": common_sizes, "hours_of_retention": [f"{h:,.1f}" for h in capacity_hours]})
st.table(cap_df.set_index("card_GB"))

st.caption("Outputs: total writes per day / year and suggested card capacity to hold the chosen retention hours. Use the TBW recommendation to compare with card endurance-rated cards.")

st.warning(
    "Make sure to use a high endurance microSD card for dashcams or continuous video recording. "
    "Prefer cards labeled **High Endurance**, **Surveillance**, or **Video** and verify the manufacturer's endurance/TBW rating. "
    "Choose a card whose endurance meets or exceeds the **Recommended TBW** shown above."
)
st.caption("Tip: industrial/endurance-rated cards usually include better wear-leveling and warranties for 24/7 recording, plus better high-temp performance.")
