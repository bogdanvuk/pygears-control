from pygears.lib import drv
from pygears import gear
from pygears.typing import Fixp
from pygears import gear
from pygears.typing import Queue
from pygears.lib import drv, flatten
from pygears.sim.modules.verilator import SimVerilated
from pygears_control.lib import scope
from pygears.typing import Float
from pygears.sim import sim

from pygears.conf.registry import bind
from pygears.lib import shred
bind('hdl/debug_intfs', ['*'])


@gear(hdl={'compile': True, 'inline_conditions': True})
async def accum(din: Queue[Fixp[5, 10], 1]) -> Queue[Fixp[12, 17], 1]:
    acc = Fixp[12, 17](0)
    async for (data, eot) in din:
        acc = acc + data
        yield (acc, eot)


seq = [0.] * 2 + [1.125] * 1000

drv(t=Queue[Fixp[5, 10], 1], seq=[seq]) \
    | accum(sim_cls=SimVerilated) \
    | flatten \
    | Float \
    | scope(clk_freq=1)

sim('/tools/home/tmp')
