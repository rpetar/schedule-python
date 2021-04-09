DEFAULT_DAY_OFF = 4

PENALTY_NUM_DAYS_LOWER = 4
PENALTY_NUM_DAYS_GREATER = 8
PENALTY_INVALID_CONSECUTIVE_DAYS = 50
PENALTY_INVALID_DAY_OFF = 40
SCHEDULE_TEST_PARAMS = [
    # Tymeshift test params
    {'num_days': 28, 'max_working': 5, 'min_working': 2, 'max_off': 3, 'min_off': 1, 'days_off': [5, 6]},
    # Fails because day off is Tuesday, and min_working days is 2 (the week starts with Monday)
    {'num_days': 28, 'max_working': 5, 'min_working': 2, 'max_off': 3, 'min_off': 1, 'days_off': [2, 5]},
    {'num_days': 112, 'max_working': 5, 'min_working': 2, 'max_off': 3, 'min_off': 1, 'days_off': [5, 6]},
    {'num_days': 112, 'max_working': 4, 'min_working': 1, 'max_off': 4, 'min_off': 2, 'days_off': []},
    {'num_days': 7, 'max_working': 5, 'min_working': 2, 'max_off': 3, 'min_off': 1, 'days_off': [5, 6]},
    # Additional test params
    {'num_days': 112, 'max_working': 4, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': []},
    {'num_days': 112, 'max_working': 4, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': [3]},
    {'num_days': 112, 'max_working': 4, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': [3, 4]},
    {'num_days': 112, 'max_working': 4, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': [3, 6]},
    {'num_days': 112, 'max_working': 4, 'min_working': 1, 'max_off': 2, 'min_off': 2, 'days_off': [3, 6]},
    {'num_days': 21, 'max_working': 4, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': []},
    {'num_days': 21, 'max_working': 4, 'min_working': 1, 'max_off': 2, 'min_off': 2, 'days_off': []},
    {'num_days': 7, 'max_working': 5, 'min_working': 2, 'max_off': 3, 'min_off': 1, 'days_off': []},
    {'num_days': 28, 'max_working': 5, 'min_working': 2, 'max_off': 3, 'min_off': 1, 'days_off': [3, 6]},  # mine
    {'num_days': 7, 'max_working': 5, 'min_working': 2, 'max_off': 3, 'min_off': 2, 'days_off': []},
    {'num_days': 7, 'max_working': 3, 'min_working': 2, 'max_off': 3, 'min_off': 1, 'days_off': []},
    {'num_days': 7, 'max_working': 3, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': []},
    {'num_days': 7, 'max_working': 3, 'min_working': 2, 'max_off': 2, 'min_off': 2, 'days_off': []},
    {'num_days': 112, 'max_working': 3, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': []},
    {'num_days': 112, 'max_working': 4, 'min_working': 2, 'max_off': 2, 'min_off': 1, 'days_off': []},
]

DAY_NAME = {
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday',
    0: 'Sunday'
}
