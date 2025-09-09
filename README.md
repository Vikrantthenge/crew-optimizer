# Crew Ops: Airline Crew Optimization Dashboard

**Built by [Vikrant Thenge](https://www.linkedin.com/in/vthenge)** 

CrewOps helps airline ops teams assign crew to flights while respecting duty limits, rest periods, and availability windows. It simulates real-world constraints and visualizes crew schedules with clarity.

---

## 🚀 Live App  
[![CrewOps – Live App](https://img.shields.io/badge/CrewOps-Dashboard-green?logo=streamlit)](https://vikrantthenge-crewops.streamlit.app)
[![CrewOps CI](https://github.com/Vikrantthenge/crew-optimizer/actions/workflows/crewops-ci.yml/badge.svg)](https://github.com/Vikrantthenge/crew-optimizer/actions/workflows/crewops-ci.yml)


## 🔄 CI/CD Integration

This app uses **GitHub Actions** for Continuous Integration and Deployment:

- ✅ Linting via `flake8` to ensure clean, error-free code
- ✅ Optional unit testing via `pytest`
- ✅ Auto-deployment to Streamlit Cloud on every push to `main`
- ✅ Live CI badge reflects build health and workflow status

Every update is automatically validated and deployed, ensuring production-grade reliability and faster iteration.


## 📸 Logo  
![CrewOps Logo](logo.png)

---

## 📊 Key Features

- 🧠 Intelligent crew assignment logic  
- ⚠️ Violation detection for overlapping shifts  
- 📈 Gantt-style visualization of crew schedules  
- 📊 KPI cards for utilization and compliance  
- 📉 Charts for crew coverage, role balance, and compliance trends  
- 📥 Downloadable assignment summary  
- 🧪 Sample data auto-loaded for demo users

---

## 📁 Sample Data Included

- `sample_flight_schedule.csv`  
- `sample_crew_pool.csv`  

These files auto-load if no uploads are provided — perfect for recruiters or demo users.

---

## 🧪 Tech Stack

- `Streamlit`  
- `Pandas`  
- `Plotly`  
- `Python 3.9+`
