from pygears_control.lib import pidtf
from control.matlab import feedback, tf

from pygears.typing import Float
from pygears.lib import drv, scoreboard
from pygears_control.lib import lti, scope
from pygears.sim import sim
from pygears import Intf, config, gear, find

# import matplotlib
# matplotlib.use('GTK3Cairo', warn=False, force=True)


@gear
def pid_lti_comb(set_point, *, Kp, Ki, Kd, Nfilt, plant):
    pid = pidtf(Kp, Ki, Kd, Nfilt)
    sys = plant * pid

    plant_out = Intf(Float)

    pid_in = set_point - plant_out

    plant_out |= pid_in \
        | lti(sys=sys, init_x=0) \

    return plant_out


@gear
def pid_pg_comb(set_point, *, Kp, Ki, Kd, Nfilt, plant):
    pid = pidtf(Kp, Ki, Kd, Nfilt)

    plant_out = Intf(Float)

    pid_in = set_point - plant_out

    pid_out = pid_in \
        | lti(name='pid', sys=pid, init_x=0)

    plant_out |= pid_out \
        | lti(name='plant', sys=plant, init_x=0)

    return plant_out


@gear
def pid_lti_feedback(set_point, *, Kp, Ki, Kd, Nfilt, plant):
    pid = pidtf(Kp, Ki, Kd, Nfilt)
    plant = tf([1], [1, 10, 20])

    sys = feedback(pid * plant)

    return set_point | lti(sys=sys, init_x=0)


def sim_pid_pg_comb(Kp, Ki, Kd, Nfilt):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | pid_pg_comb(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    find('/pid_pg_comb/pid.x').producer | scope(title="PID Input")
    find('/pid_pg_comb/pid.dout').consumer | scope(title="PID Output")
    plant_out | scope(title="Plant Output")

    sim(timeout=len(seq))


def sim_pid_lti_comb(Kp, Ki, Kd, Nfilt):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | pid_lti_comb(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    find('/pid_lti_comb/lti.x').producer | scope(title="PID Input")
    plant_out | scope(title="Plant Output")

    sim(timeout=len(seq))


def sim_pid_lti_feedback(Kp, Ki, Kd, Nfilt):
    config['sim/clk_freq'] = 1000

    plant = tf([1], [1, 10, 20])

    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    drv(t=Float, seq=seq) \
        | pid_lti_feedback(Kp=Kp, Ki=Ki, Kd=Kd, plant=plant) \
        | scope

    sim(timeout=len(seq))


def comp_pid_lti_comb_ref(Kp, Ki, Kd, Nfilt):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | pid_lti_comb(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    plant_out | scope(title="Plant Output")

    ref_out = set_point \
        | pid_lti_feedback(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    ref_out | scope(title="Continuous Reference")

    report = []
    scoreboard(plant_out, ref_out, report=report, tolerance=2e-2)

    sim(timeout=len(seq))


def comp_pid_pg_comb_ref(Kp, Ki, Kd, Nfilt):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | pid_pg_comb(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    find('/pid_pg_comb/pid.x').producer | scope(title="PID Input")
    find('/pid_pg_comb/pid.dout').consumer | scope(title="PID Output")
    plant_out | scope(title="Plant Output")

    ref_out = set_point \
        | pid_lti_feedback(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    ref_out | scope(title="Continuous Reference")

    report = []
    scoreboard(plant_out, ref_out, report=report, tolerance=5e-2)

    sim(timeout=len(seq))


def comp_pid_pg_comb_lti_comb(Kp, Ki, Kd, Nfilt):
    plant = tf([1], [1, 10, 20])

    config['sim/clk_freq'] = 1000
    seq = [0.] * 2 + [1.] * config['sim/clk_freq']

    set_point = drv(t=Float, seq=seq)

    plant_out = set_point \
        | pid_pg_comb(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    find('/pid_pg_comb/pid.x').producer | scope(title="PID Input")
    find('/pid_pg_comb/pid.dout').consumer | scope(title="PID Output")
    plant_out | scope(title="Plant Output")

    ref_out = set_point \
        | pid_lti_comb(Kp=Kp, Ki=Ki, Kd=Kd, Nfilt=Nfilt, plant=plant)

    ref_out | scope(title="Continuous Reference")

    report = []
    scoreboard(plant_out, ref_out, report=report, tolerance=2e-2)

    sim(timeout=len(seq))


def test_pid_lti_comb_ref():
    comp_pid_lti_comb_ref(350, 300, 50, 100)


def test_pid_pg_comb_ref():
    comp_pid_pg_comb_ref(350, 300, 50, 100)


def test_pid_pg_comb_lti_comb():
    comp_pid_pg_comb_lti_comb(350, 300, 50, 100)


test_pid_pg_comb_lti_comb()
