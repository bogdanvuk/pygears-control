from pygears_control.lib import ode, scope
from pygears.lib import drv
from pygears.typing import Float
from pygears.sim import sim
from functools import partial


def rc(t, y, x, R, C):
    i = (x - y) / R
    return i / C


drv(t=Float, seq=[10.0]*1000 + [0]*1000 + [10.0]*1000 + [0]*1000) \
    | ode(f=partial(rc, R=100, C=1e-6), init_y=[0], init_x=0) \
    | scope

sim(timeout=4000)
