from pygears import config, gear, registry
from pygears.typing import Float
from pygears.sim import clk, timestep
import multiprocessing


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
        yield res

        await clk()


@gear
def continuous(x: Float, *, f, init_x, clk_freq=None) -> Float:

    if clk_freq is None:
        clk_freq = config['sim/clk_freq']

    qin = multiprocessing.Queue(maxsize=1)
    qout = multiprocessing.Queue(maxsize=1)
    _proc = multiprocessing.context.Process(target=f,
                                            args=(qin, qout, clk_freq, init_x))

    _proc.start()

    def cleanup_event(sim):
        qin.put((None, None))

        if not qout.empty():
            qout.get_nowait()

        if not registry('sim/exception'):
            _proc.join()
        else:
            _proc.terminate()

    def cleanup_setup(_):
        registry('sim/simulator').events['after_cleanup'].append(cleanup_event)

    actuator(x, qin=qin, clk_freq=clk_freq, init=init_x)

    return sensor(qout=qout, sim_setup=cleanup_setup)
