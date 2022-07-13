import os
import sys
import time
import json
import argparse
from datetime import datetime, date
from datetime import time as dt_time

from urllib import request

from const import VERSION, DEFAULT_PATH

debug = False


def main_func():

    global debug

    parser = argparse.ArgumentParser(
        prog="tempres",
        usage="python3 -m %(prog)s [options]",
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
        "-debug",
        "-d",
        dest="debug",
        action="store_true",
        help="display debug info (default: %(default)s)",
        default=debug,
    )
    parser.add_argument(
        "-proto",
        type=str,
        dest="host_proto",
        action="store",
        metavar="HTTP/S",
        help="protocol to use (default: %(default)s)",
        default="http",
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
        help="url to use (default: %(default)s). use '/tempr/pop' to read from internal storage instead of instant measure.",
        default="/tempr/measure",
    )
    parser.add_argument(
        "-dest",
        type=str,
        dest="dest_dir",
        action="store",
        metavar="DIR",
        help="destination folder (default: %(default)s)",
        default=DEFAULT_PATH,
    )
    parser.add_argument(
        "-flat-dir",
        "-flat",
        dest="flat_store",
        action="store_true",
        help="use a flat directory structure in the destination folder instead grouped like YYYY/MM/YYYYMMDD/...",
        default=False,
    )
    parser.add_argument(
        "-nostore",
        "-no-store",
        "-stdout",
        "-",
        dest="no_store",
        action="store_true",
        help="output to stdout",
        default=False,
    )

    global args
    args = parser.parse_args()

    if args.debug:
        print("arguments", args)

    debug = args.debug

    if args.show_version:
        print("Version:", VERSION)
        return

    if args.host_ip is None:
        print("error", "no host specified")
        sys.exit(1)

    data = fetch(args)

    if "err" in data:
        print("error", data)
        sys.exit(1)

    tm = data["time"]
    d = date(*tm[0:3])
    t = dt_time(*tm[3:])
    dt = datetime.combine(d, t)

    data["time_ux"] = dt.timestamp()

    fnam = f"tempres-{dt.year:04}{dt.month:02}{dt.day:02}-{dt.hour:02}{dt.minute:02}{dt.second:02}.json"

    dest_dir = os.path.expanduser(args.dest_dir)
    dest_dir = os.path.expandvars(dest_dir)

    if not args.flat_store:
        dest_dir = os.path.join(
            dest_dir,
            f"{dt.year:04}{os.sep}{dt.month:02}{os.sep}{dt.year:04}{dt.month:02}{dt.day:02}",
        )

    if not args.no_store:
        debug and print("create dest folder", dest_dir)
        os.makedirs(dest_dir, exist_ok=True)

    dest_fnam = os.path.join(dest_dir, fnam)
    debug and print("dest file", dest_fnam)

    if args.no_store:
        print(data)
    else:
        outs = json.dumps(data, indent=4)
        debug and print("writing to", dest_fnam, outs)
        with open(dest_fnam, "w") as f:
            f.write(outs)


def fetch(args):
    url = f"{args.host_proto}://{args.host_ip}:{args.host_port}{args.host_url}"

    debug and print("loading from", url)
    resp = request.urlopen(url)

    debug and print("status", resp.status)

    headers = resp.getheaders()
    debug and print("headers", headers)

    data = resp.read().decode()
    debug and print("data", data)

    data = json.loads(data)
    debug and print("parsed data", data)

    return data
