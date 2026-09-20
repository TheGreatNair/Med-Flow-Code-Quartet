import streamlit as st
import time
from Patients import PatientPriorityQueue, Patient, Urgency
from Resources import SurgeryEquipmentHandler

# --- INITIALIZE BACKEND LOGIC ---
# This keeps the data from resetting every time you click a button
if 'queue' not in st.session_state:
    st.session_state.queue = PatientPriorityQueue()
if 'hospital' not in st.session_state:
    st.session_state.hospital = SurgeryEquipmentHandler()

st.title("MEDFLOW: Hospital Operations Dashboard")

# --- SIDEBAR: ADMIT NEW PATIENT ---
st.sidebar.header("Admit New Patient")
new_patient_id = st.sidebar.text_input("Patient ID (e.g., P-004)")
new_name = st.sidebar.text_input("Patient Name")
urgency_level = st.sidebar.selectbox("Urgency Level", ["CRITICAL", "URGENT", "NORMAL", "LOW"])
resource_needed = st.sidebar.selectbox("Resource Needed", ["ICU Bed", "Normal Bed", "Doctor", "Ventilator"])

if st.sidebar.button("Add to Queue"):
    # Convert text to the Urgency Enum your teammate made
    urgency_enum = getattr(Urgency, urgency_level)
    
    # Create the new patient
    new_patient = Patient(
        patient_id=new_patient_id,
        name=new_name,
        urgency=urgency_enum,
        arrival_time=int(time.time()),
        required_resource=resource_needed,
        estimated_service_time=30
    )
    
    # Add to the backend queue
    st.session_state.queue.add_patient(new_patient)
    st.sidebar.success(f"{new_name} added to the waiting room!")

# --- MAIN DASHBOARD: LIVE METRICS ---
# Pull live equipment counts from your teammate's inventory tracker
eq_manager = st.session_state.hospital.equipment_manager

col1, col2, col3 = st.columns(3)
col1.metric("Available ICU Beds", eq_manager.available_equipment.get("ICU Bed", 0))
col2.metric("Available Normal Beds", eq_manager.available_equipment.get("Normal Bed", 0))
col3.metric("Available Doctors", eq_manager.available_equipment.get("Doctor", 0))

st.divider()

# --- MAIN DASHBOARD: LIVE QUEUE ---
st.subheader("Live Patient Queue")

current_time = int(time.time())
waiting_patients = st.session_state.queue.list_queue(current_time)

if waiting_patients:
    # Convert the complex patient data into a simple table for Streamlit
    queue_data = [
        {
            "Patient ID": p.patient_id, 
            "Name": p.name, 
            "Urgency": p.urgency.name, 
            "Resource Needed": p.required_resource
        } 
        for p in waiting_patients
    ]
    st.dataframe(queue_data, use_container_width=True)
else:
    st.info("The waiting room is currently empty.")