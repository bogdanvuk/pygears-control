from pygears.typing import Float

from pygears import gear, module, GearDone, config, registry
from pygears.sim import timestep

import multiprocessing
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def plot_process(qin, clk_freq, title=None):

    fig, ax = plt.subplots()

    if title:
        plt.title(title)

    line, = ax.plot([], [], lw=2)
    ax.grid()
    ax.set_xlim(0, 100 / clk_freq)
    xdata, ydata = [], []
    yrng = [0, 0]
    done = []

    class CustFuncAnimation(animation.FuncAnimation):
        def _init_draw(self):
            try:
                super()._init_draw()
            except StopIteration:
                super()._draw_frame(tuple(yrng))

    def data_gen():
        while True:
            while True:
                if done:
                    return

                res = qin.get()

                if res is None:
                    done.append(True)
                    break

                t, y = res

                xdata.append(t)
                ydata.append(y)

                if y > yrng[1]:
                    yrng[1] = y

                if y < yrng[0]:
                    yrng[0] = y

                if qin.empty():
                    break

            yield tuple(yrng)

            if res is None:
                break

    def run(yrng):
        t = xdata[-1]
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        redraw = bool(done)
        if (t >= xmax):
            ax.set_xlim(xmin, 1.5 * t)
            redraw = True

        if (ymax < yrng[1] * 1.1) or (ymin > yrng[0]):
            ax.set_ylim(yrng[0], yrng[1] * 1.1)
            redraw = True

        if redraw:
            ax.figure.canvas.draw()

        line.set_data(xdata, ydata)

        return line,

    _ = CustFuncAnimation(fig,
                          run,
                          data_gen,
                          blit=True,
                          interval=100,
                          repeat=False)

    plt.show()


@gear
async def scope(x: Float, *, clk_freq=None, title=None):

    if clk_freq is None:
        clk_freq = config['sim/clk_freq']

    qin = multiprocessing.Queue(maxsize=10000)

    if title is None:
        title = module().name

    _proc = multiprocessing.context.Process(target=plot_process,
                                            args=(qin, clk_freq, title))
    _proc.start()

    registry('sim/simulator').events['after_cleanup'].append(lambda sim: _proc.
                                                             join())

    try:
        while True:
            async with x as x_data:
                qin.put((timestep() / clk_freq, x_data))
    except GearDone:
        qin.put(None)
        raise GearDone
