from pygears_control.lib import pid_gen
from control.matlab import *

from pygears.typing import Float
from pygears.lib import drv
from pygears_control.lib import lti, scope
from pygears.sim import sim

# import matplotlib
# matplotlib.use('GTK3Cairo', warn=False, force=True)

def test_pid_controller(Kp, Ki, Kd):
    pid = pid_gen(Kp, Ki, Kd)

    plant = tf([1], [1, 10, 20])

    sys = feedback(plant * pid, 1)

    clk_freq = 100
    seq = [0.] * 2 + [1.] * 200

    den = sys.den[0][0].tolist()
    num = sys.num[0][0].tolist()

    set_point = drv(t=Float, seq=seq)

    set_point | lti(num=num, den=den, init_x=0, clk_freq=clk_freq) | scope

    sim(timeout=len(seq))


def test_p():
    test_pid_controller(350, 0 ,0)

def test_pi():
    test_pid_controller(350, 300, 0)

def test_pd():
    test_pid_controller(350, 0, 50)

def test_pid():
    test_pid_controller(350, 300, 50)
