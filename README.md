# 🎈 Dashcam TBW & capacity calculator

This is a simple Streamlit utility to help estimate how much data your dashcam writes and what microSD capacity / TBW (total bytes written) you should pick.

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

> [!TIP]
> [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashcam-calculator.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
