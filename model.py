import copy
from abc import abstractmethod

from constants import DEFAULT_DAY_OFF, DAY_NAME, PENALTY_NUM_DAYS_GREATER, \
    PENALTY_NUM_DAYS_LOWER, PENALTY_INVALID_CONSECUTIVE_DAYS, PENALTY_INVALID_DAY_OFF
from utils import cons_days_number, get_next_available_day, find_best_schedule


class DayType:
    """
    Class which represents type of the day.
    """
    WORKING_DAY = 1
    DAY_OFF = 0


class ScheduleScore:
    """
    Schedule Score class.
    """

    def __init__(self, penalty: int, bonus: int):
        """
        Create a Schedule Score.
        :param penalty: schedule penalty
        :param bonus: total number of working days -> as greater the number of working days, as greater the bonus
        """
        self.penalty = penalty
        self.bonus = bonus
        self.total = penalty - bonus

    def __str__(self):
        return f"Penalty: {self.penalty}\nBonus: {self.bonus}\nTotal score: {self.total}"


class Block:
    def __init__(self, cons_working_days, cons_days_off):
        """
        Create a new Block.
        :param cons_working_days: number of consecutive working days
        :param cons_days_off: number of consecutive days off
        """
        self.working_days = cons_working_days
        self.days_off = cons_days_off

    def __eq__(self, other):
        return self.working_days == other.working_days and self.days_off == other.days_off


class Day:
    def __init__(self, day_type, day_index, mutable=True):
        """
        Create a new Day.
        :param day_type: type of the day
        :param day_index: index of the day
        :param mutable: can day be changed
        """
        self._type = day_type
        self._mutable = mutable
        self._index = day_index
        self.day_name = DAY_NAME[(day_index + 1) % 7]

    def __eq__(self, other):
        return self.type == other.type and self.mutable == other.mutable and self.index == other.index

    def is_working(self):
        """
        Check if day is working day.
        :return:
        """
        return self.type == DayType.WORKING_DAY

    def is_day_off(self):
        """
        Check if day is day off.
        :return:
        """
        return self.type == DayType.DAY_OFF

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        # If value is not changing or Day is mutable
        if self.mutable or self._type == value:
            self._type = value
        else:
            raise TypeError('Cannot change type of immutable Day.')

    @property
    def mutable(self):
        return self._mutable

    @mutable.setter
    def mutable(self, value):
        raise TypeError('Day is mutable. Cannot change to immutable.')

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        raise TypeError('Cannot change index of the day.')


class Schedule:
    """
    Schedule class.
    """

    def __init__(self, schedule_params, days=None):
        """
        Create a new Schedule.
        :param schedule_params: params list in the following order:
                                total number of days, max consecutive working days, min consecutive working days,
                                max consecutive days off, min consecutive days off, predefined days off indices
        :param days: the schedule (list of 1s and 0s representing working days/days off
        """
        self.num_days, self.max_working, self.min_working, self.max_off, self.min_off, self.days_off = schedule_params
        self.days = []
        self.blocks = []
        self.score = None
        if days:
            assert len(days) == self.num_days, \
                f"'days' contains {'more' if len(days) > self.num_days else 'less'} days than 'num_days'"
            self.days = days
        else:
            self.generate_initial_schedule()
        self.build_blocks()
        self.evaluate()

    def __str__(self):
        return ", ".join([str(day.type) for day in self.days])

    def __eq__(self, other):
        return self.blocks == other.blocks and self.max_working == other.max_working and \
               self.min_working == other.min_working and self.max_off == other.max_off and \
               self.min_off == other.min_off and self.days_off == other.days_off

    def working_days_num(self):
        """
        Calculate the number of working days.
        :return:
        """
        return sum(day.type for day in self.days)

    def update_schedule(self):
        """
        Update blocks and score when day is changed.
        :return:
        """
        self.build_blocks()
        self.evaluate()

    def change_day_type(self, day_index, new_day_type):
        """
        Change the type of the day in the schedule.
        :param day_index: index of the day
        :param new_day_type: the new type
        :return:
        """
        self.days[day_index].type = new_day_type
        self.update_schedule()

    def generate_initial_schedule(self):
        """
        Generate initial schedule by setting predefined days off to 0, and all other days to 1.
        :return:
        """
        # Add Saturday as default day off, if there isn't predefined day off
        if self.min_off > 0 and len(self.days_off) == 0:
            self.days_off.append(DEFAULT_DAY_OFF)

        # Set predefined days off
        for i in range(self.num_days):
            if i != 0 and (i % 7 + 1) in self.days_off:
                self.days.append(Day(DayType.DAY_OFF, i, False))
            else:
                self.days.append(Day(DayType.WORKING_DAY, i))

    def build_blocks(self):
        """
        Build blocks for the schedule.
        :return:
        """
        # Reset current blocks
        self.blocks = []
        i = 0
        while i < len(self.days):
            # Check if first day
            if i == 0 and self.days[0].is_day_off():
                n_working = 0
            else:
                # Get number of consecutive working days for a given index
                n_working = cons_days_number(self.days, i, day_type=DayType.WORKING_DAY)

            # Check if last working day is actually last in schedule
            if n_working + i >= len(self.days):
                n_off = 0

            # If day is not last, get number of consecutive days off
            else:
                n_off = cons_days_number(self.days, i + n_working, day_type=DayType.DAY_OFF)

            self.blocks.append(Block(n_working, n_off))
            # Increase the current index
            i += n_working + n_off

    def create_schedule_new_day_off(self, current_day_off_index, new_day_off_index):
        """
        Create a new Schedule. The new Schedule will have day with 'new_day_off_index' set to DAY OFF.
        :param current_day_off_index: the index of the current DAY OFF
        :param new_day_off_index: the index of the day that needs to be changed to DAY OFF
        :return:
        """
        # Make a copy of existing Schedule
        schedule_attempt = copy.deepcopy(self)
        # Change the day to day off
        schedule_attempt.change_day_type(new_day_off_index, DayType.DAY_OFF)

        # Check are conditions violated
        nc_off = cons_days_number(schedule_attempt.days, current_day_off_index)

        # Get the blocks with violated min_working days constraint
        invalid_working_days = list(
            filter(lambda block: block.working_days < self.min_working, schedule_attempt.blocks[:-1]))

        if nc_off <= self.max_off and len(invalid_working_days) == 0:
            return schedule_attempt

        return None

    def create_schedules_new_days_off(self, current_day_index):
        """
        Create a new Schedules that will have first available working days before, and after current day off, set to
        DAY OFF. This will be used if number of consecutive days off is lower than min allowed, to create more DAYS OFF.

        Example:
        input: 1 1 1 1 0 1 1
        current_day_index: 5
        output: 1 1 1 0 0 1 1 (first working day before set to day off)
                1 1 1 1 0 0 1 (first working day after set to day off)

        :param current_day_index: the index of the current day
        :return:
        """
        new_schedules = []

        # Get index of the next available working day
        next_day_index = get_next_available_day(self.days, current_day_index, day_type=DayType.DAY_OFF, right=True)
        # Try to change the working day to day off
        s = self.create_schedule_new_day_off(current_day_index, next_day_index)
        if s is not None:
            new_schedules.append(s)

        # Get index of the previous available working day
        previous_day_index = get_next_available_day(self.days, current_day_index, day_type=DayType.DAY_OFF, right=False)
        # Try to change the working day to day off
        s = self.create_schedule_new_day_off(current_day_index, previous_day_index)
        if s is not None:
            new_schedules.append(s)

        return new_schedules

    def create_schedules_new_days_off_wd(self, current_day_index):
        """
        Create a new Schedules that will have first and last available working day in the working days sequence
        current day belongs to set to DAY OFF. Also two more Schedules will be created. They will have day off at the
        place of working day which is min_working days away from the left and right side of sequence.

        Example:
        input: 0 0 1 1 1 1 1 1 0 0
        min_working = 2
        output: 0 0 0 1 1 1 1 1 0 0 (first working day changed to day off)
                0 0 1 1 1 1 1 0 0 0 (last working day changed to day off)
                0 0 1 1 0 1 1 1 0 0 (first working day + min_working changed to day off)
                0 0 1 1 1 0 1 1 0 0 (last working day - min_working changed to day off)

        :param current_day_index: the index of the current day
        :return:
        """
        new_schedules = []

        # Get the index of first day off on right side
        next_day_index_right = get_next_available_day(self.days, current_day_index,
                                                      day_type=DayType.WORKING_DAY,
                                                      right=True)
        # Index of last working day in the sequence
        next_day_index_right -= 1
        s = self.create_schedule_new_day_off(current_day_index, next_day_index_right)
        if s is not None:
            new_schedules.append(s)

        # Get the index of first day off on left side
        next_day_index_left = get_next_available_day(self.days, current_day_index,
                                                     day_type=DayType.WORKING_DAY,
                                                     right=False)
        # Index of first working day in the sequence
        next_day_index_left += 1
        s = self.create_schedule_new_day_off(current_day_index, next_day_index_left)
        if s is not None:
            new_schedules.append(s)

        # Because number of cons working days is greater than max, put day in the 'middle'. Helps if from the both side
        # of working days sequence is max number of days off
        # min_working days before last working day in the sequence
        new_index = next_day_index_right - self.min_working
        if 0 <= new_index < self.num_days:
            s = self.create_schedule_new_day_off(current_day_index, new_index)
            if s is not None:
                new_schedules.append(s)
        # min_working days after first working day in the sequence
        new_index = next_day_index_left + self.min_working
        if 0 <= new_index < self.num_days:
            s = self.create_schedule_new_day_off(current_day_index, new_index)
            if s is not None:
                new_schedules.append(s)

        return new_schedules

    def find_neighborhood(self):
        """
        Find all neighbors for the Schedule. If the input params are valid, the min_working and max_off constraints
        cannot be violated.
        :return:
        """
        neighbors = []
        for day in self.days:
            if day.is_day_off():
                nc_off = cons_days_number(self.days, day.index, day_type=DayType.DAY_OFF)
                # Check if number of consecutive days off is lower than min
                if nc_off < self.min_off:
                    # Create new schedules with changed working days to days off
                    neighbors.extend(self.create_schedules_new_days_off(day.index))

            if day.is_working():
                nc_working = cons_days_number(self.days, day.index, day_type=DayType.WORKING_DAY)
                # Check if number of consecutive working days is higher than max
                if nc_working > self.max_working:
                    neighbors.extend(self.create_schedules_new_days_off_wd(day.index))

        return neighbors

    def evaluate(self):
        """
        Evaluate the Schedule.
        :return:
        """
        penalty = self.eval_number_of_days()
        penalty += self.eval_consecutive_days()
        penalty += self.eval_days_off()

        self.score = ScheduleScore(penalty, self.working_days_num())

    def eval_number_of_days(self):
        """
        Penalize schedule if number of days is over/under the limit.
        :return: number of days over/under the limit times 8/4
        """
        days_difference = abs(len(self.days) - self.num_days)
        return days_difference * PENALTY_NUM_DAYS_GREATER if len(self.days) > self.num_days else \
            days_difference * PENALTY_NUM_DAYS_LOWER

    def eval_consecutive_days(self):
        """
        Penalize schedule if number of consecutive days is invalid. Each invalid block will be penalized by 20.
        :return:
        """
        skip_last_block = True

        penalty = 0
        # TODO: Skip last block?
        # Don't check last block for min day constraint
        if skip_last_block:
            days_to_check = self.blocks[:-1]
            b = self.blocks[-1]
            if b.working_days > self.max_working:
                penalty += b.working_days - self.max_working
            if b.days_off > self.max_off:
                penalty += b.days_off - self.max_off
        else:
            days_to_check = self.blocks

        # Leave blocks with max working days above the limit or min working days below the limit
        invalid_working_days = list(filter(
            lambda block: self.max_working < block.working_days or block.working_days < self.min_working,
            days_to_check))
        # Leave blocks with max off days above the limit or min days off below the limit
        invalid_days_off = list(filter(lambda block: self.max_off < block.days_off or block.days_off < self.min_off,
                                       days_to_check))

        # Get the sum of differences between limitations and schedule days. If max_working is 4 and the block is (6,1)
        # the difference will be 2. The same process will be applied to each block, and differences will be summed.
        working_penalties = sum(map(
            lambda block: block.working_days - self.max_working
            if self.max_working < block.working_days
            else self.min_working - block.working_days, invalid_working_days))

        day_off_penalties = sum(map(
            lambda block: block.days_off - self.max_off
            if self.max_off < block.days_off
            else self.min_off - block.days_off, invalid_days_off))

        return PENALTY_INVALID_CONSECUTIVE_DAYS * (working_penalties + day_off_penalties + penalty)

    def eval_days_off(self):
        """
        Penalize schedule if predefined days off are invalid.
        :return:
        """
        penalty = 0
        for day in self.days:
            if (day.index + 1) % 7 in self.days_off and day.is_working():
                penalty += PENALTY_INVALID_DAY_OFF

        return penalty


class Search:
    """
    Search class.
    """

    def __init__(self, max_iterations, limit_not_improved):
        """
        Init method.
        :param max_iterations: max number of iterations to perform search
        :param limit_not_improved: max number of iterations to improve the Schedule when penalty becomes 0
        """
        self.max_iterations = max_iterations
        self.limit_not_improved = limit_not_improved

    @abstractmethod
    def search(self, initial_schedule):
        raise NotImplemented('Method not implemented.')


class TabuSearch(Search):
    """
    Tabu Search algorithm.
    """

    def __init__(self, tabu_list_size, max_iterations, limit_not_improved):
        super().__init__(max_iterations, limit_not_improved)
        self.tabu_size = tabu_list_size

    def search(self, initial_schedule: Schedule):
        """
        The Tabu search algorithm.
        :param initial_schedule: the initial schedule
        :return:
        """
        count = 0
        initial_schedule.evaluate()
        best_schedule = initial_schedule
        current_schedule = initial_schedule
        tabu_list = []

        not_improved_counter = 0
        while count <= self.max_iterations:
            # Get all of the neighbors
            neighbors = current_schedule.find_neighborhood()
            # Filter already checked schedules
            neighbors = list(filter(lambda neighbor: neighbor not in tabu_list, neighbors))

            if len(neighbors) > 0:
                current_schedule = find_best_schedule(neighbors)
                if current_schedule.score.penalty < best_schedule.score.penalty or (
                        current_schedule.score.penalty == best_schedule.score.penalty and
                        current_schedule.score.total < best_schedule.score.total):
                    not_improved_counter = -1
                    best_schedule = current_schedule

                not_improved_counter += 1

                if best_schedule.score.penalty == 0 and not_improved_counter >= self.limit_not_improved:
                    return best_schedule

                tabu_list.append(current_schedule)

                if len(tabu_list) > self.tabu_size:
                    tabu_list = tabu_list[1:]
            else:
                break
            count += 1
        print(f"Search iterations number: {count}")
        return best_schedule


def check_params(params):
    """
    Check whether params are valid.
    :param params: the params
    :return:
    """
    min_w = params['min_working']
    min_o = params['min_off']
    days_off = params['days_off']
    if not days_off:
        return

    if min_w > 3 and min_o >= 1:
        raise AssertionError(f"'min_working' is {min_w}, and 'min_off' is {min_o}")

    assert min(days_off) - min_w >= 1, \
        f"'min_working_days' is {min_w}, but day off is {DAY_NAME[min(days_off)]}"

    assert min_w <= min(days_off), f"'min_working_days' is {min_w}, but first day off is {DAY_NAME[min(days_off)]}"

    if len(days_off) > 1:
        for i, day_off in enumerate(sorted(days_off)):
            if i + 1 < len(days_off):
                if days_off[i + 1] - day_off > 1:
                    assert days_off[i + 1] - day_off > min_w, \
                        f"'min_working_days' is {min_w}, but days off are {[DAY_NAME[do] for do in days_off]}"


def perform_tabu_search(params):
    """
    For a given params, find the best Schedule.
    :param params: the Schedule params
    :return:
    """
    max_iterations = 5000
    limit_not_improved = 10
    tabu_list_size = 1000

    print(params)
    check_params(params)
    new_schedule = Schedule(params.values())

    tabu_search = TabuSearch(tabu_list_size, max_iterations, limit_not_improved)
    best_schedule = tabu_search.search(new_schedule)
    print(best_schedule)
    print(best_schedule.score)
