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

    # TODO Отработать С_arr !!!!

    def _central_diff():

        A = np.zeros((len_x, len_x))
        C = np.zeros(len_x)

        for i in range(len_x):
            if dim == 1:
                D_forward = (D_arr[i] + D_arr[i + 1]) / 2 if i != len_x-1 else D_arr[i]
                D_backward = (D_arr[i] + D_arr[i - 1]) / 2 if i != 0 else D_arr[i]

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

        if dim == 1:
            if bc_type[0] == 'val':
                C[0] = bc_val[0]
            else:
                C[0] = - bc_val[0]*s*dx  # TODO: Проверить !!!!!

            if bc_type[1] == 'val':
                C[-1] = bc_val[1]
            else:
                C[-1] = - bc_val[1]*s*dx  # TODO: Проверить !!!!!

        return A, B, C

    def _diagonal_form(A):

        ab = np.zeros((3, len_x))

        ab[0, 1:] = np.diagonal(A, 1)
        ab[1, :] = np.diagonal(A, 0)
        ab[2, :-1] = np.diagonal(A, -1)

        return ab

    def _CN_step(j):
        if dim == 1:
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

    T, t = CN_diffusion_equation(T_0=np.array([40, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
                                 D_arr=np.array([100, 100, 100, 100, 100, 100, 100, 100, 100, 100]),
                                 C_arr=np.zeros(10),
                                 x=np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95]),
                                 dx=10,
                                 N=20,
                                 s=0.005,
                                 bc_val=[40.0, 20.0],
                                 bc_type=['val', 'val']
                                 )
    plt.plot(T)
    plt.show()


if __name__ == '__main__':
    solver_example()
