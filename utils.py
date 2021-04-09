def cons_days_number(schedule_days, day_index, day_type=None):
    """
    Get total number of consecutive days of sequence :param day_index belongs to.
    :param schedule_days: the sequence of days
    :param day_index: the index of the day
    :param day_type: the day type of the day
    :return:
    """
    # Set the day type to the type of the current day
    if day_type is None:
        day_type = schedule_days[day_index].type

    assert schedule_days[day_index].type == day_type, f"The day with index {day_index} is not " \
                                                      f"{'working day' if day_type else 'day off'}."
    count = 1
    stop_left = False
    stop_right = False

    # Check for day on both side of the current day
    for i in range(1, len(schedule_days)):
        if day_index - i >= 0 and not stop_left:
            if schedule_days[day_index - i].type == day_type:
                count += 1
            else:
                stop_left = True
        if day_index + i < len(schedule_days) and not stop_right:
            if schedule_days[day_index + i].type == day_type:
                count += 1
            else:
                stop_right = True
    return count


def get_next_available_day(schedule, day_index, right=True, day_type=None):
    """
    Get the index of the first next day that is not :param day_type
    :param schedule: list of days
    :param day_index: index of the current day
    :param day_type: type of the current day, the function will return the index of the next day with the different type
    :param right: get the next day from the right side if True, else from left side
    :return:
    """
    # Set the day type to the type of the current day
    if day_type is None:
        day_type = schedule[day_index].type
    assert schedule[day_index].type == day_type, f"The day with index {day_index} is " \
                                                 f"{'working day' if day_type else 'day off'}."
    # Use sum function if going right, else subtract
    fn = int.__radd__ if right else int.__rsub__

    for i in range(1, len(schedule)):
        next_index = fn(i, day_index)
        # If next index is out of range,return the previous one
        if next_index < 0 or next_index >= len(schedule):
            return fn(i - 1, day_index)
        if schedule[next_index].type != day_type:
            return next_index
    return next_index


def find_best_schedule(schedules):
    """
    Find the best schedule.
    :param schedules: the list of schedules
    :return:
    """
    best_schedule = schedules[0]

    for schedule in schedules:
        if schedule.score.penalty < best_schedule.score.penalty or \
                (schedule.score.penalty == best_schedule.score.penalty
                 and schedule.score.total < best_schedule.score.total):
            best_schedule = schedule
    return best_schedule
