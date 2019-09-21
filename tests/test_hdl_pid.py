from control.matlab import tf
from pygears.lib import drv
from pygears_control.lib import lti, scope
from pygears.sim import sim
from pygears import Intf, config, gear, find
from pygears.typing import Fixp, Uint, Float
from pygears import gear
from pygears.sim.modules.verilator import SimVerilated
from pygears_control.lib.pid import hdl_pid, hls_pid


@gear
def hdl_pid_sys(set_point, *, Kp, Ki, Kd, Ts, plant):
    plant_out = Intf(Float)

    pid_in = set_point - plant_out
    pid_in | scope(title="PID Input")

    pid_in = pid_in | Fixp[2, 22]

    pid_out = pid_in | hdl_pid(
        Kp=Uint[10](Kp), Ki=Fixp[4, 16](Ki / Ts), Kd=Fixp[20, 24](Kd * Ts))

    pid_out = pid_out | Float

    plant_out |= pid_out \
        | lti(name='plant', sys=plant, init_x=0)

    return plant_out


def sim_hdl_pid(Kp, Ki, Kd):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq'] * 2

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | hdl_pid_sys(Kp=Kp, Ki=Ki, Kd=Kd, Ts=config['sim/clk_freq'], plant=plant)

    find('/hdl_pid_sys/plant.x').producer | scope(title="PID Output")
    plant_out | scope(title="Plant Output")

    sim('/tools/home/tmp', timeout=len(seq))


from pygears import config
config['hdl/debug_intfs'] = ['*']

sim_hdl_pid(373, 807, 50)
