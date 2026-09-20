# ============================================================
# AMBULANCE ARRIVAL PATTERN MODEL
# ============================================================

import random


class AmbulanceArrivalModel:

    def __init__(self):

        # Expected ambulance arrivals for each hour.
        # Higher values = busier periods.

        self.arrival_pattern = {

            0: 1, # 12 AM
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1,

            6: 2,
            7: 2,
            8: 3,
            9: 3,
            10: 3,
            11: 4,

            12: 4,
            13: 4,
            14: 3,
            15: 3,
            16: 3,
            17: 4,

            18: 5,
            19: 5,
            20: 4,
            21: 4,
            22: 3,
            23: 2
        }


    # ========================================================
    # GET EXPECTED ARRIVALS
    # ========================================================

    def get_expected_arrivals(self, hour):

        if hour in self.arrival_pattern:
            return self.arrival_pattern[hour]

        return 0


    # ========================================================
    # GENERATE ACTUAL ARRIVALS
    # ========================================================

    def generate_arrivals(self, hour):

        expected = self.get_expected_arrivals(hour)

        # Small random variation around expected value
        minimum = max(0, expected - 1)
        maximum = expected + 1

        arrivals = random.randint(
            minimum,
            maximum
        )

        return arrivals


    # ========================================================
    # GENERATE 24-HOUR SIMULATION
    # ========================================================

    def simulate_day(self):

        results = {}

        for hour in range(24):

            arrivals = self.generate_arrivals(hour)

            results[hour] = arrivals

        return results


    # ========================================================
    # DISPLAY ARRIVAL PATTERN
    # ========================================================

    def show_pattern(self):

        print("\n========== AMBULANCE ARRIVAL PATTERN ==========")

        for hour in range(24):

            expected = self.get_expected_arrivals(hour)

            print(
                str(hour).zfill(2) + ":00",
                "| Expected arrivals:",
                expected
            )


    # ========================================================
    # DISPLAY SIMULATED DAY
    # ========================================================

    def show_simulated_day(self):

        results = self.simulate_day()

        print("\n========== SIMULATED AMBULANCE ARRIVALS ==========")

        total = 0

        for hour in range(24):

            arrivals = results[hour]

            print(
                str(hour).zfill(2) + ":00",
                "| Ambulances:",
                arrivals
            )

            total += arrivals

        print("\nTotal ambulance arrivals:", total)


# ============================================================
# TEST THE MODEL
# ============================================================

