import numpy as np
from scipy.linalg import solve_banded


def CN_diffusion_equation(T_0, D_arr, C_arr, x, dx, N, bc_val, bc_type=['flux', 'flux'], s=0.25):
    """
    TODO update doc
    :param T_0:
    :param D_arr:
    :param C_arr:
    :param x: list
    :param dx:
    :param N:
    :param bc_val:
    :param bc_type: array with len 2, elements can be 'flux' or 'val'
    :param s:
    :return:
    """

    def _central_diff():  # TODO check

        A = np.zeros((len_x - 2, len_x - 2))
        C = np.zeros((len_x - 2))

        for i in range(len_x - 2):  # TODO why -2
            if dim == 1:
                # D_forward = D(q[i] + dx / 2.)
                D_forward = (D_arr[i] + D_arr[i + 1]) / 2
                # D_backward = D(q[i] - dx / 2.)
                D_backward = (D_arr[i] + D_arr[i - 1]) / 2 if i != 0 else D_arr[i]

            A_q = np.zeros((len_x - 2))
            A_q[i] = 1. + 0.5 * s * D_forward + 0.5 * s * D_backward

            if i == 0:
                A_q[i + 1] = -0.5 * s * D_forward
            elif i == len_x - 3:
                A_q[i - 1] = -0.5 * s * D_backward
            else:
                A_q[i + 1] = -0.5 * s * D_forward
                A_q[i - 1] = -0.5 * s * D_backward
            A[i, :] = A_q

        B = 2. * np.identity(len_x - 2) - A

        if dim == 1:
            if bc_type[0] == 'val':
                C[0] = s * D_arr[0] * bc_val[0]
            else:
                raise Exception('flux mode is not implemented')

            if bc_type[1] == 'val':
                C[-1] = s * D_arr[-1] * bc_val[1]
            else:
                raise Exception('flux mode is not implemented')

        return A, B, C

    def _diagonal_form(A):

        ab = np.zeros((3, len_x - 2))

        ab[0, 1:] = np.diagonal(A, 1)
        ab[1, :] = np.diagonal(A, 0)
        ab[2, :-1] = np.diagonal(A, -1)

        return ab

    def _CN_step(j):
        if dim == 1:
            A, B, C = _central_diff()

            T[1:-1, j + 1] = solve_banded((1, 1), _diagonal_form(A), np.dot(B, T[1:-1, j]) + C)

    def _main_step():
        T[0, :] = bc_val[0]
        T[-1, :] = bc_val[1]
        for k in range(0, N - 1):
            _CN_step(k)

    #############################################################
    # -------------------- MAIN ---------------------------------
    #############################################################
    dim = len(T_0.shape)
    len_x = T_0.shape[0]

    if dim != 1:
        print('1D only, adjust initial wave array')
        return 0

    dt = s * dx ** 2

    t = np.linspace(0., (N - 1) * dt, N)

    if dim == 1:
        T = np.zeros((len_x, N))
        T[:, 0] = T_0

    _main_step()

    return T, t


def solver_example():
    import numpy as np
    from matplotlib import pyplot as plt

    def D_func(x):
        return 100 + x

    T, t = CN_diffusion_equation(T_0=np.array([20, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
                                 D_arr=np.array([105, 115, 125, 135, 145, 155, 165, 175, 185, 195]),
                                 C_arr=np.zeros(10),
                                 x=np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95]),
                                 dx=10,
                                 N=10,
                                 s=0.005,
                                 bc_val=[40.0, 20.0],
                                 bc_type=['val', 'val']
                                 )
    plt.plot(T)
    plt.show()


if __name__ == '__main__':
    solver_example()
