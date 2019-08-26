from pygears_control.lib.pid import prop
from pygears_control.lib import pidtf
from control.matlab import feedback, tf

from pygears.typing import Float
from pygears.lib import drv, scoreboard
from pygears.sim.modules.verilator import SimVerilated
from functools import partial
from pygears_control.lib import lti, scope
from pygears.sim import sim
from pygears import Intf, config, gear, find

from pygears.typing import Fixp, Ufixp


@gear
def lti_p_sys(set_point, *, Kp, plant):
    p = prop(Kp)

    plant_out = Intf(Float)

    p_in = set_point - plant_out

    p_out = p_in \
        | lti(name='p', sys=p, init_x=0)

    plant_out |= p_out \
        | lti(name='plant', sys=plant, init_x=0)

    return plant_out


def sim_lti_p(Kp):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq'] * 2

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | lti_p_sys(Kp=Kp, plant=plant)

    find('/lti_p_sys/p.x').producer | scope(title="P Input")
    find('/lti_p_sys/p.dout').consumer | scope(title="P Output")
    plant_out | scope(title="Plant Output")

    sim(timeout=len(seq))


@gear
def hdl_p(din, *, Kp):
    dout = din * Kp
    return dout


@gear
def hdl_p_sys(set_point, *, Kp, plant):
    plant_out = Intf(Float)

    p_in = (set_point - plant_out) | Fixp[2, 22]

    p_out = p_in | hdl_p(Kp=Kp, sim_cls=SimVerilated)

    plant_out |= p_out | Float | lti(name='plant', sys=plant, init_x=0)

    return plant_out


def test_hdl_p(Kp):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq'] * 2

    set_point = drv(t=Float, seq=seq)
    # set_point | scope(title="Set point")

    plant_out = set_point | hdl_p_sys(Kp=Kp, plant=plant)

    plant_out | scope(title="Plant output")

    sim(timeout=len(seq))


def comp_p_hdl_lti(Kp):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq'] * 2

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point | hdl_p_sys(Kp=Kp, plant=plant)
    plant_out | scope(title="HDL Plant output")

    ref_out = set_point | lti_p_sys(Kp=Kp, plant=plant)
    ref_out | scope(title="LTI Plant output")

    report = []
    scoreboard(plant_out, ref_out, report=report, tolerance=5e-2)

    sim(timeout=len(seq))


# sim_lti_p(100)
# test_hdl_p(100)
comp_p_hdl_lti(100)
