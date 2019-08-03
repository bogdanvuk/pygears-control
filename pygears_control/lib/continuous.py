import threading
import queue
from pygears import GearDone, gear, module, registry, config
from pygears.typing import Float
from pygears.sim import clk, timestep


def cont_wrap(f, qin, qout, init):
    def wrap(t, y):
        res = f(t, y, wrap.x)

        if t < wrap.t:
            return res

        if wrap.done_out:
            raise GearDone

        if qout.empty():
            qout.put(y)

        wrap.x = wrap.next_x
        wrap.next_x, wrap.t = qin.get()

        if wrap.t is None:
            raise GearDone

        return res

    wrap.x = init
    wrap.next_x = init
    wrap.t = 0
    wrap.done_out = False

    return wrap


@gear
async def actuator(x: Float, *, qin, clk_freq, init):

    x_data = init
    while (1):
        if not x.empty():
            x_data = x.get_nb()

        qin.put((x_data, (timestep() + 1) / clk_freq))

        await clk()


@gear
async def sensor(*, qout) -> Float:
    while (1):
        res = qout.get()
        # sim_log().info(res)
        yield res

        await clk()


@gear
def continuous(x: Float, *, f, init_x, clk_freq=None) -> Float:

    if clk_freq is None:
        clk_freq = config['sim/clk_freq']

    qin = queue.Queue(maxsize=1)
    qout = queue.Queue(maxsize=1)

    module()._thrd = threading.Thread(target=f,
                                      args=(qin, qout, clk_freq, init_x))
    module()._thrd.start()

    def cleanup_event(sim):
        qin.put((None, None))

        if not qout.empty():
            qout.get_nowait()

    def cleanup_setup(module):
        registry('sim/simulator').events['after_cleanup'].append(cleanup_event)

    actuator(x, qin=qin, clk_freq=clk_freq, init=init_x)

    return sensor(qout=qout, sim_setup=cleanup_setup)
