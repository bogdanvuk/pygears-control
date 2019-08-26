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


@gear
def hdl_i(din, *, Ki):

    accum_s = Intf(Fixp[5, 28])
    gain = din * Ki

    dout = gain + accum_s
    accum_s |= dout | dreg

    return dout


@gear
def hdl_pi(din, *, Kp, Ki):
    p = din | hdl_p(Kp=Kp)
    i = din | hls_i(Ki=Ki)

    return p + i


@gear
def hdl_pi_sys(set_point, *, Kp, Ki, plant):
    plant_out = Intf(Float)

    pi_in = set_point - plant_out
    pi_in | scope(title="PI Input")

    pi_in = pi_in | Fixp[2, 22]

    pi_out = pi_in | hdl_pi(Kp=Kp, Ki=Ki, sim_cls=SimVerilated)
    # pi_out = pi_in | hdl_pi(Kp=Kp, Ki=Ki)

    pi_out = pi_out | Float

    plant_out |= pi_out \
        | lti(name='plant', sys=plant, init_x=0)

    return plant_out


def sim_hdl_pi(Kp, Ki):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    # seq = [0.] * 2 + [1.] * config['sim/clk_freq'] * 2
    seq = [0.] * 2 + [1.] * 500

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | hdl_pi_sys(Kp=Kp, Ki=Ki, plant=plant)

    find('/hdl_pi_sys/plant.x').producer | scope(title="PI Output")
    plant_out | scope(title="Plant Output")

    sim('/tools/home/tmp', timeout=len(seq))


from pygears import config
config['hdl/debug_intfs'] = ['*']
sim_hdl_pi(Uint[10](300), Fixp[4, 16](300 / 1000))
