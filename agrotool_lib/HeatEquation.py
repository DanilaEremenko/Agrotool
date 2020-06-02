import numpy as np
from scipy.linalg import solve_banded


def cn_diffusion_equation(T_0, D_arr, C_arr, dx, dt, N, bc_val, bc_type=['flux', 'flux']):
    """
    TODO define metrics
    :param T_0:     распределение интересующей величины в начальный момент времени
    :param D_arr:   текущее значение коэффициента проводимости интересующей величины
    :param C_arr:   коэффициенты теплоемкости(для задачи теплопереноса)
    :param dx:      шаг по координате(толщина слоя)
    :param dt:      шаг по времени
    :param N:       число шагов по времени
    :param bc_val:  граничные условия
    :param bc_type: тип граничный условий(flux - поток, val - значение)
    :return:
    """

    def _central_diff():

        A = np.zeros((len_x, len_x))
        C = np.zeros(len_x)

        for i in range(len_x):
            D_forward = (D_arr[i] + D_arr[i + 1]) / (2 * C_arr[i]) if i != len_x - 1 else D_arr[i] / C_arr[i]
            D_backward = (D_arr[i] + D_arr[i - 1]) / (2 * C_arr[i]) if i != 0 else D_arr[i] / C_arr[i]

            A_q = np.zeros(len_x)
            if i == 0:
                if bc_type[0] == 'val':
                    A_q[i] = 1.0
                else:
                    A_q[i] = 1. + 0.5 * s * D_forward
                    A_q[i + 1] = -0.5 * s * D_forward
            elif i == len_x - 1:
                if bc_type[1] == 'val':
                    A_q[i] = 1.0
                else:
                    A_q[i] = 1. + 0.5 * s * D_backward
                    A_q[i - 1] = -0.5 * s * D_backward
            else:
                A_q[i] = 1. + 0.5 * s * D_forward + 0.5 * s * D_backward
                A_q[i + 1] = -0.5 * s * D_forward
                A_q[i - 1] = -0.5 * s * D_backward
            A[i, :] = A_q

        B = 2. * np.identity(len_x) - A
        if bc_type[0] == 'val':
            B[0, :] = np.zeros(len_x)
        if bc_type[1] == 'val':
            B[-1, :] = np.zeros(len_x)

        if bc_type[0] == 'val':
            C[0] = bc_val[0]
        else:
            C[0] = - bc_val[0] * s * dx / C_arr[0]  # TODO: Проверить !!!!!
        if bc_type[1] == 'val':
            C[-1] = bc_val[1]
        else:
            C[-1] = bc_val[1] * s * dx / C_arr[-1]  # TODO: Проверить !!!!!

        return A, B, C

    def _diagonal_form(A):
        ab = np.zeros((3, len_x))
        ab[0, 1:] = np.diagonal(A, 1)
        ab[1, :] = np.diagonal(A, 0)
        ab[2, :-1] = np.diagonal(A, -1)
        return ab

    def _CN_step(j):
        A, B, C = _central_diff()
        T[:, j + 1] = solve_banded((1, 1), _diagonal_form(A), np.dot(B, T[:, j]) + C)

    def _main_step():
        for k in range(0, N - 1):
            _CN_step(k)

    #############################################################
    # -------------------- MAIN ---------------------------------
    #############################################################
    if (bc_type[0] != 'val') and (bc_type[0] != 'flux'):
        raise Exception('Boundary condition mode is not implemented')
    if (bc_type[1] != 'val') and (bc_type[1] != 'flux'):
        raise Exception('Boundary condition mode is not implemented')

    dim = len(T_0.shape)
    len_x = T_0.shape[0]
    if dim != 1:
        print('1D only, adjust initial wave array')
        return 0

    s = dt / (dx ** 2)

    t = np.linspace(0., (N - 1) * dt, N)

    T = np.zeros((len_x, N))
    T[:, 0] = T_0

    _main_step()

    return T, t


def solver_example():
    import numpy as np
    from matplotlib import pyplot as plt

    T_0 = np.array([40, 20, 20, 20, 20, 20, 20, 20, 20, 20])
    D_arr = np.array([200, 200, 200, 200, 200, 200, 200, 200, 200, 200])
    C_arr = np.ones(10)
    C_arr[3] = 4
    T, t = cn_diffusion_equation(T_0,
                                 D_arr,
                                 C_arr,
                                 dx=10,
                                 N=20,
                                 dt=100,
                                 # bc_val=[40.0, 20.0],
                                 # bc_type=['val', 'val']
                                 bc_val=[40.0, 0.0],
                                 bc_type=['val', 'flux']  # Изоляция на нижнем конце
                                 )
    plt.plot(T)
    plt.show()

    import plotly.express as px
    from pandas import DataFrame

    t_full = []
    layers = []
    for layer_n, T_layer_history in enumerate(T):
        t_full = [*t_full, *t]
        layers = [*layers, *np.ones(len(T_layer_history), dtype=int) * (layer_n + 1)]

    temp_df = DataFrame(
        {
            't': t_full,
            'layer': layers,
            'layer_sym': list(map(lambda layer: "layer_%d" % layer, layers)),
            'T': T.flatten()
        }
    )
    fig2 = px.scatter(temp_df, x="layer_sym", y="T", animation_frame="t", animation_group='layer_sym')
    fig2.show()


if __name__ == '__main__':
    solver_example()
