import streamlit as st

st.title("MEDFLOW: Hospital Operations Dashboard")

# Create three columns to display available hospital resources
col1, col2, col3 = st.columns(3)
col1.metric(label="Available ICU Beds", value=5, delta="-2")
col2.metric(label="Available Normal Beds", value=42, delta="-5")
col3.metric(label="Available Doctors", value=12, delta="0")

st.divider()

st.subheader("Live Patient Queue")

# A mock list representing the patient queue with different urgency levels
patient_queue = [
    {"Patient ID": "P-001", "Urgency": "Critical", "Resource Needed": "ICU Bed"},
    {"Patient ID": "P-002", "Urgency": "High", "Resource Needed": "Doctor"},
    {"Patient ID": "P-003", "Urgency": "Low", "Resource Needed": "Normal Bed"}
]

# Display the data as an interactive table
st.dataframe(patient_queue, use_container_width=True)
