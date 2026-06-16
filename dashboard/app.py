import json
from pathlib import Path

import pandas as pd
import streamlit as st
import requests
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

DEVICES_FILE = BASE_DIR / "data" / "devices.json"
ALERTS_FILE = BASE_DIR / "data" / "alerts.json"
LOGS_FILE = BASE_DIR / "data" / "logs.json"

st.set_page_config(
    page_title="SecureIoMT",
    layout="wide"
)

st.title("SecureIoMT Dashboard")
st.caption(
    "Cybersecurity supervision platform for Internet of Medical Things"
)


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


devices = load_json(DEVICES_FILE, [])
alerts = load_json(ALERTS_FILE, [])
logs = load_json(LOGS_FILE, [])

# ======================
# Metrics
# ======================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Connected Devices", len(devices))
col2.metric("Security Alerts", len(alerts))
col3.metric("System Status", "Online")
col4.metric("Log Events", len(logs))

st.divider()

# ======================
# Devices
# ======================

st.subheader("Medical Devices")

if devices:
    devices_df = pd.DataFrame(devices)
    st.dataframe(devices_df, width="stretch")
else:
    st.info("No device data available.")

# ======================
# Alerts
# ======================

st.subheader("Security Alerts")

if alerts:
    st.error(f"{len(alerts)} alert(s) detected")

    alerts_df = pd.DataFrame(alerts)
    st.dataframe(alerts_df, width="stretch")

else:
    st.success("No security alerts detected.")

# ======================
# Logs
# ======================

st.subheader("System Logs")

if logs:
    logs_df = pd.DataFrame(logs)
    st.dataframe(logs_df, width="stretch")
else:
    st.info("No system logs available.")

# ======================
# LLM Analysis
# ======================
def analyze_with_ollama(alert):
    prompt = f"""
You are a cybersecurity assistant for an Internet of Medical Things platform.

Analyze this security alert:

Alert type: {alert.get("alert_type", alert.get("type", "Unknown"))}
Device: {alert.get("device_id", alert.get("device", "Unknown"))}
Severity: {alert.get("severity", "Unknown")}
Description: {alert.get("description", "No description")}
Recommended action: {alert.get("recommended_action", "No action provided")}

Give:
1. Short incident explanation
2. Possible cause
3. Risk level
4. Recommended action

Keep it concise.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()
    return response.json()["response"]


st.subheader("LLM Incident Analysis")

if alerts:
    alert_options = [
        f"{alert.get('alert_id', i)} - {alert.get('alert_type', alert.get('type', 'Unknown'))} - {alert.get('device_id', alert.get('device', 'Unknown'))}"
        for i, alert in enumerate(alerts)
    ]

    selected_option = st.selectbox(
        "Select an alert to analyze",
        alert_options
    )

    selected_index = alert_options.index(selected_option)
    selected_alert = alerts[selected_index]

    if st.button("Analyze with AI"):
        with st.spinner("Analyzing incident with Phi-3..."):
            try:
                ai_analysis = analyze_with_ollama(selected_alert)
                st.warning(ai_analysis)
            except Exception as error:
                st.error(f"Ollama analysis failed: {error}")

else:
    st.info("No alerts available for AI analysis.")

# ======================
# Automatic Incident Report
# ======================

st.subheader("Automatic Incident Report")

def generate_incident_report(alerts):
    severities = Counter(
        alert.get("severity", "Unknown")
        for alert in alerts
    )

    alert_types = Counter(
        alert.get("alert_type", alert.get("type", "Unknown"))
        for alert in alerts
    )

    affected_devices = sorted(set(
        alert.get("device_id", alert.get("device", "Unknown"))
        for alert in alerts
    ))

    report_context = f"""
Total alerts: {len(alerts)}

Severity distribution:
{dict(severities)}

Alert types:
{dict(alert_types)}

Affected devices:
{', '.join(affected_devices)}
"""

    prompt = f"""
You are a cybersecurity analyst for an Internet of Medical Things platform.

Generate a concise incident report based on the following IDS alerts summary:

{report_context}

The report must include:
1. Executive summary
2. Main detected threats
3. Risk assessment
4. Recommended actions

Keep the report clear and professional.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False
        },
        timeout=90
    )

    response.raise_for_status()
    return response.json()["response"]


if alerts:
    if st.button("Generate Incident Report"):
        with st.spinner("Generating incident report with Phi-3..."):
            try:
                report = generate_incident_report(alerts)
                st.markdown(report)

                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name="secure_iomt_incident_report.md",
                    mime="text/markdown"
                )

            except Exception as error:
                st.error(f"Report generation failed: {error}")
else:
    st.info("No alerts available to generate a report.")