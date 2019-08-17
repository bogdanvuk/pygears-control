from pygears import GearDone, gear
from scipy.integrate import solve_ivp
from pygears.typing import Float
from .continuous import continuous


def cont_wrap(f, qin, qout, init):
    def wrap(t, y):
        dy = f(t, y, wrap.x)

        if isinstance(dy, tuple):
            outp = dy[0]
            dy = dy[1]
        else:
            outp = y

        if t < wrap.t:
            return dy

        if wrap.done_out:
            raise GearDone

        if qout.empty():
            qout.put(outp)

        wrap.x = wrap.next_x
        wrap.next_x, wrap.t = qin.get()

        if wrap.t is None:
            raise GearDone

        return dy

    wrap.x = init
    wrap.next_x = init
    wrap.t = 0
    wrap.done_out = False

    return wrap


@gear
def ode(x: Float, *, f, init_y, init_x, clk_freq=None) -> Float:
    def thread_function(qin, qout, clk_freq, init_x):
        try:
            f_wrap = cont_wrap(f, qin, qout, init_x)
            solve_ivp(f_wrap, [0, float('inf')],
                      init_y,
                      max_step=1 / (2 * clk_freq),
                      first_step=1 / (2 * clk_freq))
        except GearDone:
            pass

    return continuous(x, f=thread_function, init_x=init_x, clk_freq=clk_freq)
