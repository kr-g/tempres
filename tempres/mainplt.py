import datetime as dt

try:
    from maindb import configure_engine, qry_all
except:
    from tempres.maindb import configure_engine, qry_all

import matplotlib.pyplot as plt

import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU

import numpy as np


def main_func():

    engine = configure_engine()
    # dump_all(engine,full=True)

    recs = list(qry_all(engine, full=True))
    recs = sorted(recs, key=lambda x: x.time_stamp)

    for r in recs:
        print(r)

    # x = list(map(lambda x: x.time_stamp, recs))

    x = np.array(list(map(lambda x: dt.datetime.fromtimestamp(x.time_stamp), recs)))

    yt = list(map(lambda y: y.temperature, recs))
    yp = list(map(lambda y: y.pressure, recs))

    fig, ax = plt.subplots()

    ax.grid(True)
    ax2 = ax.twinx()

    locator = mdates.AutoDateLocator()
    locator.intervald[mdates.HOURLY] = [3]

    formatter = mdates.AutoDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    (l1,) = ax.plot(x, yt, "C1")

    (l2,) = ax2.plot(
        x,
        yp,
    )
    ax2.legend([l1, l2], ["temperature", "pressure"])

    plt.show()


if __name__ == "__main__":
    main_func()
