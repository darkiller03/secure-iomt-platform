import json
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DEVICES_FILE = BASE_DIR / "data" / "devices.json"
ALERTS_FILE = BASE_DIR / "data" / "alerts.json"

st.set_page_config(page_title="SecureIoMT", layout="wide")

st.title("SecureIoMT Dashboard")
st.caption("Cybersecurity supervision platform for Internet of Medical Things")

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default

devices = load_json(DEVICES_FILE, [])
alerts = load_json(ALERTS_FILE, [])

col1, col2, col3 = st.columns(3)
col1.metric("Connected Devices", len(devices))
col2.metric("Security Alerts", len(alerts))
col3.metric("System Status", "Online")

st.divider()

st.subheader("Medical Devices")
if devices:
    st.dataframe(pd.DataFrame(devices), use_container_width=True)
else:
    st.info("No device data available.")

st.subheader("Security Alerts")
if alerts:
    st.error("Alerts detected")
    st.dataframe(pd.DataFrame(alerts), use_container_width=True)
else:
    st.success("No security alerts detected.")

st.subheader("LLM Incident Analysis")
st.info("Waiting for IDS alerts to generate analysis.")