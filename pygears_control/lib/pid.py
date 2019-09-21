from control.matlab import tf, parallel
from pygears import Intf, gear
from pygears.lib import dreg, decouple


def integral(Ki):
    return tf([Ki], [1, 0])


def prop(Kp):
    return tf([Kp], [1])


def deriv(Kd, N_filt=0):
    return tf([Kd, 0], [1]) * lp_filt(N_filt)


def lp_filt(N):
    return tf([N], [1, N])


def pidtf(Kp, Ki=0, Kd=0, N_filt=0):
    assert Kp != 0, "Proportional parameter must be greater than zero"

    p = prop(Kp)
    i = integral(Ki)
    d = deriv(Kd, N_filt)

    return parallel(p, i, d)


@gear
def hdl_p(din, *, Kp):
    dout = din * Kp
    return dout


@gear(hdl={'compile': True, 'inline_conditions': True})
async def hls_i(din, *, Ki) -> b'din*bitw(Ki)*10':
    acc = (din.dtype * type(Ki) * 10)(0)
    while True:
        async with din as data:
            mult = data * Ki
            acc = acc + mult
            yield acc


@gear(hdl={'compile': True, 'inline_conditions': True})
async def hls_d(din, *, Kd) -> b'din*bitw(Kd)*10':
    dly = (din.dtype * type(Kd) * 10)(0)

    while True:
        async with din as data:
            gain = data * Kd
            sub_s = gain - dly
            dly = gain
            yield sub_s


@gear
def hdl_i(din, *, Ki):
    din = din * Ki
    y = Intf(din.dtype * type(Ki) * 10)
    acc = y | decouple(init=0)
    y |= (acc + din)
    return y


@gear
def hdl_d(din, *, Kd):
    din = din * Kd
    acc = din | dreg(init=0)
    return din - acc


@gear
def hdl_pid(din, *, Kp, Ki, Kd):
    p = din | hdl_p(Kp=Kp)
    i = din | hdl_i(Ki=Ki)
    d = din | hdl_d(Kd=Kd)

    return p + i + d

@gear
def hls_pid(din, *, Kp, Ki, Kd):
    p = din | hdl_p(Kp=Kp)
    i = din | hls_i(Ki=Ki)
    d = din | hls_d(Kd=Kd)

    return p + i + d
