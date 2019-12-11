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
    prob = 0.0

    while True:
        prec_history = np.zeros(len(T_history))
        prob += 0.1
        not_zero_indexes = []

        for i in range(1, len(T_history)):

            if T_history[i] < T_history[i - 1]:
                max_rand = int(1 / prob)
                prec_history[i] = np.random.uniform(min_prec, max_prec) * \
                                  int(np.random.randint(0, max_rand + 1) / max_rand)

                if prec_history[i] != 0:
                    not_zero_indexes.append(i)

                if sum(prec_history) > prec_sum:
                    diff = sum(prec_history) - prec_sum
                    for i in not_zero_indexes:
                        prec_history[i] -= diff / len(not_zero_indexes)
                    return prec_history
