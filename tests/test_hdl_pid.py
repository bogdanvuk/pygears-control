from pygears_control.lib.pid import prop, integral
from pygears.lib import scoreboard
from pygears_control.lib import pidtf
from control.matlab import tf
from pygears.typing import Float
from pygears.lib import drv
from pygears_control.lib import lti, scope
from pygears.sim import sim
from pygears import Intf, config, gear, find
from pygears.lib import dreg
from pygears.typing import Fixp, Uint
from pygears import gear
from pygears.typing import Queue, bitw
from pygears.sim.modules.verilator import SimVerilated


@gear
def hdl_p(din, *, Kp):
    dout = din * Kp
    return dout


@gear(hdl={'compile': True, 'inline_conditions': True})
async def hls_i(din, *, Ki) -> b'din*bitw(Ki)*10':
    acc = (din.dtype * type(Ki) * 10)(0)
    print(
        f'{type(acc)} + {din.dtype} * {type(Ki)} = {type(acc)} + {din.dtype * type(Ki)}'
    )
    while True:
        async with din as data:
            print(
                f'{int(acc)} + {int(data)}*{int(Ki)} = {int(acc + data * Ki)}')
            print(
                f'{float(acc)} + {float(data)}*{float(Ki)} = {float(acc + data * Ki)}'
            )
            mult = data * Ki
            acc = acc + mult
            yield acc

@gear(hdl={'compile': True, 'inline_conditions': True})
async def hls_d(din, *, Kd) -> b'din*bitw(Kd)*10':
    dly = (din.dtype * type(Kd) * 10)(0)

    while True:
        async with din as data:
            gain = data * Kd
            sub_s = gain + (-dly)
            dly = gain
            yield sub_s

@gear
def hdl_pid(din, *, Kp, Ki, Kd):
    p = din | hdl_p(Kp=Kp)
    i = din | hls_i(Ki=Ki)
    d = din | hls_d(Kd=Kd)

    return p + i + d

@gear
def hdl_pid_sys(set_point, *, Kp, Ki, Kd, plant):
    plant_out = Intf(Float)

    pid_in = set_point - plant_out
    pid_in | scope(title="PID Input")

    pid_in = pid_in | Fixp[2, 22]

    pid_out = pid_in | hdl_pid(Kp=Kp, Ki=Ki, Kd=Kd, sim_cls=SimVerilated)

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
        | hdl_pid_sys(Kp=Kp, Ki=Ki, Kd=Kd, plant=plant)

    find('/hdl_pid_sys/plant.x').producer | scope(title="PID Output")
    plant_out | scope(title="Plant Output")

    sim('/tools/home/tmp', timeout=len(seq))

from pygears import config
config['hdl/debug_intfs'] = ['*']

sim_hdl_pid(Uint[10](373), Fixp[4, 16](807 / 1000), Fixp[20, 24](50*1000))
