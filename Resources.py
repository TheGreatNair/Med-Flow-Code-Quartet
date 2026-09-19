# ============================================================
# SURGICAL EQUIPMENT MANAGER
# ============================================================

class SurgicalEquipmentManager:
    def __init__(self):
        self.total_equipment = {
            "Anesthesia Machine": 2,
            "ECG Monitor": 2,
            "Ventilator": 2,
            "Electrocautery Machine": 1,
            "Surgical Laser": 1,
            "Ultrasound Machine": 1,
            "Infusion Pump": 4,
            # Added your frontend resources here so they connect!
            "ICU Bed": 10,
            "Normal Bed": 42,
            "Doctor": 12,
            "General Doctor": 10,
            "Emergency Doctor": 5
        }
        self.available_equipment = self.total_equipment.copy()
        self.patient_equipment = {}

    def check_availability(self, patient):
        equipment = patient.required_resource
        if equipment not in self.available_equipment:
            return False
        if self.available_equipment[equipment] <= 0:
            return False
        return True

    def allocate_equipment(self, patient):
        if self.check_availability(patient) == False:
            return False
        equipment = patient.required_resource
        self.available_equipment[equipment] -= 1
        self.patient_equipment[patient.patient_id] = equipment
        return True

    def release_equipment(self, patient):
        patient_id = patient.patient_id
        if patient_id not in self.patient_equipment:
            return False
        equipment = self.patient_equipment[patient_id]
        self.available_equipment[equipment] += 1
        del self.patient_equipment[patient_id]
        return True

    def show_equipment(self):
        print("\n========== SURGICAL EQUIPMENT ==========")
        for equipment in self.total_equipment:
            total = self.total_equipment[equipment]
            available = self.available_equipment[equipment]
            used = total - available
            print(equipment, "| Total:", total, "| Available:", available, "| Used:", used)

    def show_utilization(self):
        print("\n====== EQUIPMENT UTILIZATION ======")
        for equipment in self.total_equipment:
            total = self.total_equipment[equipment]
            available = self.available_equipment[equipment]
            used = total - available
            if total > 0:
                percentage = (used / total) * 100
            else:
                percentage = 0
            print(equipment, ":", round(percentage, 2), "%")

# ============================================================
# NEARBY HOSPITAL NETWORK
# ============================================================

class HospitalNetwork:
    def __init__(self):
        self.hospitals = {
            "Hospital A": {
                "Anesthesia Machine": 1, "ECG Monitor": 2, "Ventilator": 0,
                "Electrocautery Machine": 1, "Surgical Laser": 0,
                "Ultrasound Machine": 1, "Infusion Pump": 2
            },
            "Hospital B": {
                "Anesthesia Machine": 0, "ECG Monitor": 1, "Ventilator": 2,
                "Electrocautery Machine": 0, "Surgical Laser": 1,
                "Ultrasound Machine": 0, "Infusion Pump": 3
            },
            "Hospital C": {
                "Anesthesia Machine": 2, "ECG Monitor": 0, "Ventilator": 1,
                "Electrocautery Machine": 1, "Surgical Laser": 0,
                "Ultrasound Machine": 2, "Infusion Pump": 1
            }
        }

    def find_hospital(self, patient):
        equipment = patient.required_resource
        for hospital in self.hospitals:
            if equipment in self.hospitals[hospital]:
                if self.hospitals[hospital][equipment] > 0:
                    return hospital
        return None

    def request_equipment(self, patient):
        hospital = self.find_hospital(patient)
        if hospital is not None:
            print("Equipment available at", hospital)
            print("Communication/transfer request can be initiated.")
            return hospital
        print("Equipment is not available at nearby hospitals.")
        return None

# ============================================================
# SURGERY EQUIPMENT HANDLER
# ============================================================

class SurgeryEquipmentHandler:
    def __init__(self):
        self.equipment_manager = SurgicalEquipmentManager()
        self.hospital_network = HospitalNetwork()

    def handle_patient(self, patient):
        print("\n--------------------------------")
        print("Patient:", patient.patient_id)
        print("Name:", patient.name)
        print("Required equipment:", patient.required_resource)
        if self.equipment_manager.allocate_equipment(patient):
            print("Equipment available in our hospital.")
            print("Equipment allocated successfully.")
            return True
        
        print("Equipment unavailable in our hospital.")
        print("Checking nearby hospitals...")
        hospital = self.hospital_network.request_equipment(patient)
        if hospital is not None:
            print("Recommendation: coordinate with", hospital)
            patient.status = "transferred"
        else:
            print("No nearby hospital has the required equipment.")
            patient.status = "waiting"
        return False