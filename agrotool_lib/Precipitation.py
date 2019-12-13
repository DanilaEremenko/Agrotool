import numpy as np


# TODO check
def get_precipitation_history(prec_sum, T_history):
    """

    :param prec_sum: sum of precipitation
    :param T_history: history of temperature
    :return: prec_history : list of precipitation
    """
    if prec_sum == 0:
        return np.zeros(len(T_history))

    min_prec = prec_sum / (len(T_history) / 2)
    max_prec = prec_sum / (len(T_history) / 4)
    common_prob = 0.0

    while True:
        prec_history = np.zeros(len(T_history))
        common_prob += 0.1
        not_zero_indexes = []

        for i, curr_t in enumerate(T_history):

            if T_history[i] < T_history[i - 1]:  # probability bigger if t falls
                prob = common_prob + 0.2
            else:
                prob = common_prob

            max_rand = int(1 / prob)

            if max_rand == 0:
                prec_history[i] = 0
            else:
                prec_history[i] = np.random.uniform(min_prec, max_prec) * \
                                  int(np.random.randint(0, max_rand + 1) / max_rand) #

            if prec_history[i] != 0:
                not_zero_indexes.append(i)

            if sum(prec_history) > prec_sum:
                diff = sum(prec_history) - prec_sum
                for i in not_zero_indexes:
                    prec_history[i] -= diff / len(not_zero_indexes)
                return prec_history
