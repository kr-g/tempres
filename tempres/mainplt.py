import datetime as dt

try:
    from maindb import configure_engine, qry_all
except:
    from tempres.maindb import configure_engine, qry_all

import matplotlib.pyplot as plt

import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU

import numpy as np


def main_func(rec_stdout=False):

    engine = configure_engine()
    # dump_all(engine,full=True)

    recs = list(qry_all(engine, full=True))
    recs = sorted(recs, key=lambda x: x.time_stamp)

    if rec_stdout:
        for r in recs:
            print(r)

    # x = list(map(lambda x: x.time_stamp, recs))

    x = np.array(list(map(lambda x: dt.datetime.fromtimestamp(x.time_stamp), recs)))

    yt = list(map(lambda y: y.temperature, recs))
    yp = list(map(lambda y: y.pressure, recs))

    fig, ax = plt.subplots()
    fig.suptitle("temperature and pressure over time")

    ax.grid(True)
    ax2 = ax.twinx()

    locator = mdates.AutoDateLocator()
    locator.intervald[mdates.HOURLY] = [3]

    formatter = mdates.AutoDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    sz = 5

    rc1 = ax.scatter(x, yt, s=sz, c="C1")
    # (l1,) = rc # for plot
    ax.set_ylabel("temperature [°C]")

    rc2 = ax2.scatter(x, yp, s=sz, c="C0")
    # (l2,) = rc # for plot
    ax2.set_ylabel("pressure [hPa]")

    ax2.legend([rc1, rc2], ["temperature", "pressure"])
    # ax2.legend([l1, l2], ["temperature", "pressure"]) # for plot

    plt.show()


if __name__ == "__main__":
    main_func()
