# Secure IoMT Platform Demo

Cybersecurity supervision platform for Internet of Medical Things (IoMT). Detects real-time attacks: Data Injection, Device Spoofing, and Denial of Service (DoS).

---

## 1. Clone & Setup

Clone the repository:

```bash
git clone https://github.com/your-org/secure-iomt-platform.git
cd secure-iomt-platform
```

Create and activate a Python virtual environment:

```bash
# Linux/WSL
python3 -m venv venv
source venv/bin/activate

# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 2. Start Docker Stack

Start all services (Mosquitto MQTT broker, Gateway, IDS, Dashboard, Simulators):

```bash
docker compose up -d --build
```

**Verify all services are running:**

```bash
docker compose ps
```

You should see 6 services: `mosquitto`, `gateway`, `ids`, `dashboard`, `normal-simulator`, `multi-simulator`.

---

## 3. Access the Dashboard

Open the Streamlit dashboard in your browser:

```text
http://localhost:8501
```

The dashboard displays:
- **Connected Devices** (4 active medical devices)
- **Security Alerts** (in real-time as attacks are detected)
- **System Metrics** (CPU, Memory)
- **LLM Incident Analysis** (optional Ollama integration)

The dashboard auto-refreshes every 2 seconds.

---

## 4. Run Attack Simulations

From your terminal (with venv activated), run attack scripts:

**4.1 Data Injection Attack** (HRM001 with invalid heart rate):

```bash
./venv/bin/python3 simulator/attack_data_injection.py
```

Expected: `Data Injection` alert in dashboard with severity `High`.

**4.2 Device Spoofing Attack** (unknown device ID):

```bash
./venv/bin/python3 simulator/attack_device_spoofing.py
```

Expected: `Device Spoofing` alert for device `UNKNOWN999` with severity `Medium`.

**4.3 Denial of Service Attack** (1000 rapid messages):

```bash
./venv/bin/python3 simulator/attack_dos.py
```

Expected: `DoS` alert with high anomaly score.

**4.4 View Attack Results:**

- Watch the **Security Alerts** table update in the dashboard
- View raw alerts:

```bash
cat data/alerts.json | jq
```

---

## 5. Clean Up & Reset

### Stop the Docker stack:

```bash
docker compose down
```

### Reset all data files (for a fresh demo):

```bash
# Linux/WSL
sudo sh -c "printf '[]' > data/validated_data.json"
sudo sh -c "printf '[]' > data/alerts.json"
sudo sh -c "printf '[]' > data/logs.json"
sudo sh -c "printf '[]' > data/devices.json"
sudo sh -c "printf '[]' > gateway/data/validated_data.json"
sudo sh -c "printf '[]' > gateway/data/logs.json"

# Or Windows PowerShell (with admin rights):
"[]" | Out-File -Encoding utf8 data/validated_data.json
"[]" | Out-File -Encoding utf8 data/alerts.json
"[]" | Out-File -Encoding utf8 data/logs.json
"[]" | Out-File -Encoding utf8 data/devices.json
"[]" | Out-File -Encoding utf8 gateway/data/validated_data.json
"[]" | Out-File -Encoding utf8 gateway/data/logs.json
```

After cleanup, re-run `docker compose up -d --build` for a fresh demo.

---

## 6. View Logs

Monitor what each service is doing:

```bash
# Gateway (subscribing to MQTT)
docker logs secureiomt-gateway -f

# IDS (detecting attacks)
docker logs secureiomt-ids -f

# Dashboard
docker logs secureiomt-dashboard -f

# Simulators
docker logs secureiomt-normal-simulator -f
docker logs secureiomt-multi-simulator -f
```

---

## Architecture Overview

```
IoT Devices (Simulators)
    ↓ (MQTT publish)
Mosquitto Broker (port 1883)
    ↓ (MQTT subscribe)
Gateway (validates telemetry)
    ↓ (writes JSON)
validated_data.json
    ↓ (polls every 2 sec)
IDS (detects attacks)
    ↓ (writes JSON)
alerts.json
    ↓ (reads every 2 sec)
Dashboard (displays real-time)
    ↓ (http://localhost:8501)
Browser
```

---

## Project Structure

```
secure-iomt-platform/
├── dashboard/          # Streamlit web interface
├── gateway/            # MQTT subscriber & validator
├── ids/                # Intrusion detection system
├── simulator/          # Attack & baseline simulators
├── data/               # Shared data files (JSON)
├── docker-compose.yml  # Container orchestration
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Deactivate Virtual Environment

When done, exit the virtual environment:

```bash
# Linux/WSL
deactivate

# Windows PowerShell
deactivate
```

