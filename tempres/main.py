import os
import time
import json
import argparse
from datetime import datetime, date, time

from urllib import request

from tempres import VERSION


def main_func():

    trace = False
    debug = False

    parser = argparse.ArgumentParser(
        prog="tempres",
        usage="python3 -m %(prog)s [DEVICE-PARAMETER] [options]",
        description="collect temperature and pressure data",
    )
    parser.add_argument(
        "-v",
        "--version",
        dest="show_version",
        action="store_true",
        help="show version info and exit",
        default=False,
    )

    parser.add_argument(
        "-trace",
        "-t",
        dest="trace",
        action="store_true",
        help="display trace info (default: %(default)s)",
        default=trace,
    )
    parser.add_argument(
        "-debug",
        "-d",
        dest="debug",
        action="store_true",
        help="display debug info (default: %(default)s)",
        default=debug,
    )

    parser.add_argument(
        "-host",
        "-ip",
        type=str,
        dest="host_ip",
        action="store",
        metavar="IP",
        help="ip adress to use (default: %(default)s)",
    )
    parser.add_argument(
        "-port",
        "-p",
        type=str,
        dest="host_port",
        action="store",
        metavar="PORT",
        help="ip port to use (default: %(default)s)",
        default=80,
    )
    parser.add_argument(
        "-url",
        type=str,
        dest="host_url",
        action="store",
        metavar="URL",
        help="url to use (default: %(default)s)",
        default="/tempr/measure",
    )

    global args
    args = parser.parse_args()

    if args.debug:
        print("arguments", args)

    debug = args.debug
    trace = args.trace

    if args.show_version:
        print("Version:", VERSION)
        return

    data = fetch(args)

    tm = data["time"]
    d = date(*tm[0:3])
    t = time(*tm[3:])
    dt = datetime.combine(d, t)

    fnam = f"tempres-{dt.year:04}{dt.month:02}{dt.day:02}-{dt.hour:02}{dt.minute:02}{dt.second:02}.json"

    print("writing to", fnam)


def fetch(args):
    url = f"http://{args.host_ip}:{args.host_port}{args.host_url}"
    print("loading from", url)
    resp = request.urlopen(url)

    print("status", resp.status)

    headers = resp.getheaders()
    print("headers", headers)

    data = resp.read().decode()
    print("data", data)

    data = json.loads(data)
    print("parsed data", data)

    return data
