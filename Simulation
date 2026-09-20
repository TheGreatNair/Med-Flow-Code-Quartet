Simulation code

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional
import heapq
import random
import math


class Urgency(IntEnum):
    CRITICAL = 1
    URGENT = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Patient:
    patient_id: str
    arrival_time: int
    urgency: Urgency
    arrival_mode: str
    needs_icu: bool
    required_staff: str
    treatment_time: int

    status: str = "waiting"
    start_time: Optional[int] = None
    discharge_time: Optional[int] = None

    @property
    def waiting_time(self) -> Optional[int]:
        if self.start_time is None:
            return None
        return self.start_time - self.arrival_time


@dataclass(order=True)
class QueueEntry:
    priority: int
    arrival_order: int
    patient: Patient = field(compare=False)


class PatientPriorityQueue:
    def __init__(self, waiting_bonus_interval=30):
        self.queue = []
        self.arrival_order = 0
        self.waiting_bonus_interval = waiting_bonus_interval

    def calculate_priority(self, patient, current_time):
        waiting_time = max(0, current_time - patient.arrival_time)

        # Waiting-time bonus prevents starvation.
        waiting_bonus = waiting_time // self.waiting_bonus_interval

        # The cap prevents waiting time from completely overriding
        # the most urgent category.
        waiting_bonus = min(waiting_bonus, 2)

        return max(1, patient.urgency.value - waiting_bonus)

    def add(self, patient, current_time):
        priority = self.calculate_priority(patient, current_time)

        entry = QueueEntry(
            priority=priority,
            arrival_order=self.arrival_order,
            patient=patient
        )

        heapq.heappush(self.queue, entry)
        self.arrival_order += 1

    def refresh(self, current_time):
        refreshed = []

        for entry in self.queue:
            new_priority = self.calculate_priority(
                entry.patient,
                current_time
            )

            refreshed.append(
                QueueEntry(
                    priority=new_priority,
                    arrival_order=entry.arrival_order,
                    patient=entry.patient
                )
            )

        heapq.heapify(refreshed)
        self.queue = refreshed

    def pop_best_available(self, current_time, can_treat):
        """
        Select the highest-priority patient whose required
        resources are currently available.
        """
        self.refresh(current_time)

        ordered_entries = sorted(self.queue)

        for entry in ordered_entries:
            patient = entry.patient

            if can_treat(patient):
                self.queue.remove(entry)
                heapq.heapify(self.queue)
                return patient

        return None

    def __len__(self):
        return len(self.queue)


@dataclass
class HospitalResources:
    total_staff: dict
    available_staff: dict
    total_icu_beds: int
    available_icu_beds: int

    @classmethod
    def create(cls, doctors, nurses, icu_beds):
        staff = {
            "doctor": doctors,
            "nurse": nurses
        }

        return cls(
            total_staff=staff.copy(),
            available_staff=staff.copy(),
            total_icu_beds=icu_beds,
            available_icu_beds=icu_beds
        )

    def can_treat(self, patient):
        staff_available = (
            self.available_staff.get(patient.required_staff, 0) > 0
        )

        icu_available = (
            not patient.needs_icu
            or self.available_icu_beds > 0
        )

        return staff_available and icu_available

    def allocate(self, patient):
        if not self.can_treat(patient):
            return False

        self.available_staff[patient.required_staff] -= 1

        if patient.needs_icu:
            self.available_icu_beds -= 1

        return True

    def release(self, patient):
        self.available_staff[patient.required_staff] += 1

        if patient.needs_icu:
            self.available_icu_beds += 1


class HospitalSimulation:
    def __init__(
        self,
        simulation_minutes=24 * 60,
        seed=42,
        doctors=5,
        nurses=8,
        icu_beds=4,
        waiting_bonus_interval=30
    ):
        random.seed(seed)

        self.simulation_minutes = simulation_minutes
        self.current_time = 0

        self.patient_counter = 1
        self.event_counter = 0

        self.waiting_queue = PatientPriorityQueue(
            waiting_bonus_interval=waiting_bonus_interval
        )

        self.resources = HospitalResources.create(
            doctors=doctors,
            nurses=nurses,
            icu_beds=icu_beds
        )

        self.events = []

        self.all_patients = []
        self.completed_patients = []
        self.rejected_patients = []

        self.metrics = {
            "ambulance_arrivals": 0,
            "walk_in_arrivals": 0,
            "surge_arrivals": 0,
            "icu_blocked_attempts": 0,
            "staff_blocked_attempts": 0
        }

    # ---------------------------------------------------------
    # Event handling
    # ---------------------------------------------------------

    def schedule_event(self, event_time, event_type, data=None):
        heapq.heappush(
            self.events,
            (
                event_time,
                self.event_counter,
                event_type,
                data
            )
        )

        self.event_counter += 1

    # ---------------------------------------------------------
    # Arrival models
    # ---------------------------------------------------------

    def is_surge_period(self, time):
        """
        Simulated emergency surge windows.

        Example:
        - 09:00 to 11:00
        - 18:00 to 21:00
        """
        hour = (time // 60) % 24

        morning_surge = 9 <= hour < 11
        evening_surge = 18 <= hour < 21

        return morning_surge or evening_surge

    def walk_in_arrival_rate(self, time):
        """
        Returns the expected walk-in arrivals per hour.
        """
        hour = (time // 60) % 24

        if self.is_surge_period(time):
            return 18

        if 0 <= hour < 6:
            return 4

        if 6 <= hour < 12:
            return 10

        if 12 <= hour < 18:
            return 12

        return 14

    def ambulance_arrival_rate(self, time):
        """
        Returns the expected ambulance arrivals per hour.

        Ambulance arrivals are increased during emergency surges.
        """
        hour = (time // 60) % 24

        if self.is_surge_period(time):
            return 6

        if 0 <= hour < 6:
            return 1

        if 6 <= hour < 12:
            return 2

        if 12 <= hour < 18:
            return 3

        return 4

    def poisson_count(self, rate_per_hour):
        """
        Generate an approximate Poisson-distributed count
        using Knuth's algorithm.
        """
        expected_arrivals = rate_per_hour / 60
        limit = math.exp(-expected_arrivals)

        probability = 1.0
        count = 0

        while probability > limit:
            count += 1
            probability *= random.random()

        return count - 1

    def generate_arrivals(self, time):
        """
        Generate walk-in and ambulance arrivals for one minute.
        """
        walk_in_count = self.poisson_count(
            self.walk_in_arrival_rate(time)
        )

        ambulance_count = self.poisson_count(
            self.ambulance_arrival_rate(time)
        )

        for _ in range(walk_in_count):
            self.create_patient(
                arrival_time=time,
                arrival_mode="walk-in"
            )

        for _ in range(ambulance_count):
            self.create_patient(
                arrival_time=time,
                arrival_mode="ambulance"
            )

    # ---------------------------------------------------------
    # Patient generation
    # ---------------------------------------------------------

    def choose_urgency(self, arrival_mode):
        """
        Ambulance arrivals have a higher probability of being urgent.
        """
        if arrival_mode == "ambulance":
            return random.choices(
                population=[
                    Urgency.CRITICAL,
                    Urgency.URGENT,
                    Urgency.NORMAL,
                    Urgency.LOW
                ],
                weights=[0.30, 0.45, 0.20, 0.05]
            )[0]

        return random.choices(
            population=[
                Urgency.CRITICAL,
                Urgency.URGENT,
                Urgency.NORMAL,
                Urgency.LOW
            ],
            weights=[0.08, 0.27, 0.45, 0.20]
        )[0]

    def create_patient(self, arrival_time, arrival_mode):
        urgency = self.choose_urgency(arrival_mode)

        needs_icu = (
            urgency == Urgency.CRITICAL
            or random.random() < 0.08
        )

        required_staff = (
            "doctor"
            if urgency in [Urgency.CRITICAL, Urgency.URGENT]
            else "nurse"
        )

        treatment_time = random.randint(20, 60)

        patient = Patient(
            patient_id=f"P{self.patient_counter:04d}",
            arrival_time=arrival_time,
            urgency=urgency,
            arrival_mode=arrival_mode,
            needs_icu=needs_icu,
            required_staff=required_staff,
            treatment_time=treatment_time
        )

        self.patient_counter += 1
        self.all_patients.append(patient)

        if arrival_mode == "ambulance":
            self.metrics["ambulance_arrivals"] += 1
        else:
            self.metrics["walk_in_arrivals"] += 1

        if self.is_surge_period(arrival_time):
            self.metrics["surge_arrivals"] += 1

        self.waiting_queue.add(patient, arrival_time)

    # ---------------------------------------------------------
    # Staff shortages
    # ---------------------------------------------------------

    def apply_staff_shortage(self):
        """
        Simulate a shortage during the evening surge.

        Staff availability is reduced but never becomes negative.
        """
        self.resources.available_staff["doctor"] = max(
            1,
            self.resources.available_staff["doctor"] - 2
        )

        self.resources.available_staff["nurse"] = max(
            1,
            self.resources.available_staff["nurse"] - 3
        )

    def restore_staff(self):
        """
        Restore staff to normal capacity.
        """
        self.resources.available_staff = (
            self.resources.total_staff.copy()
        )

    # ---------------------------------------------------------
    # Treatment and discharge
    # ---------------------------------------------------------

    def start_treatment(self):
        """
        Start as many patients as current resources allow.
        """
        while True:
            patient = self.waiting_queue.pop_best_available(
                current_time=self.current_time,
                can_treat=self.resources.can_treat
            )

            if patient is None:
                break

            if not self.resources.allocate(patient):
                break

            patient.status = "in treatment"
            patient.start_time = self.current_time

            finish_time = (
                self.current_time + patient.treatment_time
            )

            self.schedule_event(
                event_time=finish_time,
                event_type="discharge",
                data=patient
            )

    def process_discharge(self, patient):
        patient.status = "discharged"
        patient.discharge_time = self.current_time

        self.resources.release(patient)
        self.completed_patients.append(patient)

    # ---------------------------------------------------------
    # Simulation loop
    # ---------------------------------------------------------

    def run(self):
        for time in range(self.simulation_minutes):
            self.current_time = time

            # Generate incoming patients.
            self.generate_arrivals(time)

            # Staff shortage begins at 18:00.
            if time == 18 * 60:
                self.apply_staff_shortage()

            # Staff returns at 21:00.
            if time == 21 * 60:
                self.restore_staff()

            # Process all discharge events scheduled for this minute.
            while self.events and self.events[0][0] <= time:
                _, _, event_type, data = heapq.heappop(self.events)

                if event_type == "discharge":
                    self.process_discharge(data)

            # Try to start treatment after arrivals and discharges.
            self.start_treatment()

        # Process any remaining treatment after the main period.
        self.current_time = self.simulation_minutes

        while self.events:
            event_time, _, event_type, data = heapq.heappop(
                self.events
            )

            self.current_time = event_time

            if event_type == "discharge":
                self.process_discharge(data)

        return self.report()

    # ---------------------------------------------------------
    # Reporting
    # ---------------------------------------------------------

    def report(self):
        waiting_patients = self.waiting_queue.queue

        completed_waiting_times = [
            patient.waiting_time
            for patient in self.completed_patients
            if patient.waiting_time is not None
        ]

        average_wait = (
            sum(completed_waiting_times)
            / len(completed_waiting_times)
            if completed_waiting_times
            else 0
        )

        max_wait = (
            max(completed_waiting_times)
            if completed_waiting_times
            else 0
        )

        return {
            "total_patients": len(self.all_patients),
            "completed_patients": len(self.completed_patients),
            "still_waiting": len(waiting_patients),
            "ambulance_arrivals": self.metrics["ambulance_arrivals"],
            "walk_in_arrivals": self.metrics["walk_in_arrivals"],
            "surge_arrivals": self.metrics["surge_arrivals"],
            "average_wait_minutes": round(average_wait, 2),
            "maximum_wait_minutes": max_wait,
            "available_icu_beds": self.resources.available_icu_beds,
            "total_icu_beds": self.resources.total_icu_beds
        }
Failure state

self.resource_failures = {
    "doctor": 0,
    "nurse": 0,
    "icu_bed": 0
}

self.failure_log = []

Constructor section :

class HospitalSimulation:
    def __init__(
        self,
        simulation_minutes=24 * 60,
        seed=42,
        doctors=5,
        nurses=8,
        icu_beds=4,
        waiting_bonus_interval=30
    ):
        random.seed(seed)

        self.simulation_minutes = simulation_minutes
        self.current_time = 0

        self.patient_counter = 1
        self.event_counter = 0

        self.waiting_queue = PatientPriorityQueue(
            waiting_bonus_interval=waiting_bonus_interval
        )

        self.resources = HospitalResources.create(
            doctors=doctors,
            nurses=nurses,
            icu_beds=icu_beds
        )

        self.events = []

        self.all_patients = []
        self.completed_patients = []
        self.rejected_patients = []

        self.resource_failures = {
            "doctor": 0,
            "nurse": 0,
            "icu_bed": 0
        }

        self.failure_log = []

        self.metrics = {
            "ambulance_arrivals": 0,
            "walk_in_arrivals": 0,
            "surge_arrivals": 0,
            "icu_blocked_attempts": 0,
            "staff_blocked_attempts": 0,
            "resource_failure_events": 0,
            "failure_downtime_minutes": 0
        }

Updating resource availability checks:

def can_treat(self, patient, failed_resources=None):
    if failed_resources is None:
        failed_resources = {}

    required_staff = patient.required_staff

    staff_available = (
        self.available_staff.get(required_staff, 0) > 0
        and failed_resources.get(required_staff, 0) == 0
    )

    icu_available = (
        not patient.needs_icu
        and failed_resources.get("icu_bed", 0) == 0
    ) or (
        patient.needs_icu
        and self.available_icu_beds > 0
        and failed_resources.get("icu_bed", 0) == 0
    )

    # Non-ICU patients do not require an ICU bed.
    if not patient.needs_icu:
        icu_available = True

    return staff_available and icu_available
@dataclass
class HospitalResources:
    total_staff: dict
    available_staff: dict
    total_icu_beds: int
    available_icu_beds: int

    @classmethod
    def create(cls, doctors, nurses, icu_beds):
        staff = {
            "doctor": doctors,
            "nurse": nurses
        }

        return cls(
            total_staff=staff.copy(),
            available_staff=staff.copy(),
            total_icu_beds=icu_beds,
            available_icu_beds=icu_beds
        )

    def can_treat(self, patient, failed_resources=None):
        if failed_resources is None:
            failed_resources = {}

        required_staff = patient.required_staff

        if failed_resources.get(required_staff, 0) > 0:
            return False

        if self.available_staff.get(required_staff, 0) <= 0:
            return False

        if patient.needs_icu:
            if failed_resources.get("icu_bed", 0) > 0:
                return False

            if self.available_icu_beds <= 0:
                return False

        return True

    def allocate(self, patient):
        if not self.can_treat(patient):
            return False

        self.available_staff[patient.required_staff] -= 1

        if patient.needs_icu:
            self.available_icu_beds -= 1

        return True

    def release(self, patient):
        self.available_staff[patient.required_staff] += 1

        if patient.needs_icu:
            self.available_icu_beds += 1

Unexpected failure generation :

def schedule_random_failure(self):
    """
    Schedule one unexpected resource failure.

    A failure can affect doctors, nurses, or ICU beds.
    """
    failure_time = random.randint(
        60,
        self.simulation_minutes - 120
    )

    resource_type = random.choices(
        population=["doctor", "nurse", "icu_bed"],
        weights=[0.40, 0.35, 0.25]
    )[0]

    if resource_type == "doctor":
        failed_units = 1
    elif resource_type == "nurse":
        failed_units = 2
    else:
        failed_units = 1

    duration = random.randint(30, 120)

    self.schedule_event(
        event_time=failure_time,
        event_type="resource_failure_start",
        data={
            "resource_type": resource_type,
            "failed_units": failed_units,
            "duration": duration
        }
    )

    self.schedule_event(
        event_time=failure_time + duration,
        event_type="resource_failure_end",
        data={
            "resource_type": resource_type,
            "failed_units": failed_units,
            "duration": duration
        }
    )

Failure processing:

def start_resource_failure(self, failure_data):
    resource_type = failure_data["resource_type"]
    failed_units = failure_data["failed_units"]
    duration = failure_data["duration"]

    self.resource_failures[resource_type] += failed_units

    self.metrics["resource_failure_events"] += 1
    self.metrics["failure_downtime_minutes"] += duration

    self.failure_log.append({
        "time": self.current_time,
        "event": "failure_started",
        "resource": resource_type,
        "units": failed_units,
        "duration": duration
    })

    print(
        f"[{self.format_time(self.current_time)}] "
        f"FAILURE: {failed_units} {resource_type} resource(s) "
        f"unavailable for {duration} minutes"
    )


def end_resource_failure(self, failure_data):
    resource_type = failure_data["resource_type"]
    failed_units = failure_data["failed_units"]

    self.resource_failures[resource_type] = max(
        0,
        self.resource_failures[resource_type] - failed_units
    )

    self.failure_log.append({
        "time": self.current_time,
        "event": "failure_recovered",
        "resource": resource_type,
        "units": failed_units
    })

    print(
        f"[{self.format_time(self.current_time)}] "
        f"RECOVERY: {resource_type} resource(s) restored"
    )
def format_time(self, minutes):
    hour = (minutes // 60) % 24
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"

Updating treatment allocation:

def start_treatment(self):
    """
    Start treatment for the highest-priority patients whose
    required resources are available and operational.
    """
    while True:
        patient = self.waiting_queue.pop_best_available(
            current_time=self.current_time,
            can_treat=lambda p: self.resources.can_treat(
                p,
                self.resource_failures
            )
        )

        if patient is None:
            break

        if not self.resources.can_treat(
            patient,
            self.resource_failures
        ):
            break

        if not self.resources.allocate(patient):
            break

        patient.status = "in treatment"
        patient.start_time = self.current_time

        finish_time = (
            self.current_time + patient.treatment_time
        )

        self.schedule_event(
            event_time=finish_time,
            event_type="discharge",
            data=patient
        )

Event handling:

while self.events and self.events[0][0] <= time:
    _, _, event_type, data = heapq.heappop(self.events)

    if event_type == "discharge":
        self.process_discharge(data)

while self.events and self.events[0][0] <= time:
    _, _, event_type, data = heapq.heappop(self.events)

    if event_type == "discharge":
        self.process_discharge(data)

    elif event_type == "resource_failure_start":
        self.start_resource_failure(data)

    elif event_type == "resource_failure_end":
        self.end_resource_failure(data)

Scheduling failure :

def run(self):
    # Schedule unexpected failures before the simulation starts.
    self.schedule_random_failure()
    self.schedule_random_failure()

    for time in range(self.simulation_minutes):
        self.current_time = time

        self.generate_arrivals(time)

        if time == 18 * 60:
            self.apply_staff_shortage()

        if time == 21 * 60:
            self.restore_staff()

        while self.events and self.events[0][0] <= time:
            _, _, event_type, data = heapq.heappop(self.events)

            if event_type == "discharge":
                self.process_discharge(data)

            elif event_type == "resource_failure_start":
                self.start_resource_failure(data)

            elif event_type == "resource_failure_end":
                self.end_resource_failure(data)

        self.start_treatment()

    self.current_time = self.simulation_minutes

    while self.events:
        event_time, _, event_type, data = heapq.heappop(self.events)

        self.current_time = event_time

        if event_type == "discharge":
            self.process_discharge(data)

        elif event_type == "resource_failure_start":
            self.start_resource_failure(data)

        elif event_type == "resource_failure_end":
            self.end_resource_failure(data)

    return self.report()

Include failures in report:

def report(self):
    waiting_patients = self.waiting_queue.queue

    completed_waiting_times = [
        patient.waiting_time
        for patient in self.completed_patients
        if patient.waiting_time is not None
    ]

    average_wait = (
        sum(completed_waiting_times)
        / len(completed_waiting_times)
        if completed_waiting_times
        else 0
    )

    max_wait = (
        max(completed_waiting_times)
        if completed_waiting_times
        else 0
    )

    return {
        "total_patients": len(self.all_patients),
        "completed_patients": len(self.completed_patients),
        "still_waiting": len(waiting_patients),
        "ambulance_arrivals": self.metrics["ambulance_arrivals"],
        "walk_in_arrivals": self.metrics["walk_in_arrivals"],
        "surge_arrivals": self.metrics["surge_arrivals"],
        "resource_failure_events": (
            self.metrics["resource_failure_events"]
        ),
        "failure_downtime_minutes": (
            self.metrics["failure_downtime_minutes"]
        ),
        "failure_log": self.failure_log,
        "average_wait_minutes": round(average_wait, 2),
        "maximum_wait_minutes": max_wait,
        "available_icu_beds": self.resources.available_icu_beds,
        "total_icu_beds": self.resources.total_icu_beds
    }

Running updated simulation :

simulation = HospitalSimulation(
    simulation_minutes=24 * 60,
    seed=7,
    doctors=5,
    nurses=8,
    icu_beds=4,
    waiting_bonus_interval=30
)

results = simulation.run()

print("
Simulation report")
print("=================")

for key, value in results.items():
    if key != "failure_log":
        print(f"{key}: {value}")

print("
Failure events")
print("==============")

for failure in results["failure_log"]:
    print(failure)
