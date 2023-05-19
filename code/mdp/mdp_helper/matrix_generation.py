from setting import *

from .matrix import *


def generate_matrixs(indexer, probability_provider, alpha, gamma):
    # print(action_lib)
    A, H, P = (
        [None] * len(actions_lib),
        [None] * len(actions_lib),
        [None] * len(actions_lib),
    )
    # init the data.
    states_num, rounds, fork_states_num = (
        len(indexer.index_to_state),
        indexer.rounds,
        indexer.fork_states_num,
    )

    max_fork_len = rounds - 1

    # rounds * 80 is just a random number that guaranteed to be greater than # of elements with non zero value.
    preset_num_element_in_matrix = states_num * rounds * 80

    matrixs = [None] * len(actions_lib)
    for action in actions_lib:
        matrixs[action] = Matrix(preset_num_element_in_matrix)

    # init default value for actions except ADOPT.
    ordered_list = np.arange(states_num)
    ones = np.ones([states_num])
    action_without_adopt = actions_lib[1:]

    # Illustrate why we need punish parameter.
    punish_parameter = 1000000

    for action in action_without_adopt:
        matrixs[action].row[0:states_num] = ordered_list
        matrixs[action].col[0:states_num] = ordered_list
        matrixs[action].p[0:states_num] = ones
        matrixs[action].h[0:states_num] = ones * punish_parameter
        matrixs[action].cursor = states_num

    # probability under action adopt.
    matrixs[ADOPT].row[0:states_num] = ordered_list
    matrixs[ADOPT].col[0:states_num] = ones * indexer.get_index_by_state(
        1, 1, 0, INACTIVE, SETTLED
    )
    matrixs[ADOPT].p[0:states_num] = ones * alpha

    matrixs[ADOPT].row[states_num : 2 * states_num] = ordered_list
    matrixs[ADOPT].col[states_num : 2 * states_num] = ones * indexer.get_index_by_state(
        0, 0, 1, INACTIVE, SETTLED
    )
    matrixs[ADOPT].p[states_num : 2 * states_num] = ones * (1 - alpha)
    matrixs[ADOPT].cursor = 2 * states_num

    for index in range(states_num):
        a, a_prime, h, f, s = indexer.get_state_by_index(index)
        assert indexer.verify_correctness_of_state(a, a_prime, h)

        # reward of ADOPT
        matrixs[ADOPT].h[index] = h
        matrixs[ADOPT].h[index + states_num] = h

        if a < max_fork_len and h < max_fork_len:
            # OVERRIDE
            if a > h:
                # clear the data in the diagonal.
                matrixs[OVERRIDE].h[index] = 0
                matrixs[OVERRIDE].p[index] = 0

                # case1: no block left after override.
                if a == h + 1:
                    matrixs[OVERRIDE].add_element(
                        index,
                        indexer.get_index_by_state(1, 1, 0, INACTIVE, SETTLED),
                        alpha,
                        h + 1,
                    )
                    matrixs[OVERRIDE].add_element(
                        index,
                        indexer.get_index_by_state(0, 0, 1, INACTIVE, SETTLED),
                        1 - alpha,
                        h + 1,
                    )

                # case2: there are withheld blocks after override.
                elif a >= h + 2:
                    matrixs[OVERRIDE].add_elements_when_withholding(
                        index,
                        "OVERRIDE",
                        indexer,
                        probability_provider,
                    )

            # WAIT in INACTIVE.
            if f == INACTIVE:
                matrixs[WAIT].h[index] = 0
                matrixs[WAIT].p[index] = 0
                if a_prime == 0:
                    matrixs[WAIT].add_element(
                        index,
                        indexer.get_index_by_state(a + 1, 1, h, INACTIVE, UNSETTLED),
                        alpha,
                        0,
                    )
                    matrixs[WAIT].add_element(
                        index,
                        indexer.get_index_by_state(a, 0, h + 1, INACTIVE, UNSETTLED),
                        1 - alpha,
                        0,
                    )

                # Distinguish between override case and no override case.
                # To judge whether there is match during wait, we need to know the h+, which
                # cannot get at this point.
                elif a - a_prime < h and a_prime > 0:
                    matrixs[WAIT].add_elements_when_withholding(
                        index,
                        "WAIT_WITHOUT_OVERRIDE",
                        indexer,
                        probability_provider,
                        gamma,
                    )

                elif a - a_prime == h and a_prime > 0:
                    matrixs[WAIT].add_elements_when_withholding(
                        index,
                        "WAIT_WITH_OVERRIDE",
                        indexer,
                        probability_provider,
                        gamma,
                    )
            # WAIT in active
            if a >= h and f == ACTIVE and a_prime == a - h and h != 0:
                matrixs[WAIT].h[index] = 0
                matrixs[WAIT].p[index] = 0
                action_type = "WAIT_IN_ACTIVE"
                current_action = WAIT

                # If there is no withheld block after the action.
                if a_prime == 0:
                    matrixs[current_action].add_element(
                        index,
                        indexer.get_index_by_state(
                            a + 1, a - h + 1, h, ACTIVE, UNSETTLED
                        ),
                        alpha,
                        0,
                    )

                    matrixs[current_action].add_element(
                        index,
                        indexer.get_index_by_state(a - h, a - h, 1, INACTIVE, SETTLED),
                        gamma * (1 - alpha),
                        h,
                    )
                    matrixs[current_action].add_element(
                        index,
                        indexer.get_index_by_state(
                            a, a - h, h + 1, INACTIVE, UNSETTLED
                        ),
                        (1 - gamma) * (1 - alpha),
                        0,
                    )
                # If there are withheld blocks after the action.
                elif a_prime > 0:
                    matrixs[current_action].add_elements_when_withholding(
                        index,
                        action_type,
                        indexer,
                        probability_provider,
                        gamma,
                    )
    # Finish the matrix generation, then try to transfer it to sparse metrixs.
    for action in actions_lib:
        P[action], A[action], H[action] = matrixs[action].transfer_to_sparse(states_num)

    return P, A, H
