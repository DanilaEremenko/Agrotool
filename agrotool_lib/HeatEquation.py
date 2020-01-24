from pycav.pde import CN_diffusion_equation


def solver_example():
    import numpy as np
    from matplotlib import pyplot as plt

    def D_func(x):
        return 100 + x

    T, t = CN_diffusion_equation(T_0=np.array([20, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
                                 D=D_func,
                                 x_list=np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95]),
                                 dx=10,
                                 N=10,
                                 s=0.005,
                                 wall_T=[40.0, 20.0]
                                 )
    plt.plot(T)
    plt.show()


if __name__ == '__main__':
    solver_example()
