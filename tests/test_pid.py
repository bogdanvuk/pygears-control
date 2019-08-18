from pygears_control.lib import pidtf
from control.matlab import tf, feedback, pade

from pygears.typing import Float
from pygears.lib import drv
from pygears_control.lib import lti, scope
from pygears.sim import sim
from pygears import Intf, config

# import matplotlib
# matplotlib.use('GTK3Cairo', warn=False, force=True)


def test_pid_lti_feedback(Kp, Ki, Kd):
    pid = pidtf(Kp, Ki, Kd)

    config['sim/clk_freq'] = 1000

    plant = tf([1], [1, 10, 20])

    sys = feedback(pid * plant)

    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    set_point | lti(sys=sys, init_x=0) | scope

    sim(timeout=len(seq))


def test_pi_lti_comb(Kp, Ki, Kd):
    pid = pidtf(Kp, Ki, Kd)
    config['sim/clk_freq'] = 1000

    plant = tf([1], [1, 10, 20])

    sys = feedback(plant * pid)

    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    plant_out = Intf(Float)

    pid_in = set_point - plant_out

    plant_out |= pid_in \
        | lti(sys=sys, init_x=0) \

    pid_in | scope(title="PID Input")
    plant_out | scope(title="Plant Output")

    sim(timeout=len(seq))


def test_pi_pg_comb(Kp, Ki, Kd):
    Kp, Ki, Kd = 350, 300, 0
    pid = pidtf(Kp, Ki, Kd)

    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    plant_out = Intf(Float)

    pid_in = set_point - plant_out

    pid_out = pid_in \
        | lti(sys=pid, init_x=0) \

    plant_out |= pid_out \
        | lti(sys=plant, init_x=0) \

    pid_in | scope(title="PID Input")
    pid_out | scope(title="PID Output")
    plant_out | scope(title="Plant Output")

    sim(timeout=len(seq))


# def test_p():
#     test_pid_controller(350, 0, 0)


# def test_pi():
#     test_pid_controller(350, 300, 0)


# test_pid_controller(10000, 30, 0)
# test_pid_controller(350, 300, 0)
test_pi_lti_comb(350, 300, 0)
# test_pi_pg_comb(350, 300, 0)
# test_pi()


# def test_pd():
#     test_pid_controller(350, 0, 50)


# def test_pid():
#     test_pid_controller(350, 300, 50)
