# 🎈 Dashcam TBW & capacity calculator

This is a simple Streamlit utility to help estimate how much data your dashcam writes and what microSD capacity / TBW (total bytes written) you should pick. Enter each stream's file size and length, set recording hours/day and expected card lifetime — the app shows GB/day, TB/year, suggested card sizes, and a TBW recommendation.

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
