import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
import time
from collections import deque
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Smart IoT Dashboard",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=2000, key="refresh")

# =========================================================
# DATA FILE
# =========================================================

DATA_FILE = "data/live_sensor.json"
ALERT_FILE="data/alerts.csv"

# =========================================================
# SENSOR LOG FILE
# =========================================================

LOG_FILE = "data/sensor_logs.csv"

if not os.path.exists(LOG_FILE):

    log_df = pd.DataFrame(columns=[

        "Timestamp",
        "Temperature",
        "Humidity",
        "Device_Status",
        "Alert"

    ])

    log_df.to_csv(LOG_FILE, index=False)

# =========================================================
# SESSION STATE
# =========================================================

if "temp_history" not in st.session_state:

    st.session_state.temp_history = deque(maxlen=50)

if "hum_history" not in st.session_state:

    st.session_state.hum_history = deque(maxlen=50)

if "packet_history" not in st.session_state:

    st.session_state.packet_history = deque(maxlen=50)

# =========================================================
# SAVE ALERT
# =========================================================

def save_alert(level, message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    new_alert = pd.DataFrame([{

        "Timestamp": timestamp,
        "Level": level,
        "Message": message

    }])

    new_alert.to_csv(
        ALERT_FILE,
        mode='a',
        header=False,
        index=False
    )

# =========================================================
# SAVE SENSOR LOG
# =========================================================

def save_sensor_log(

    temperature,
    humidity,
    device_status,
    alert_message

):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_data = pd.DataFrame([{

        "Timestamp": timestamp,

        "Temperature": temperature,

        "Humidity": humidity,

        "Device_Status": device_status,

        "Alert": alert_message

    }])

    log_data.to_csv(

        LOG_FILE,

        mode='a',

        header=False,

        index=False
    )

# =========================================================
# DEVICE HEALTH STATES
# =========================================================

if "packet_count" not in st.session_state:
    st.session_state.packet_count = 0

if "last_packet_time" not in st.session_state:
    st.session_state.last_packet_time = time.time()

if "dashboard_start_time" not in st.session_state:
    st.session_state.dashboard_start_time = time.time()

if "mqtt_status" not in st.session_state:
    st.session_state.mqtt_status = "ONLINE"

if "last_alert" not in st.session_state:
    st.session_state.last_alert = ""

if "last_logged_temp" not in st.session_state:

    st.session_state.last_logged_temp = None

current_time = time.time()

seconds_since_last_packet = (
    current_time
    - st.session_state.last_packet_time
)

if seconds_since_last_packet > 10:

    device_status = "OFFLINE"
    device_color = "red"

else:

    device_status = "ONLINE"
    device_color = "green"

uptime_seconds = int(
    current_time
    - st.session_state.dashboard_start_time
)

hours = uptime_seconds // 3600
minutes = (uptime_seconds % 3600) // 60
seconds = uptime_seconds % 60

uptime_text = (
    f"{hours:02}:{minutes:02}:{seconds:02}"
)
# =========================================================
# READ SENSOR DATA
# =========================================================

temperature =st.session_state.get("temperature",30)

humidity = st.session_state.get("humidity",60)

if os.path.exists(DATA_FILE):

    try:

        with open(DATA_FILE, "r") as f:

            data = json.load(f)

            temperature = data["temperature"]
            humidity = data["humidity"]
            
            st.session_state.packet_count += 1

            st.session_state.last_packet_time = time.time()

            st.session_state.packet_history.append(
            st.session_state.packet_count)

            st.session_state.temperature=temperature
            st.session_state.humidity=humidity


    except:

        pass

# =========================================================
# STORE HISTORY
# =========================================================

st.session_state.temp_history.append(temperature)
st.session_state.hum_history.append(humidity)

# =========================================================
# ALERT ENGINE
# =========================================================

alert_message = "SYSTEM NORMAL"
alert_level = "NORMAL"
alert_color = "green"

if temperature >= 38:

    alert_message = "CRITICAL HIGH TEMPERATURE"
    alert_level = "CRITICAL"
    alert_color = "red"

elif temperature >= 34:

    alert_message = "HIGH TEMPERATURE WARNING"
    alert_level = "WARNING"
    alert_color = "orange"

elif humidity <= 30:

    alert_message = "LOW HUMIDITY DETECTED"
    alert_level = "WARNING"
    alert_color = "yellow"

elif humidity >= 80:

    alert_message = "HIGH HUMIDITY DETECTED"
    alert_level = "WARNING"
    alert_color = "purple"

# =========================================================
# SAVE SENSOR DATA
# =========================================================

if temperature != st.session_state.last_logged_temp:

    save_sensor_log(

    temperature,
    humidity,
    device_status,
    alert_message
)

    st.session_state.last_logged_temp = temperature

# =========================================================
# STORE NEW ALERTS ONLY
# =========================================================

if alert_message != st.session_state.last_alert:

    if alert_message != "SYSTEM NORMAL":

        save_alert(
            alert_level,
            alert_message
        )

    st.session_state.last_alert = alert_message

#================================================#
#           side bar
# =========================================================

st.sidebar.title("⚙ SYSTEM PANEL")

st.sidebar.markdown("---")

if device_status == "ONLINE":

    st.sidebar.success("🟢 Device Online")

else:

    st.sidebar.error("🔴 Device Offline")

st.sidebar.info(
    f"📡 MQTT Status: {st.session_state.mqtt_status}"
)

st.sidebar.write(
    f"🌡 Temperature: {temperature:.2f} °C"
)

st.sidebar.write(
    f"💧 Humidity: {humidity:.2f} %"
)

st.sidebar.write(
    f"📦 Packets Received: {st.session_state.packet_count}"
)

st.sidebar.write(
    f"⏱ Uptime: {uptime_text}"
)

st.sidebar.write(
    f"🕒 Last Packet: {int(seconds_since_last_packet)} sec ago"
)

st.sidebar.markdown("---")

ALERT_FILE = "data/alerts.csv"

if not os.path.exists(ALERT_FILE):

    alert_df = pd.DataFrame(columns=[
        "Timestamp",
        "Level",
        "Message"
    ])

    alert_df.to_csv(ALERT_FILE, index=False)





# =========================================================
# TITLE
# =========================================================

st.title("🌍 Smart IoT Dashboard")

# =========================================================
# ALERT BANNER
# =========================================================

if alert_level == "CRITICAL":

    st.error(f"🚨 {alert_message}")

elif alert_level == "WARNING":

    st.warning(f"⚠ {alert_message}")

else:

    st.success("✅ SYSTEM NORMAL")

# =========================================================
# CARDS
# =========================================================

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Temperature",
        f"{temperature:.2f} °C"
    )

with c2:

    st.metric(
        "Humidity",
        f"{humidity:.2f} %"
    )

# =========================================================
# GAUGES
# =========================================================

g1, g2 = st.columns(2)

with g1:

    fig_temp = go.Figure(go.Indicator(

        mode="gauge+number",

        value=temperature,

        title={'text': "Temperature"},

        gauge={
            'axis': {'range': [0, 50]}
        }
    ))

    st.plotly_chart(
        fig_temp,
        width='stretch'
    )

with g2:

    fig_hum = go.Figure(go.Indicator(

        mode="gauge+number",

        value=humidity,

        title={'text': "Humidity"},

        gauge={
            'axis': {'range': [0, 100]}
        }
    ))

    st.plotly_chart(
        fig_hum,
        width='stretch'
    )

# =========================================================
# LIVE CHART
# =========================================================

chart_data = pd.DataFrame({

    "Temperature": list(
        st.session_state.temp_history
    ),

    "Humidity": list(
        st.session_state.hum_history
    )
})

fig = px.line(

    chart_data,

    y=[
        "Temperature",
        "Humidity"
    ],

    title="Live Sensor Data"
)

st.plotly_chart(
    fig,
    width='stretch'
)
# =========================================================
# ADVANCED ANALYTICS
# =========================================================

st.markdown("---")

st.subheader("📊 Advanced Analytics")

# =========================================================
# TEMPERATURE ANALYTICS
# =========================================================

temp_list = list(
    st.session_state.temp_history
)

hum_list = list(
    st.session_state.hum_history
)

temp_min = min(temp_list)
temp_max = max(temp_list)
temp_avg = sum(temp_list) / len(temp_list)

hum_min = min(hum_list)
hum_max = max(hum_list)
hum_avg = sum(hum_list) / len(hum_list)

# =========================================================
# ENVIRONMENT SCORE
# =========================================================

environment_score = 100

if temperature > 38:
    environment_score -= 40

elif temperature > 34:
    environment_score -= 20

if humidity < 30:
    environment_score -= 20

elif humidity > 80:
    environment_score -= 20

environment_score = max(
    environment_score,
    0
)

# =========================================================
# TREND DETECTION
# =========================================================

if len(temp_list) >= 2:

    if temp_list[-1] > temp_list[-2]:

        trend = "📈 Rising"

    elif temp_list[-1] < temp_list[-2]:

        trend = "📉 Falling"

    else:

        trend = "➡ Stable"

else:

    trend = "➡ Stable"

# =========================================================
# ANALYTICS CARDS
# =========================================================

a1, a2, a3, a4 = st.columns(4)

with a1:

    st.metric(
        "🌡 Temp Avg",
        f"{temp_avg:.2f} °C"
    )

with a2:

    st.metric(
        "💧 Humidity Avg",
        f"{hum_avg:.2f} %"
    )

with a3:

    st.metric(
        "🧠 Environment Score",
        f"{environment_score}%"
    )

with a4:

    st.metric(
        "📊 Trend",
        trend
    )

# =========================================================
# MIN/MAX TABLE
# =========================================================

analytics_df = pd.DataFrame({

    "Metric": [
        "Temperature",
        "Humidity"
    ],

    "Minimum": [
        round(temp_min, 2),
        round(hum_min, 2)
    ],

    "Maximum": [
        round(temp_max, 2),
        round(hum_max, 2)
    ],

    "Average": [
        round(temp_avg, 2),
        round(hum_avg, 2)
    ]
})

st.dataframe(
    analytics_df,
    width='stretch'
)

# =========================================================
# ENVIRONMENT HEATMAP
# =========================================================

st.markdown("---")

st.subheader("🔥 Environment Heatmap")

# =========================================================
# CREATE HEATMAP DATA
# =========================================================

heatmap_data = np.array([

    list(st.session_state.temp_history),

    list(st.session_state.hum_history)

])

# =========================================================
# HEATMAP FIGURE
# =========================================================

fig_heatmap = px.imshow(

    heatmap_data,

    labels=dict(
        x="Reading Index",
        y="Sensor Type",
        color="Intensity"
    ),

    x=list(range(len(st.session_state.temp_history))),

    y=[
        "Temperature",
        "Humidity"
    ],

    aspect="auto",

    color_continuous_scale="Turbo"
)

fig_heatmap.update_layout(

    paper_bgcolor="#0E1117",

    plot_bgcolor="#1E1E2F",

    font_color="white",

    height=400
)

st.plotly_chart(
    fig_heatmap,
    width='stretch'
)
# =========================================================
# DEVICE HEARTBEAT MONITOR
# =========================================================

st.markdown("---")

st.subheader("📡 Device Heartbeat Monitor")

# =========================================================
# HEARTBEAT STATUS
# =========================================================

heartbeat_delay = int(seconds_since_last_packet)

if heartbeat_delay <= 3:

    heartbeat_status = "🟢 Excellent"

elif heartbeat_delay <= 6:

    heartbeat_status = "🟡 Moderate"

else:

    heartbeat_status = "🔴 Weak"

# =========================================================
# HEARTBEAT CARDS
# =========================================================

h1, h2, h3, h4 = st.columns(4)

with h1:

    st.metric(
        "📦 Packets",
        st.session_state.packet_count
    )

with h2:

    st.metric(
        "📶 Connection Quality",
        heartbeat_status
    )

with h3:

    st.metric(
        "⏱ Last Packet Delay",
        f"{heartbeat_delay} sec"
    )

with h4:

    st.metric(
        "🖥 Device State",
        device_status
    )

# =========================================================
# PACKET RATE CHART
# =========================================================

packet_df = pd.DataFrame({

    "Packet Count": list(
        st.session_state.packet_history
    )
})

fig_packet = px.area(

    packet_df,

    y="Packet Count",

    title="📈 MQTT Packet Activity"
)

fig_packet.update_layout(

    paper_bgcolor="#0E1117",

    plot_bgcolor="#1E1E2F",

    font_color="white",

    height=350
)

st.plotly_chart(
    fig_packet,
    width='stretch'
)


# =========================================================
# ALERT HISTORY
# =========================================================

st.markdown("---")

st.subheader("🚨 Alert History")

try:

    alerts_df = pd.read_csv(ALERT_FILE)

    st.dataframe(
        alerts_df.tail(10),
        width='stretch'
    )

except:

    st.info("No alerts recorded yet.")

# =========================================================
# SENSOR HISTORY TABLE
# =========================================================

st.markdown("---")

st.subheader("📋 Historical Sensor Logs")

try:

    logs_df = pd.read_csv(LOG_FILE)

    st.dataframe(

        logs_df.tail(20),

        width='stretch'
    )

except:

    st.info("No logs available.")

# =========================================================
# CSV EXPORT
# =========================================================

try:

    csv_data = logs_df.to_csv(index=False)

    st.download_button(

        label="⬇ Download Full Sensor Dataset",

        data=csv_data,

        file_name="sensor_logs.csv",

        mime="text/csv"
    )

except:

    pass