import streamlit as st
st.set_page_config(
    page_title="MEDFLOW Hospital Triage",
    page_icon="🏥",
    layout="wide"
)
import time
from Patients import PatientPriorityQueue, Patient, Urgency
from Resources import HospitalSystem

# --- INITIALIZE BACKEND LOGIC ---
# This keeps the data from resetting every time you click a button
if 'queue' not in st.session_state:
    st.session_state.queue = PatientPriorityQueue()
if 'hospital' not in st.session_state:
    st.session_state.hospital = HospitalSystem()

st.markdown("<h1 style='text-align: center; color: #005b96;'>🏥 MEDFLOW: Central Triage Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Live Resource & Patient Management System</p>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR: ADMIT NEW PATIENT ---
st.sidebar.header("Admit New Patient")
new_patient_id = st.sidebar.text_input("Patient ID (e.g., P-004)")
new_name = st.sidebar.text_input("Patient Name")
urgency_level = st.sidebar.selectbox("Urgency Level", ["CRITICAL", "URGENT", "NORMAL", "LOW"])
resource_needed = st.sidebar.selectbox("Resource Needed", ["ICU Bed", "Normal Bed", "Doctor", "Ventilator"])
department_choice = st.sidebar.selectbox("Department", ["Cardiology", "Neurology", "Orthopedics", "General Surgery", "Pediatrics"])

if st.sidebar.button("Add to Queue"):
        # Map UI dropdown to his backend code names
        resource_map = {
            "ICU Bed": "icu_bed", 
            "Normal Bed": "bed", 
            "Doctor": "doctor", 
            "Ventilator": "ventilator"
        }
        backend_resource = resource_map[resource_needed]

        # Convert text to the Urgency Enum your teammate made
        urgency_enum = getattr(Urgency, urgency_level)

        # Create the new patient
        new_patient = Patient(
            patient_id=new_patient_id,
            name=new_name,
            urgency=urgency_enum,
            arrival_time=int(time.time()),
            required_resource=backend_resource,
            estimated_service_time=30
        )
# Attach the user's chosen department dynamically!
        new_patient.department = department_choice
        # Add to the backend queue
        st.session_state.queue.add_patient(new_patient)
        st.sidebar.success(f"{new_name} added to the waiting room!")

# --- MAIN DASHBOARD: LIVE METRICS ---
# Sum up all the resources across his 5 departments
hospital_sys = st.session_state.hospital
depts = hospital_sys.resource_manager.departments

available_icu = sum(dept["icu_bed"] for dept in depts.values())
available_normal = sum(dept["bed"] for dept in depts.values())
available_doctors = sum(dept["doctor"] for dept in depts.values())

# Safely grab ventilators from the equipment manager (or departments as a fallback)
if hasattr(hospital_sys, "surgery_manager"):
    available_ventilators = hospital_sys.surgery_manager.available_equipment.get("ventilator", 0)
else:
    available_ventilators = sum(dept.get("ventilator", 0) for dept in depts.values())

# Change to 4 columns to fit the new metric
col1, col2, col3, col4 = st.columns(4)
col1.metric("Available ICU Beds", available_icu)
col2.metric("Available Normal Beds", available_normal)
col3.metric("Available Doctors", available_doctors)
col4.metric("Available Ventilators", available_ventilators)
st.divider()

# --- DETAILED INVENTORY TABS ---
st.subheader("Comprehensive Hospital Inventory")

# Create interactive tabs for a clean UI
tab1, tab2, tab3 = st.tabs(["🏥 Departments", "🩸 Blood & Organs", "⚕️ Equipment"])

with tab1:
    st.write("Live bed and staff counts by department:")
    st.dataframe(st.session_state.hospital.resource_manager.departments, use_container_width=True)
    
with tab2:
    col_b, col_o = st.columns(2)
    with col_b:
        st.write("Blood Bank (Units):")
        st.dataframe(st.session_state.hospital.resource_manager.blood_bank, use_container_width=True)
    with col_o:
        st.write("Organ Bank (Availability):")
        st.dataframe(st.session_state.hospital.resource_manager.organ_bank, use_container_width=True)
        
with tab3:
    st.write("Available Surgical Equipment:")
    st.dataframe(st.session_state.hospital.surgery_manager.available_equipment, use_container_width=True)
    
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
    # --- MAIN DASHBOARD: HOSPITAL ACTIONS ---
st.divider()
st.subheader("Hospital Actions")

# We use type="primary" to make this button stand out visually
if st.button("Treat Next Priority Patient", type="primary"):
    current_time = int(time.time())
    waiting_patients = st.session_state.queue.list_queue(current_time)
    
    if len(waiting_patients) == 0:
        st.info("No patients are currently waiting.")
    else:
        top_patient = waiting_patients[0]
        
        # This triggers your teammate's massive allocation logic!
        success = st.session_state.hospital.allocate_resource(top_patient)
        
        if success:
            st.session_state.queue.remove_patient(top_patient.patient_id)
            st.success(f"Success! {top_patient.name} has been allocated their resource and is in treatment.")
            st.rerun()
        else:
            st.error(f"Cannot treat {top_patient.name}! Resource is unavailable in our hospital.")