from constants import SCHEDULE_TEST_PARAMS
from model import perform_tabu_search, Schedule


def test_schedule():
    test_params = SCHEDULE_TEST_PARAMS[0]

    new_schedule = Schedule(test_params.values())
    new_schedule.build_blocks()
    print(new_schedule)
    nbs = new_schedule.find_neighborhood()
    print(nbs[0].eval_consecutive_days())
    print(nbs[0].eval_number_of_days())
    print(nbs[0].eval_days_off())
    print(nbs[0].working_days_num())

    s1 = Schedule(test_params.values())
    s11 = Schedule(test_params.values())

    s2 = Schedule(SCHEDULE_TEST_PARAMS[1].values())

    print(s1 == s11)
    print(s1 == s2)


if __name__ == '__main__':
    for i, params in enumerate(SCHEDULE_TEST_PARAMS):
        print(f'{i + 1}.')
        try:
            perform_tabu_search(params)
        except AssertionError as e:
            print(e)
        print('-----------------')
