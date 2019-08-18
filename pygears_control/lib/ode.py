from pygears import GearDone, gear, module
from scipy.integrate import solve_ivp
from pygears.typing import Float
from .continuous import continuous
from collections import deque


def cont_wrap(f, qin, qout, init, m):
    def wrap(t, y):
        x = wrap.x

        # Sometimes ODE solver might go into the past trying to improve the
        # accuracy. In that case we need to dig the appropriate set of inputs
        # for that moment in time
        if wrap.hist and t < wrap.hist[-1][1]:
            for i in range(-2, -len(wrap.hist), -1):
                if t >= wrap.hist[i][1]:
                    x = wrap.hist[i+1][0]
                    break
            else:
                x = init

        dy = f(t, y, x)

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

        wrap.hist.append((wrap.x, wrap.t))
        wrap.x, wrap.t = qin.get()

        if wrap.t is None:
            raise GearDone

        return dy

    wrap.hist = deque([], 10)
    wrap.x = init
    wrap.next_x = init
    wrap.t = 0
    wrap.done_out = False

    return wrap


@gear
def ode(x: Float, *, f, init_y, init_x, clk_freq=None) -> Float:
    def thread_function(qin, qout, clk_freq, init_x):
        try:
            f_wrap = cont_wrap(f, qin, qout, init_x, module())
            solve_ivp(f_wrap, [0, float('inf')],
                      init_y,
                      max_step=1 / (2 * clk_freq),
                      first_step=1 / (2 * clk_freq))
        except GearDone:
            pass

    return continuous(x,
                      f=thread_function,
                      init_x=float(init_x),
                      clk_freq=clk_freq)
