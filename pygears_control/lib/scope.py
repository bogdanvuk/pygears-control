from pygears.typing import Float

from pygears import gear, module, GearDone, config
from pygears.sim import timestep

import queue
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def plot_thread(qin, clk_freq):

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)
    ax.grid()
    ax.set_xlim(0, 10 / clk_freq)
    xdata, ydata = [], []

    def data_gen():
        ymax = 0
        ymin = 0

        while True:
            while True:
                res = qin.get()

                if res is None:
                    break

                t, y = res

                xdata.append(t)
                ydata.append(y)

                if y > ymax:
                    ymax = y

                if y < ymin:
                    ymin = y

                if qin.empty():
                    break

            yield (ymax, ymin)

            if res is None:
                break

    def run(data):
        t = xdata[-1]
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        redraw = False
        if (t >= xmax):
            ax.set_xlim(xmin, 1.5 * t)
            redraw = True

        if (ymax < data[0] * 1.1) or (ymin > data[1]):
            ax.set_ylim(data[1], data[0] * 1.1)
            redraw = True

        if redraw:
            ax.figure.canvas.draw()

        line.set_data(xdata, ydata)

        return line,

    ani = animation.FuncAnimation(fig,
                                  run,
                                  data_gen,
                                  blit=True,
                                  interval=100,
                                  repeat=False)

    plt.show()


@gear
async def scope(x: Float, *, clk_freq=None):

    if clk_freq is None:
        clk_freq = config['sim/clk_freq']

    qin = queue.Queue(maxsize=1000)

    module()._thrd = threading.Thread(target=plot_thread, args=(qin, clk_freq))
    module()._thrd.start()

    try:
        while True:
            async with x as x_data:
                qin.put((timestep() / clk_freq, x_data))
    except GearDone:
        qin.put(None)
        module()._thrd.join()
        raise GearDone
