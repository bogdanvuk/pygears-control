from pygears import config
from pygears.sim import SimPlugin


class ContinuousSimPlugin(SimPlugin):
    @classmethod
    def bind(cls):
        config.define('sim/clk_freq', default=1e6)
