# ============================================================
# GENERAL RESOURCE MANAGER
# ============================================================

class ResourceManager:

    def __init__(self, beds, icu_beds, doctors, nurses,
                 ventilators, operating_rooms, ambulances):

        # Resources divided between departments
        self.departments = {

            "Cardiology": {
                "bed": beds // 5,
                "icu_bed": icu_beds // 5,
                "doctor": doctors // 5,
                "nurse": nurses // 5
            },

            "Neurology": {
                "bed": beds // 5,
                "icu_bed": icu_beds // 5,
                "doctor": doctors // 5,
                "nurse": nurses // 5
            },

            "Orthopedics": {
                "bed": beds // 5,
                "icu_bed": icu_beds // 5,
                "doctor": doctors // 5,
                "nurse": nurses // 5
            },

            "General Surgery": {
                "bed": beds // 5,
                "icu_bed": icu_beds // 5,
                "doctor": doctors // 5,
                "nurse": nurses // 5
            },

            "Pediatrics": {
                "bed": beds - (4 * (beds // 5)),
                "icu_bed": icu_beds - (4 * (icu_beds // 5)),
                "doctor": doctors - (4 * (doctors // 5)),
                "nurse": nurses - (4 * (nurses // 5))
            }
        }

        # Hospital-wide resources
        self.total = {
            "ventilator": ventilators,
            "operating_room": operating_rooms,
            "ambulance": ambulances
        }

        self.available = self.total.copy()

        # Resources assigned to patients
        self.patient_resources = {}

        # Department assigned to each patient
        self.patient_departments = {}


    # ========================================================
    # CHOOSE DEPARTMENT
    # ========================================================

    def choose_department(self, patient):

        resource = patient.required_resource

        if resource == "icu_bed":
            return "Cardiology"

        elif resource == "operating_room":
            return "General Surgery"

        elif resource == "bed":
            return "General Surgery"

        elif resource == "doctor":
            return "Cardiology"

        elif resource == "nurse":
            return "Pediatrics"

        else:
            return None


    # ========================================================
    # CHECK AVAILABILITY
    # ========================================================

    def check_availability(self, patient):

        resource = patient.required_resource

        # Hospital-wide resource
        if resource in self.available:

            if self.available[resource] > 0:
                return True

            return False

        # Department resource
        department = self.choose_department(patient)

        if department is None:
            return False

        if resource not in self.departments[department]:
            return False

        if self.departments[department][resource] <= 0:
            return False

        return True


    # ========================================================
    # ALLOCATE RESOURCE
    # ========================================================

    def allocate_resources(self, patient):

        patient_id = patient.patient_id

        # Prevent double allocation
        if patient_id in self.patient_resources:
            return False

        if self.check_availability(patient) == False:
            return False

        resource = patient.required_resource

        # Hospital-wide resource
        if resource in self.available:

            self.available[resource] -= 1

            self.patient_resources[patient_id] = resource
            self.patient_departments[patient_id] = "Hospital-Wide"

        # Department resource
        else:

            department = self.choose_department(patient)

            self.departments[department][resource] -= 1

            self.patient_resources[patient_id] = resource
            self.patient_departments[patient_id] = department

        patient.status = "in treatment"

        return True


    # ========================================================
    # RELEASE RESOURCE
    # ========================================================

    def release_resources(self, patient):

        patient_id = patient.patient_id

        if patient_id not in self.patient_resources:
            return False

        resource = self.patient_resources[patient_id]

        department = self.patient_departments[patient_id]

        # Hospital-wide resource
        if department == "Hospital-Wide":

            self.available[resource] += 1

        # Department resource
        else:

            self.departments[department][resource] += 1

        del self.patient_resources[patient_id]
        del self.patient_departments[patient_id]

        patient.status = "completed"

        return True


    # ========================================================
    # SHOW RESOURCES
    # ========================================================

    def show_resources(self):

        print("\n========== HOSPITAL RESOURCES ==========")

        for department in self.departments:

            print("\n---", department, "---")

            for resource in self.departments[department]:

                print(
                    resource.replace("_", " ").title(),
                    ":",
                    self.departments[department][resource]
                )

        print("\n--- Hospital-Wide Resources ---")

        for resource in self.total:

            total = self.total[resource]
            available = self.available[resource]
            used = total - available

            print(
                resource.replace("_", " ").title(),
                ": Total =", total,
                "| Available =", available,
                "| Used =", used
            )


    # ========================================================
    # SHOW UTILIZATION
    # ========================================================

    def utilization(self):

        print("\n====== RESOURCE UTILIZATION ======")

        for resource in self.total:

            total = self.total[resource]
            available = self.available[resource]
            used = total - available

            if total > 0:
                percentage = (used / total) * 100
            else:
                percentage = 0

            print(
                resource.replace("_", " ").title(),
                ":",
                round(percentage, 2),
                "%"
            )
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
            "Infusion Pump": 4
        }

        self.available_equipment = self.total_equipment.copy()

        self.patient_equipment = {}


    # ========================================================
    # CHECK AVAILABILITY
    # ========================================================

    def check_availability(self, patient):

        equipment = patient.required_resource

        if equipment not in self.available_equipment:
            return False

        if self.available_equipment[equipment] <= 0:
            return False

        return True


    # ========================================================
    # ALLOCATE EQUIPMENT
    # ========================================================

    def allocate_equipment(self, patient):

        patient_id = patient.patient_id

        if patient_id in self.patient_equipment:
            return False

        if self.check_availability(patient) == False:
            return False

        equipment = patient.required_resource

        self.available_equipment[equipment] -= 1

        self.patient_equipment[patient_id] = equipment

        patient.status = "in treatment"

        return True


    # ========================================================
    # RELEASE EQUIPMENT
    # ========================================================

    def release_equipment(self, patient):

        patient_id = patient.patient_id

        if patient_id not in self.patient_equipment:
            return False

        equipment = self.patient_equipment[patient_id]

        self.available_equipment[equipment] += 1

        del self.patient_equipment[patient_id]

        patient.status = "completed"

        return True


    # ========================================================
    # SHOW EQUIPMENT
    # ========================================================

    def show_equipment(self):

        print("\n========== SURGICAL EQUIPMENT ==========")

        for equipment in self.total_equipment:

            total = self.total_equipment[equipment]
            available = self.available_equipment[equipment]
            used = total - available

            print(
                equipment,
                "| Total:", total,
                "| Available:", available,
                "| Used:", used
            )


    # ========================================================
    # UTILIZATION
    # ========================================================

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

            print(
                equipment,
                ":",
                round(percentage, 2),
                "%"
            )


# ============================================================
# NEARBY HOSPITAL NETWORK
# ============================================================

class HospitalNetwork:

    def __init__(self):

        self.hospitals = {

            "Hospital A": {
                "Anesthesia Machine": 1,
                "ECG Monitor": 2,
                "Ventilator": 1,
                "Electrocautery Machine": 1,
                "Surgical Laser": 0,
                "Ultrasound Machine": 1,
                "Infusion Pump": 2
            },

            "Hospital B": {
                "Anesthesia Machine": 0,
                "ECG Monitor": 1,
                "Ventilator": 2,
                "Electrocautery Machine": 0,
                "Surgical Laser": 1,
                "Ultrasound Machine": 0,
                "Infusion Pump": 3
            },

            "Hospital C": {
                "Anesthesia Machine": 2,
                "ECG Monitor": 0,
                "Ventilator": 1,
                "Electrocautery Machine": 1,
                "Surgical Laser": 0,
                "Ultrasound Machine": 2,
                "Infusion Pump": 1
            }
        }


    # ========================================================
    # FIND HOSPITAL
    # ========================================================

    def find_hospital(self, patient):

        equipment = patient.required_resource

        for hospital in self.hospitals:

            if equipment in self.hospitals[hospital]:

                if self.hospitals[hospital][equipment] > 0:

                    return hospital

        return None


    # ========================================================
    # REQUEST EQUIPMENT
    # ========================================================

    def request_equipment(self, patient):

        hospital = self.find_hospital(patient)

        if hospital is not None:

            print(
                "Equipment available at",
                hospital
            )

            print(
                "Communication/transfer request can be initiated."
            )

            return hospital

        print(
            "Equipment is not available at nearby hospitals."
        )

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
        print(
            "Required resource:",
            patient.required_resource
        )

        # Try our hospital first
        if self.equipment_manager.allocate_equipment(patient):

            print(
                "Equipment available in our hospital."
            )

            print(
                "Equipment allocated successfully."
            )

            return True

        # Equipment unavailable
        print(
            "Equipment unavailable in our hospital."
        )

        print(
            "Checking nearby hospitals..."
        )

        hospital = self.hospital_network.request_equipment(
            patient
        )

        if hospital is not None:

            print(
                "Recommendation: coordinate with",
                hospital
            )

            patient.status = "transferred"

        else:

            print(
                "No nearby hospital has the required equipment."
            )

            patient.status = "waiting"

        return False
