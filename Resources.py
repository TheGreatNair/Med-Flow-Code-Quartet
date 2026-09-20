# ============================================================
# HOSPITAL RESOURCE MANAGEMENT MODULE
# ============================================================


# ============================================================
# GENERAL RESOURCE MANAGER
# ============================================================

class ResourceManager:

    def __init__(self, beds, icu_beds, doctors, nurses,
                 ventilators, operating_rooms, ambulances):

        # --------------------------------------------------------
        # DEPARTMENT RESOURCES
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # HOSPITAL-WIDE RESOURCES
        # --------------------------------------------------------

        self.total = {
            "ventilator": ventilators,
            "operating_room": operating_rooms,
            "ambulance": ambulances
        }

        self.available = self.total.copy()

        # Resources assigned to patients
        self.patient_resources = {}

        # Department assigned to patients
        self.patient_departments = {}

        # --------------------------------------------------------
        # BLOOD BANK
        # --------------------------------------------------------

        self.blood_bank = {
            "A+": 10,
            "A-": 5,
            "B+": 10,
            "B-": 5,
            "AB+": 5,
            "AB-": 3,
            "O+": 15,
            "O-": 7
        }

        # Blood given to patients
        self.patient_blood = {}

        # --------------------------------------------------------
        # ORGAN BANK
        # --------------------------------------------------------

        self.organ_bank = {
            "Kidney": 2,
            "Liver": 1,
            "Heart": 1,
            "Lung": 2,
            "Pancreas": 1
        }

        # Organs allocated to patients
        self.patient_organs = {}


    # ============================================================
    # CHOOSE DEPARTMENT
    # ============================================================

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

        return None


    # ============================================================
    # CHECK RESOURCE AVAILABILITY
    # ============================================================

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


    # ============================================================
    # ALLOCATE RESOURCE
    # ============================================================

    def allocate_resources(self, patient):

        patient_id = patient.patient_id

        # Prevent double allocation
        if patient_id in self.patient_resources:
            return False

        # Check availability
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


    # ============================================================
    # RELEASE RESOURCE
    # ============================================================

    def release_resources(self, patient):

        patient_id = patient.patient_id

        if patient_id not in self.patient_resources:
            return False

        resource = self.patient_resources[patient_id]
        department = self.patient_departments[patient_id]

        if department == "Hospital-Wide":

            self.available[resource] += 1

        else:

            self.departments[department][resource] += 1

        del self.patient_resources[patient_id]
        del self.patient_departments[patient_id]

        patient.status = "completed"

        return True


    # ============================================================
    # ICU TRANSFER
    # ============================================================

    def check_icu_transfer(self, patient, hospital_network):

        if patient.required_resource != "icu_bed":
            return False

        # Check our hospital first
        if self.check_availability(patient):
            return False

        print("\nICU beds unavailable in our hospital.")
        print("Checking nearby hospitals...")

        hospital = hospital_network.find_icu_hospital()

        if hospital is not None:

            print("ICU bed available at", hospital)
            print("Patient can be transferred to", hospital)

            patient.status = "transferred"

            return True

        print("No nearby hospital has an available ICU bed.")

        patient.status = "waiting"

        return False


    # ============================================================
    # BLOOD SUPPLY
    # ============================================================

    def check_blood(self, blood_group, units=1):

        if blood_group not in self.blood_bank:
            return False

        if self.blood_bank[blood_group] >= units:
            return True

        return False


    def allocate_blood(self, patient, blood_group, units=1):

        patient_id = patient.patient_id

        if patient_id in self.patient_blood:
            return False

        if self.check_blood(blood_group, units) == False:

            print("Required blood is not available.")

            return False

        self.blood_bank[blood_group] -= units

        self.patient_blood[patient_id] = {
            "blood_group": blood_group,
            "units": units
        }

        print(
            units,
            "unit(s) of",
            blood_group,
            "blood allocated to",
            patient_id
        )

        return True


    def release_blood(self, patient):

        patient_id = patient.patient_id

        if patient_id not in self.patient_blood:
            return False

        blood_group = self.patient_blood[patient_id]["blood_group"]
        units = self.patient_blood[patient_id]["units"]

        self.blood_bank[blood_group] += units

        del self.patient_blood[patient_id]

        return True


    def show_blood_supply(self):

        print("\n========== BLOOD BANK ==========")

        for blood_group in self.blood_bank:

            print(
                blood_group,
                ":",
                self.blood_bank[blood_group],
                "unit(s)"
            )


    # ============================================================
    # ORGAN DONATION
    # ============================================================

    def check_organ(self, organ):

        if organ not in self.organ_bank:
            return False

        if self.organ_bank[organ] > 0:
            return True

        return False


    def allocate_organ(self, patient, organ):

        patient_id = patient.patient_id

        if patient_id in self.patient_organs:
            return False

        if self.check_organ(organ) == False:

            print("Required organ is not available locally.")

            return False

        self.organ_bank[organ] -= 1

        self.patient_organs[patient_id] = organ

        print(
            organ,
            "allocated to patient",
            patient_id
        )

        return True


    def release_organ(self, patient):

        patient_id = patient.patient_id

        if patient_id not in self.patient_organs:
            return False

        organ = self.patient_organs[patient_id]

        self.organ_bank[organ] += 1

        del self.patient_organs[patient_id]

        return True


    # ============================================================
    # REQUEST ORGAN
    # ============================================================

    def request_organ(self, patient, organ, hospital_network):

        patient_id = patient.patient_id

        # First check our own hospital
        if self.check_organ(organ):

            self.allocate_organ(patient, organ)

            return {
                "status": "available",
                "hospital": "Our Hospital",
                "message": organ + " allocated from our hospital."
            }

        # If unavailable, contact nearby hospitals
        hospital = hospital_network.request_organ(organ)

        if hospital is not None:

            return {
                "status": "requested",
                "hospital": hospital,
                "message": (
                    organ +
                    " requested from " +
                    hospital +
                    " for patient " +
                    patient_id
                )
            }

        return {
            "status": "unavailable",
            "hospital": None,
            "message": (
                organ +
                " is unavailable locally and at nearby hospitals."
            )
        }


    # ============================================================
    # SHOW ORGAN SUPPLY
    # ============================================================

    def show_organ_supply(self):

        print("\n========== ORGAN DONATION ==========")

        for organ in self.organ_bank:

            print(
                organ,
                ":",
                self.organ_bank[organ],
                "available"
            )


    # ============================================================
    # SHOW ALL RESOURCES
    # ============================================================

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


    # ============================================================
    # RESOURCE UTILIZATION
    # ============================================================

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
            "Electrocautery Machine": 1,
            "Surgical Laser": 1,
            "Ultrasound Machine": 1,
            "Infusion Pump": 4
        }

        self.available_equipment = self.total_equipment.copy()

        self.patient_equipment = {}


    # ============================================================
    # CHECK EQUIPMENT
    # ============================================================

    def check_availability(self, patient):

        equipment = patient.required_resource

        if equipment not in self.available_equipment:
            return False

        if self.available_equipment[equipment] <= 0:
            return False

        return True


    # ============================================================
    # ALLOCATE EQUIPMENT
    # ============================================================

    def allocate_equipment(self, patient):

        patient_id = patient.patient_id

        if patient_id in self.patient_equipment:
            return False

        if self.check_availability(patient) == False:
            return False

        equipment = patient.required_resource

        self.available_equipment[equipment] -= 1

        self.patient_equipment[patient_id] = equipment

        return True


    # ============================================================
    # RELEASE EQUIPMENT
    # ============================================================

    def release_equipment(self, patient):

        patient_id = patient.patient_id

        if patient_id not in self.patient_equipment:
            return False

        equipment = self.patient_equipment[patient_id]

        self.available_equipment[equipment] += 1

        del self.patient_equipment[patient_id]

        return True


    # ============================================================
    # SHOW EQUIPMENT
    # ============================================================

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


    # ============================================================
    # EQUIPMENT UTILIZATION
    # ============================================================

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
                "Infusion Pump": 2,

                "ICU Bed": 2,

                "Kidney": 1,
                "Liver": 0,
                "Heart": 1,
                "Lung": 1,
                "Pancreas": 0
            },

            "Hospital B": {

                "Anesthesia Machine": 0,
                "ECG Monitor": 1,
                "Ventilator": 2,
                "Electrocautery Machine": 0,
                "Surgical Laser": 1,
                "Ultrasound Machine": 0,
                "Infusion Pump": 3,

                "ICU Bed": 3,

                "Kidney": 2,
                "Liver": 1,
                "Heart": 0,
                "Lung": 1,
                "Pancreas": 1
            },

            "Hospital C": {

                "Anesthesia Machine": 2,
                "ECG Monitor": 0,
                "Ventilator": 1,
                "Electrocautery Machine": 1,
                "Surgical Laser": 0,
                "Ultrasound Machine": 2,
                "Infusion Pump": 1,

                "ICU Bed": 1,

                "Kidney": 0,
                "Liver": 1,
                "Heart": 0,
                "Lung": 2,
                "Pancreas": 0
            }
        }

        # Organ requests made to other hospitals
        self.organ_requests = []


    # ============================================================
    # FIND HOSPITAL WITH EQUIPMENT
    # ============================================================

    def find_hospital(self, patient):

        equipment = patient.required_resource

        for hospital in self.hospitals:

            if equipment in self.hospitals[hospital]:

                if self.hospitals[hospital][equipment] > 0:

                    return hospital

        return None


    # ============================================================
    # REQUEST EQUIPMENT
    # ============================================================

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
    # FIND HOSPITAL WITH ICU BED
    # ============================================================

    def find_icu_hospital(self):

        for hospital in self.hospitals:

            if self.hospitals[hospital]["ICU Bed"] > 0:

                return hospital

        return None


    # ============================================================
    # REQUEST ICU TRANSFER
    # ============================================================

    def request_icu_transfer(self, patient):

        hospital = self.find_icu_hospital()

        if hospital is not None:

            print(
                "ICU bed available at",
                hospital
            )

            print(
                "ICU transfer can be coordinated."
            )

            patient.status = "transferred"

            return hospital

        print(
            "No nearby hospital has an available ICU bed."
        )

        patient.status = "waiting"

        return None


    # ============================================================
    # FIND HOSPITAL WITH ORGAN
    # ============================================================

    def find_organ_hospital(self, organ):

        for hospital in self.hospitals:

            if organ in self.hospitals[hospital]:

                if self.hospitals[hospital][organ] > 0:

                    return hospital

        return None


    # ============================================================
    # REQUEST ORGAN FROM ANOTHER HOSPITAL
    # ============================================================

    def request_organ(self, organ):

        hospital = self.find_organ_hospital(organ)

        if hospital is None:

            print(
                "Organ is not available at nearby hospitals."
            )

            return None


        # Record the request
        request = {
            "organ": organ,
            "hospital": hospital,
            "status": "requested"
        }

        self.organ_requests.append(request)

        print(
            "\n",
            organ,
            "available at",
            hospital
        )

        print(
            "Organ request sent to",
            hospital
        )

        # IMPORTANT:
        # Hospital inventory is NOT decreased here.
        # It will only decrease when the request is fulfilled.

        return hospital


    # ============================================================
    # FULFILL ORGAN REQUEST
    # ============================================================

    def fulfill_organ_request(self, organ, hospital):

        if hospital not in self.hospitals:
            return False

        if organ not in self.hospitals[hospital]:
            return False

        if self.hospitals[hospital][organ] <= 0:
            return False

        # Decrease the other hospital's inventory
        self.hospitals[hospital][organ] -= 1

        # Mark matching request as fulfilled
        for request in self.organ_requests:

            if (
                request["organ"] == organ
                and request["hospital"] == hospital
                and request["status"] == "requested"
            ):

                request["status"] = "fulfilled"

                return True

        return False


    # ============================================================
    # SHOW ORGAN REQUESTS
    # ============================================================

    def show_organ_requests(self):

        print("\n========== ORGAN REQUESTS ==========")

        if len(self.organ_requests) == 0:

            print("No organ requests.")

            return

        for request in self.organ_requests:

            print(
                "Organ:", request["organ"],
                "| Hospital:", request["hospital"],
                "| Status:", request["status"]
            )


# ============================================================
# SURGERY EQUIPMENT HANDLER
# ============================================================

class SurgeryEquipmentHandler:

    def __init__(self):

        self.equipment_manager = SurgicalEquipmentManager()

        self.hospital_network = HospitalNetwork()


    # ============================================================
    # HANDLE SURGICAL PATIENT
    # ============================================================

    def handle_patient(self, patient):

        print("\n--------------------------------")

        print(
            "Patient:",
            patient.patient_id
        )

        print(
            "Name:",
            patient.name
        )

        print(
            "Required resource:",
            patient.required_resource
        )


        # Try local equipment
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


# ============================================================
# WEBSITE-FRIENDLY FUNCTIONS
# ============================================================
#
# These are the functions your website/backend can call when
# the user presses a button or submits a form.
#
# Your teammate's Patient class does NOT need to be changed.
# ============================================================


class HospitalSystem:

    def __init__(self):

        # Change these numbers to whatever your project uses
        self.resource_manager = ResourceManager(
            beds=50,
            icu_beds=10,
            doctors=20,
            nurses=40,
            ventilators=4,
            operating_rooms=3,
            ambulances=5
        )

        self.hospital_network = HospitalNetwork()

        self.surgery_manager = SurgicalEquipmentManager()


    # ============================================================
    # WEBSITE: REQUEST BLOOD
    # ============================================================

    def request_blood(self, patient, blood_group, units):

        return self.resource_manager.allocate_blood(
            patient,
            blood_group,
            units
        )


    # ============================================================
    # WEBSITE: REQUEST ORGAN
    # ============================================================

    def request_organ(self, patient, organ):

        return self.resource_manager.request_organ(
            patient,
            organ,
            self.hospital_network
        )


    # ============================================================
    # WEBSITE: FULFILL ORGAN REQUEST
    # ============================================================

    def fulfill_organ_request(self, organ, hospital):

        return self.hospital_network.fulfill_organ_request(
            organ,
            hospital
        )


    # ============================================================
    # WEBSITE: CHECK ICU
    # ============================================================

    def check_icu(self, patient):

        return self.resource_manager.check_icu_transfer(
            patient,
            self.hospital_network
        )


    # ============================================================
    # WEBSITE: ALLOCATE NORMAL RESOURCE
    # ============================================================

    def allocate_resource(self, patient):

        return self.resource_manager.allocate_resources(
            patient
        )


    # ============================================================
    # WEBSITE: RELEASE NORMAL RESOURCE
    # ============================================================

    def release_resource(self, patient):

        return self.resource_manager.release_resources(
            patient
        )


    # ============================================================
    # WEBSITE: ALLOCATE SURGICAL EQUIPMENT
    # ============================================================

    def allocate_equipment(self, patient):

        if self.surgery_manager.allocate_equipment(patient):

            return True

        hospital = self.hospital_network.request_equipment(
            patient
        )

        if hospital is not None:

            patient.status = "transferred"

        else:

            patient.status = "waiting"

        return False


    # ============================================================
    # WEBSITE: SHOW DASHBOARD
    # ============================================================

    def show_dashboard(self):

        self.resource_manager.show_resources()

        self.resource_manager.show_blood_supply()

        self.resource_manager.show_organ_supply()

        self.surgery_manager.show_equipment()

        self.hospital_network.show_organ_requests()
