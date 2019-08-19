from control.matlab import tf, parallel


def integral(Ki):
    return tf([Ki], [1, 0])


def prop(Kp):
    return tf([Kp], [1])


def deriv(Kd):
    return tf([Kd, 0], [0.001, 1])


def pidtf(Kp, Ki=0, Kd=0):
    assert Kp != 0, "Proportional parameter must be greater than zero"

    branches = []
    for k, f in zip((Kp, Ki, Kd), (prop, integral, deriv)):
        if k != 0:
            branches.append(f(k))

    return parallel(*branches)
