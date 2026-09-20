# Med-Flow-Code-Quartet
This repository is for the working of website, which aims to provide assistance on the ever-important schedule of any hospital in general, The following is for a Hack-a-matics conducted by BMSCE.

# 🏥 MEDFLOW: Central Triage Dashboard

**A Live Resource, Patient Management, and Smart Triage System for Modern Hospitals**

## 🚀 The Problem
During peak emergencies, hospitals struggle with real-time resource allocation. Disconnected systems lead to bottlenecks, delayed critical care, and inefficient use of life-saving equipment. 

## 💡 Our Solution
MEDFLOW is a centralized, real-time triage dashboard that seamlessly connects a complex backend resource management system with an intuitive frontend UI. It intelligently routes patients based on clinical urgency and tracks granular hospital resources—from ICU beds to rare blood types—across multiple departments.

## ✨ Key Features
* **Smart Priority Queue:** Automatically sorts incoming patients by clinical urgency (CRITICAL, URGENT, NORMAL, LOW) rather than simple arrival time.
* **Granular Department Tracking:** Manages beds, nurses, and doctors across specialized wards (Cardiology, Neurology, General Surgery, Pediatrics, Orthopedics).
* **Advanced Asset Management:** Tracks comprehensive hospital inventory, including surgical equipment, blood banks, and organ availability.
* **Cross-Hospital Networking:** Automatically initiates transfer protocols to nearby network hospitals if local critical resources (like ICU beds or specific organs) are exhausted.
* **Live Interactive Dashboard:** Provides triage nurses and hospital administrators with a real-time, zero-latency overview of all operations.

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python) for rapid, interactive data visualization.
* **Backend:** Object-Oriented Python (Custom `HospitalSystem`, `PatientPriorityQueue`, and `ResourceManager` classes).

## 💻 How to Run Locally
1. Clone this repository.
2. Install dependencies: `pip install streamlit`
3. Run the application: `streamlit run app.py`

---
*Team Code Quartet*
