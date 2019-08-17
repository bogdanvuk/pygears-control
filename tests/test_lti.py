from pygears.typing import Float
from pygears.lib import drv
from pygears_control.lib import lti, scope
from pygears.sim import sim


def test_pid():
    Kp = 350
    Ki = 300
    Kd = 50
    clk_freq = 10  # Hz
    seq = [1.] * 500 + [0.] * 500

    drv(t=Float, seq=seq) \
        | lti(num=[Kd, Kp, Ki], den=[1, (10 + Kd), (20 + Kp), Ki], init_x=0, clk_freq=clk_freq) \
        | scope

    sim(timeout=len(seq))


def test_rc():
    R = 100
    C = 1e-6
    clk_freq = 1e6  # Hz
    seq = [1] * 1000 + [0] * 1000

    drv(t=Float, seq=seq) \
        | lti(num=[1], den=[R*C, 1], init_x=0, clk_freq=clk_freq) \
        | scope

    sim(timeout=len(seq))
