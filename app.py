import streamlit as st
from datetime import date, datetime
import json
import os

# Configuration constants
SAVE_FILE = "water_tracker.json"
TARGET_ML = 3785
REFERENCE_BOTTLE = 650
GOAL_BOTTLES = 6

# Initialize session state (forces reset on every app start)
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.today_total = 0.0
    st.session_state.today_records = []
    st.session_state.history = {}
    st.session_state.last_date = date.today().isoformat()
    st.session_state.celebrated_today = False

    # Remove any existing save file to enforce full reset on startup
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        st.info("Application started with cleared data (previous records removed).")

# Save current state to file
def save_data():
    data = {
        "current_date": date.today().isoformat(),
        "today_total": st.session_state.today_total,
        "today_records": st.session_state.today_records,
        "history": st.session_state.history
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Main interface
st.title("OneGallonTracker")

# Current progress display
st.metric("Today's Water Intake", f"{int(st.session_state.today_total)} ml / {TARGET_ML} ml")

progress_value = min(st.session_state.today_total / TARGET_ML, 1.0)
st.progress(progress_value)

st.caption(f"Equivalent: {st.session_state.today_total / REFERENCE_BOTTLE:.1f} / {GOAL_BOTTLES} bottles")

# Input section
amount = st.number_input("Amount to add (ml)", min_value=0, step=50, value=650)

if st.button("Add") and amount > 0:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.today_total += amount
    st.session_state.today_records.append({"time": now, "amount": amount})

    # Immediate save
    save_data()

    # Achievement check (only once per day)
    equiv = st.session_state.today_total / REFERENCE_BOTTLE
    today_str = date.today().isoformat()

    if st.session_state.today_total >= TARGET_ML and today_str not in st.session_state.history:
        # Record achievement
        st.session_state.history[today_str] = st.session_state.today_total

        # Show balloons first (before reset)
        st.balloons()
        st.success("★ Goal Achieved! Well done! ★")

        # Reset today's count immediately after celebration
        st.session_state.today_total = 0.0
        st.session_state.today_records = []
        st.session_state.celebrated_today = True

        # Save reset state
        save_data()

        # Allow balloons to be visible for a moment before refresh
        import time
        time.sleep(3.0)  # Gives browser time to render the animation
        st.rerun()

    else:
        st.rerun()

# History section
with st.expander("History"):
    st.write("Today's records (cleared on startup)")
    for rec in sorted(st.session_state.today_records, key=lambda x: x["time"]):
        st.write(f"{rec['time']} : {rec['amount']} ml")

    st.write("Past Achievement Days")
    for d, total in sorted(st.session_state.history.items(), reverse=True):
        st.write(f"{d} : {total} ml"