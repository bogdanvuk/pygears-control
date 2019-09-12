from pygears_control.lib import ngspice, scope
from pygears.lib import drv, shred
from pygears.typing import Float, bitw
from pygears.sim import sim
from PySpice.Spice.Library import SpiceLibrary
import os

from PySpice.Unit import *

from pygears.lib import pulse
from pygears.typing import Tuple, Uint

from pygears.lib.verif import drv
from pygears.sim.modules.verilator import SimVerilated
from pygears.lib import shred

def test_buck_converter():
    spice_library = SpiceLibrary(os.path.abspath(os.path.dirname(__file__)))
    spice_library['1N4148']

    Vin = 20@u_V
    Vout = 15@u_V
    Vpulse = 5@u_V
    ratio = Vout / Vin

    clk_freq = 1@u_MHz
    clk_period = clk_freq.period

    sw_freq = 50@u_kHz
    sw_period = sw_freq.period

    sw_period_cnt = int(sw_period / clk_period)
    sw_width_cnt = int(sw_period_cnt * (1-ratio))
    w_period = bitw(sw_period_cnt)

    def buck_converter(c, ins, outs):
        c.include(spice_library['1N4148'])
        ins.append(('gate', c.gnd))
        outs.append(('output', c.gnd))

        Rload = 3@u_Ohm
        L = 750@u_uH
        Cout = 0.47@u_uF

        c.V('input', 'in', c.gnd, Vin)

        c.VCS(name='sw1', input_plus='gate', input_minus=c.gnd, output_minus='in', output_plus='sw_out', model='SW', initial_state='off')
        c.model('SW','SW', Ron=1@u_mOhm, Roff=100@u_MOhm, Vt=1.1@u_V)

        c.X('D1', '1N4148', c.gnd, 'sw_out')
        c.L(1, 'sw_out', 'output', L)
        c.R(1, 'output', c.gnd, Rload)
        c.C(1, 'output', c.gnd, Cout)

    seq = [(sw_period_cnt, sw_width_cnt)]*5000
    din = pulse(drv(t=Tuple[Uint[w_period], Uint[w_period]], seq=seq), sim_cls=SimVerilated)[0] | Float
    din = din * int(Vpulse)

    dout = din | ngspice(f=buck_converter, init_x=0)

    dout | scope
    dout | shred

    sim(timeout=4000)


test_buck_converter()
