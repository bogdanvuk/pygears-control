from pygears import GearDone, gear
from pygears.typing import Float
from .continuous import continuous

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.NgSpice.Shared import NgSpiceShared


class PgNgSpice(NgSpiceShared):
    def __init__(self, qin, qout, x, outs, **kwargs):

        super().__init__(**kwargs)

        self._qin = qin
        self._qout = qout
        self._x = x
        self._next_x = x
        self._t = 0
        self._initial = True
        self._outs = outs

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
        if self._qout.empty():
            if self._outs[0][1] == 0:
                neg = 0
            else:
                neg = actual_vector_values[self._outs[0][1]].real

            self._qout.put(actual_vector_values[self._outs[0][0]].real - neg)

        return 0

    def get_vsrc_data(self, voltage, time, node, ngspice_id):

        if self._t is None:
            return 0

        # print(f'Request v for {node}@{time} for {ngspice_id}')
        if (time < self._t) or (self._initial):
            voltage[0] = self._x
            return 0

        self._x = self._next_x
        self._next_x, self._t = self._qin.get()

        voltage[0] = self._x
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
