from pygears_control.lib import ngspice, scope
from pygears.lib import drv
from pygears.typing import Float
from pygears.sim import sim
from functools import partial
from PySpice.Spice.Library import SpiceLibrary
import math
import os


def test_rc():
    def rc(c, ins, outs, R, C):
        c.R(1, 'input', 'output', R)
        c.C(1, 'output', c.gnd, C)
        ins.append(('input', c.gnd))
        outs.append(('output', c.gnd))

    drv(t=Float, seq=[10.0] * 1000 + [0] * 1000 + [10.0] * 1000 + [0] * 1000) \
        | ngspice(f=partial(rc, R=100, C=1e-6), init_x=0) \
        | scope

    sim(timeout=4000)


def test_half_rect():
    spice_library = SpiceLibrary(os.path.abspath(os.path.dirname(__file__)))
    spice_library['1N4148']

    def half_rect(c, ins, outs):
        c.include(spice_library['1N4148'])
        ins.append(('in', c.gnd))
        outs.append(('output', c.gnd))

        c.X('D1', '1N4148', 'in', 'output')
        c.R('load', 'output', c.gnd, 100)
        c.C('1', 'output', c.gnd, 1e-3)

    def sinus(a, w, th, t_step):
        t = 0
        while True:
            yield a * math.sin(w * t + th)
            t += t_step

    clk_freq = 1e6

    drv(t=Float, seq=sinus(a=10, w=2*math.pi*50, th=0, t_step=1 / clk_freq)) \
        | ngspice(f=half_rect, init_x=0) \
        | scope

    sim(timeout=40000)
