import os
import time

from datetime import datetime, date
from datetime import time as dt_time


def build_timed_path_fnam(
    time_=None,
    tm=None,
    dest_dir=".",
    prefix=None,
    sep="-",
    fnam=None,
    postfix=None,
    ext="",
    incl_stamp=False,
    utc=True,
):

    if time_ is None:
        time_ = time.time()

    if tm is None:
        tm = time.gmtime(time_) if utc else time.localtime(time_)
    else:
        tm = list(tm)

    d = date(*tm[0:3])
    t = dt_time(*tm[3:6])
    dt = datetime.combine(d, t)

    prefix = prefix + sep if prefix is not None else ""
    t_stamp = sep + str(time_).replace(".", "_") if incl_stamp else ""
    fnam = sep + fnam if fnam is not None else ""
    postfix = sep + postfix if postfix is not None else ""

    fnam = (
        f"{prefix}{dt.year:04}{dt.month:02}{dt.day:02}{sep}"
        + f"{dt.hour:02}{dt.minute:02}{dt.second:02}"
        + f"{t_stamp}{fnam}{postfix}{ext}"
    )

    dest_dir = os.path.expanduser(dest_dir)
    dest_dir = os.path.expandvars(dest_dir)

    dest_dir = os.path.join(
        dest_dir,
        f"{dt.year:04}{os.sep}{dt.month:02}",
        f"{dt.year:04}{dt.month:02}{dt.day:02}",
    )

    return dest_dir, fnam


def combine2(path, fnam):
    return os.path.join(path, fnam)


def combine(path_fnam):
    return combine2(*path_fnam)
