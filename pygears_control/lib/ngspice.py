from pygears import GearDone, gear
from pygears.typing import Float
from .continuous import continuous
import multiprocessing as mp
from collections import deque
from pygears.sim import timestep

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.NgSpice.Shared import NgSpiceShared


class PgNgSpice(NgSpiceShared):
    def __init__(self, qin, qout, x, outs, **kwargs):

        super().__init__(**kwargs)

        self._qin = qin
        self._qout = qout
        self._x = x
        self._init = x
        self._t = 0
        self._initial = True
        self._outs = outs
        self._hist = deque([], 10)

    # @staticmethod
    # def _send_data(data, number_of_vectors, ngspice_id, user_data):
    #     breakpoint()
    #     return NgSpiceShared._send_data(data, number_of_vectors, ngspice_id,
    #                                     user_data)

    @staticmethod
    def _send_char(message_c, ngspice_id, user_data):
        return 0

    def run(self, background=False):
        while self._t is not None:
            self.step(10)

    def send_data(self, actual_vector_values, number_of_vectors, ngspice_id):
        self._initial = False

        if self._outs[0][1] == 0:
            neg = 0
        else:
            neg = actual_vector_values[self._outs[0][1]].real

        try:
            self._qout.put_nowait(actual_vector_values[self._outs[0][0]].real -
                                  neg)
        except mp.queues.Full:
            pass

        return 0

    def get_vsrc_data(self, voltage, t, node, ngspice_id):
        x = self._x

        # Sometimes ODE solver might go into the past trying to improve the
        # accuracy. In that case we need to dig the appropriate set of inputs
        # for that moment in time
        if self._hist and t < self._hist[-1][1]:
            for i in range(-2, -len(self._hist), -1):
                if t >= self._hist[i][1]:
                    x = self._hist[i + 1][0]
                    break
            else:
                x = self._init

        voltage[0] = x

        if self._t is None:
            return 0

        if (t < self._t) or (self._initial):
            return 0

        self._hist.append((self._x, self._t))
        self._x, self._t = self._qin.get()

        return 0


@gear
def ngspice(x: Float, *, f, init_x, clk_freq=None) -> Float:
    def thread_function(qin, qout, clk_freq, init_x):
        try:

            c = Circuit('pygears')
            ins = []
            outs = []
            f(c, ins, outs)

            c.V('__x', ins[0][0], ins[0][1], f'dc {init_x} external')

            ngspice_shared = PgNgSpice(qin,
                                       qout,
                                       x=init_x,
                                       outs=outs,
                                       send_data=True)

            simulator = c.simulator(temperature=25,
                                    nominal_temperature=25,
                                    simulator='ngspice-shared',
                                    ngspice_shared=ngspice_shared)

            simulator.transient(step_time=1 / (2 * clk_freq), end_time=1e3)
        except GearDone:
            pass

    return continuous(x, f=thread_function, init_x=init_x, clk_freq=clk_freq)
