from pygears import gear, alternative
from scipy import signal
from pygears.typing import Float
import numpy as np
from .ode import ode


@gear
def lti(x: Float, *, num, den, init_x, init_y=None, clk_freq=None) -> Float:
    tf = signal.TransferFunction(num, den)
    ss = tf.to_ss()
    n_states = ss.A.shape[0]
    # n_inputs = ss.B.shape[1]
    # n_outputs = ss.C.shape[0]

    if init_y is None:
        init_y = [0] * n_states

    def lti_ode(t, y, x):
        res = ss.A @ np.vstack(y) + ss.B * x
        res.shape = (res.shape[0], )
        return float(np.dot(ss.C, y) + ss.D*x), res

    return ode(x, f=lti_ode, init_y=init_y, init_x=init_x, clk_freq=clk_freq)


@alternative(lti)
@gear
def lti_ctrl(x: Float, *, sys, init_x, init_y=None, clk_freq=None) -> Float:

    return lti(x,
               num=sys.num[0][0],
               den=sys.den[0][0],
               init_x=init_x,
               init_y=init_y,
               clk_freq=clk_freq)
