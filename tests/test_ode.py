from pygears_control.lib import ode, scope
from pygears.lib import drv
from pygears.typing import Float
from pygears.sim import sim
from functools import partial


def rc(t, Vo, Vi, R, C):
    i = (Vi - Vo) / R
    dVo = i / C

    return Vo, dVo


seq = [10.0] * 1000 + [0] * 1000

drv(t=Float, seq=seq) \
    | ode(f=partial(rc, R=100, C=1e-6), init_y=[0], init_x=0) \
    | scope

sim(timeout=len(seq))
