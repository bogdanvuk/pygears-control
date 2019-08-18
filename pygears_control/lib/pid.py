from control.matlab import *

def integral(Ki):
    return tf([Ki], [1, 0])

def prop(Kp):
    return tf([Kp], [1])

def deriv(Kd):
    return tf([Kd, 0], [1])


def pid_gen(Kp, Ki=0, Kd=0):
    if Kp == 0:
        print("Proportional parameter must be greater than zero")
        return

    if Ki == 0 and Kd == 0:
        return prop(Kp)

    if Ki == 0 and Kd != 0:
        return parallel(prop(Kp), deriv(Kd))

    if Ki != 0 and Kd == 0:
        return parallel(prop(Kp), integral(Ki))

    if Ki != 0 and Kd != 0:
        return parallel(prop(Kp), integral(Ki), deriv(Kd))
