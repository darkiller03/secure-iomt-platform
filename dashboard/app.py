import streamlit as st

st.set_page_config(page_title="SecureIoMT", layout="wide")

st.title("SecureIoMT Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Connected Devices", 0)
col2.metric("Alerts", 0)
col3.metric("System Status", "Online")

st.subheader("Latest Medical Data")
st.info("Waiting for IoMT data...")

st.subheader("Security Alerts")
st.success("No alerts detected yet.")
