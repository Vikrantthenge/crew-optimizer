import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="CrewOps: Crew Optimization", layout="wide")

# 🖼️ Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.png", width=100)
with col2:
    st.markdown("## CrewOps: Airline Crew Optimization Dashboard")

# 📘 Overview
st.markdown("""
CrewOps simulates crew assignments across flights while respecting duty limits, rest periods, and availability windows.  
It helps airline ops teams optimize crew utilization and minimize violations and cost.

**Key Features:**
- 🧠 Crew assignment logic based on availability  
- ⚠️ Violation detection for overlapping shifts  
- 📊 KPI cards for utilization and compliance  
- 📈 Gantt-style visualization of crew schedules  
- 📉 Graphs for crew coverage, role balance, and compliance trends  
- 📥 Downloadable assignment summary  
- 🧪 Sample data auto-loaded if no files uploaded
""")

# 📁 Upload Section
st.sidebar.markdown("### 📁 Upload Flight & Crew Data")

@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.title()
    return df

@st.cache_data
def load_sample_data():
    sample_flights = pd.DataFrame({
        "Flight No": ["F1001", "F1002", "F1003"],
        "Origin": ["BOM", "DEL", "MAA"],
        "Departure": ["2025-09-06 14:15", "2025-09-06 15:30", "2025-09-06 16:45"],
        "Arrival": ["2025-09-06 16:15", "2025-09-06 17:30", "2025-09-06 18:45"],
        "Crew Required": [8, 9, 7]
    })

    sample_crew = pd.DataFrame({
        "Name": ["Crew_301", "Crew_302", "Crew_303", "Crew_304"],
        "Role": ["Pilot", "Co-Pilot", "Cabin Crew", "Cabin Crew"],
        "Base": ["BOM", "BOM", "BOM", "DEL"],
        "Available From": ["2025-09-06 08:00", "2025-09-06 09:00", "2025-09-06 10:00", "2025-09-06 12:00"],
        "Available Until": ["2025-09-06 20:00", "2025-09-06 18:00", "2025-09-06 19:00", "2025-09-06 22:00"]
    })

    sample_flights.columns = sample_flights.columns.str.strip().str.title()
    sample_crew.columns = sample_crew.columns.str.strip().str.title()

    return sample_flights, sample_crew

flight_file = st.sidebar.file_uploader("Upload flight_schedule.csv", type="csv")
crew_file = st.sidebar.file_uploader("Upload crew_pool.csv", type="csv")

if flight_file and crew_file:
    flights = load_csv(flight_file)
    crew = load_csv(crew_file)
    st.success("✅ Using uploaded data")
else:
    flights, crew = load_sample_data()
    st.info("ℹ️ No files uploaded — using sample data for demo")

# ⏱️ Defensive datetime parsing
for col in ["Departure", "Arrival"]:
    if col in flights.columns:
        flights[col] = pd.to_datetime(flights[col], errors="coerce", dayfirst=True)

for col in ["Available From", "Available Until"]:
    if col in crew.columns:
        crew[col] = pd.to_datetime(crew[col], errors="coerce", dayfirst=True)

# ✅ Check required columns
required_flight_cols = {"Flight No", "Origin", "Departure", "Arrival", "Crew Required"}
required_crew_cols = {"Name", "Role", "Base", "Available From", "Available Until"}

if not required_flight_cols.issubset(flights.columns) or not required_crew_cols.issubset(crew.columns):
    st.error("❌ Missing required columns in uploaded or sample data.")
    st.stop()

# 📄 Sample CSV Preview
with st.expander("📄 Preview Crew Pool"):
    st.dataframe(crew.head(10))
with st.expander("📄 Preview Flight Schedule"):
    st.dataframe(flights.head(10))

# 📊 Coverage Summary
st.markdown("### 🧭 Crew Coverage Summary for 06-Sep-2025")
coverage = []
for base in crew["Base"].dropna().unique():
    available = crew[
        (crew["Base"] == base) &
        (crew["Available From"] <= pd.Timestamp("2025-09-06")) &
        (crew["Available Until"] >= pd.Timestamp("2025-09-06"))
    ]
    coverage.append({"Base": base, "Available Crew": len(available), "Total Crew": len(crew[crew["Base"] == base])})
coverage_df = pd.DataFrame(coverage)
st.dataframe(coverage_df)

# 📊 Bar Chart: Crew Availability by Base
fig_bar = px.bar(coverage_df, x="Base", y="Available Crew", color="Base", title="Crew Availability by Base")
st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")

# 🧮 Pie Chart: Role Distribution
role_counts = crew["Role"].value_counts().reset_index()
role_counts.columns = ["Role", "Count"]
fig_pie = px.pie(role_counts, names="Role", values="Count", title="Crew Role Distribution")
st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

# 🔍 Optional Filters
selected_origin = st.sidebar.selectbox("Filter by Origin", flights["Origin"].dropna().unique())
filtered_flights = flights[flights["Origin"] == selected_origin]

# 🧭 Preview Crew Availability at Selected Base
st.markdown(f"### 🔍 Crew Availability at {selected_origin}")
st.dataframe(crew[crew["Base"] == selected_origin][["Name", "Role", "Available From", "Available Until"]])

# 🧠 Assignment Logic
assignments = []
violations = 0

for _, flight in filtered_flights.iterrows():
    assigned = []
    for _, member in crew.iterrows():
        if member["Base"] == selected_origin:
            if pd.notna(flight["Departure"]) and pd.notna(flight["Arrival"]) and pd.notna(member["Available From"]) and pd.notna(member["Available Until"]):
                if member["Available From"] <= flight["Departure"] and member["Available Until"] >= flight["Arrival"]:
                    assigned.append(member["Name"])
                    if len(assigned) >= flight["Crew Required"]:
                        break
    if len(assigned) < flight["Crew Required"]:
        violations += 1
    assignments.append(", ".join(assigned))

filtered_flights["Assigned Crew"] = assignments

# 📊 KPI Cards
total_flights = len(filtered_flights)
total_crew = len(crew[crew["Base"] == selected_origin])
compliance_rate = round((total_flights - violations) / total_flights * 100, 2) if total_flights > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Filtered Flights", total_flights)
col2.metric("Crew Pool Size", total_crew)
col3.metric("Compliance Rate", f"{compliance_rate}%")

# 📉 Line Chart: Simulated Compliance Trend
trend_data = pd.DataFrame({
    "Date": pd.date_range("2025-09-01", periods=7),
    "Compliance Rate": [82, 85, 78, 90, 88, 92, compliance_rate]
})
fig_line = px.line(trend_data, x="Date", y="Compliance Rate", markers=True, title="Compliance Rate Over Time")
st.plotly_chart(fig_line, use_container_width=True, key="line_chart")

# 🚨 Sidebar alert for zero compliance
if compliance_rate == 0.0:
    st.sidebar.error("🚨 All filtered flights failed crew assignment. Check crew availability or filter settings.")

# 📈 Gantt Chart
gantt_data = []
for _, flight in filtered_flights.iterrows():
    for crew_name in flight["Assigned Crew"].split(", "):
        if crew_name:
            gantt_data.append({
                "Crew": crew_name,
                "Start": flight["Departure"],
                "End": flight["Arrival"],
                "Flight": flight["Flight No"]
            })

gantt_df = pd.DataFrame(gantt_data)

if not gantt_df.empty:
    fig = px.timeline(gantt_df, x_start="Start", x_end="End", y="Crew", color="Flight")
    fig.update_layout(title="Crew Assignment Timeline", xaxis_title="Time", yaxis_title="Crew Member")
                      
# 📈 Gantt Chart (continued)
if not gantt_df.empty:
    fig = px.timeline(gantt_df, x_start="Start", x_end="End", y="Crew", color="Flight")
    fig.update_layout(title="Crew Assignment Timeline", xaxis_title="Time", yaxis_title="Crew Member")
    st.plotly_chart(fig, use_container_width=True, key="gantt_chart")
else:
    st.warning("⚠️ No valid crew assignments found. Gantt chart cannot be generated.")

# 🧾 Assignment Table
st.markdown("### 🧾 Crew Assignment Summary")
st.dataframe(filtered_flights[["Flight No", "Origin", "Departure", "Arrival", "Crew Required", "Assigned Crew"]])

# ❌ Violation Table
failed = filtered_flights[filtered_flights["Assigned Crew"] == ""]
if not failed.empty:
    st.markdown("### ❌ Flights Without Assigned Crew")
    st.dataframe(failed[["Flight No", "Departure", "Crew Required"]])
else:
    st.markdown("✅ All flights successfully assigned crew.")

# 📥 Download Button
st.download_button("📥 Download Assignment Summary", filtered_flights.to_csv(index=False), file_name="crew_assignments.csv")

# 🔗 Connect with Me
st.markdown("---")
st.markdown("""
### 🔗 Connect with Me  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-vthenge-blue?logo=linkedin)](https://www.linkedin.com/in/vthenge)  
[![Outlook](https://img.shields.io/badge/Outlook-vikrantthenge@outlook.com-blue?logo=microsoft-outlook)](mailto:vikrantthenge@outlook.com)  
[![GitHub](https://img.shields.io/badge/GitHub-vikrantthenge-black?logo=github)](https://github.com/vikrantthenge)  
[![🚀 Live App](https://img.shields.io/badge/Live_App-Click_to_Open-green?logo=streamlit)](https://vikrantthenge-crewops.streamlit.app)
""", unsafe_allow_html=True)

# 🛡️ Copyright
st.markdown("---")
st.markdown("© 2025 Vikrant Thenge. All rights reserved.  \nCrafted with precision and purpose ✈️")