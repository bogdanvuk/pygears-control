from control.matlab import tf, parallel


def integral(Ki):
    return tf([Ki], [1, 0])


def prop(Kp):
    return tf([Kp], [1])


def deriv(Kd, N_filt=0):
    return tf([Kd, 0], [1]) * lp_filt(N_filt)


def lp_filt(N):
    return tf([N], [1, N])


def pidtf(Kp, Ki=0, Kd=0, N_filt=0):
    assert Kp != 0, "Proportional parameter must be greater than zero"

    p = prop(Kp)
    i = integral(Ki)
    d = deriv(Kd, N_filt)

    return parallel(p, i, d)
