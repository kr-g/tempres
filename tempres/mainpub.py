import sys

import time
import json
import argparse

from urllib.request import urlopen, Request

from pyjsoncfg import Config  # , Namespace

from const import VERSION, DEFAULT_PATH

CONFIG_FNAM = "stations.json"

BASE_URL = "http://api.openweathermap.org"
GEO_VER = "1.0"
DATA_VER = "2.5"
STATION_VER = "3.0"

#


def build_station_url(api_key, station_id=None):
    if station_id is None:
        station_id = ""
    else:
        station_id = "/" + station_id
    return f"{BASE_URL}/data/{STATION_VER}/stations{station_id}?appid={api_key}"


# def build_push_station_url():
#     return f"{BASE_URL}/data/{STATION_VER}/measurements?appid={api_key}"

# api doc
# https://openweathermap.org/stations
def request_stations(api_key, station_id=None, is_ext_id=True):
    url = build_station_url(api_key, station_id if not is_ext_id else None)
    debug and print("url", url)
    resp = urlopen(url)
    if resp.status != 200:
        raise Exception(f"failed to load {url} with error {resp.status}")
    cont = resp.read()
    jso = json.loads(cont)
    if station_id and is_ext_id:
        jso = list(filter(lambda x: x["external_id"] == station_id, jso))
    return jso


def register_update_station(station_id, x_station_id, name, lat, lon, alt, api_key):

    update = station_id is not None

    data = {
        "external_id": x_station_id,
        "name": name,
        "latitude": lat,
        "longitude": lon,
    }
    if alt is not None:
        data.update({"altitude": alt})

    id = station_id if update else None

    data = json.dumps(data).encode()

    url = build_station_url(api_key, id)

    meth = "PUT" if update else "POST"
    print(meth, url)

    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=meth,
    )
    resp = urlopen(req)
    if not (resp.status >= 200 and resp.status < 300):
        raise Exception(f"failed to load {url} with error {resp.status}")
    return resp


def delele_station(station_id, api_key):
    print("delete", station_id)

    url = build_station_url(api_key, station_id)
    print("delete", url)
    req = Request(url, method="DELETE")
    resp = urlopen(req)
    if not (resp.status >= 200 and resp.status < 300):
        raise Exception(f"failed to load {url} with error {resp.status}")
    return resp


#


def read_conf():
    cfg = Config(
        filename=CONFIG_FNAM,
        basepath=DEFAULT_PATH,
    )
    debug and print("config", cfg())
    return cfg


def build_zip_url(zip_code, country_code, api_key):
    return f"{BASE_URL}/geo/{GEO_VER}/zip?zip={zip_code},{country_code}&appid={api_key}"


def request_zip_lat_lon(zip_code, country_code, api_key):
    url = build_zip_url(zip_code, country_code, api_key)
    resp = urlopen(url)
    if resp.status != 200:
        raise Exception(f"failed to load {url} with error {resp.status}")
    cont = resp.read()
    jso = json.loads(cont)
    return jso["lat"], jso["lon"]


def build_lat_lon_url(lat, lon, api_key, exclude_part=None):
    if exclude_part is not None:
        exclude_part = exclude_part.strip()
        if len(exclude_part) > 0:
            exclude_part = f"&exclude={exclude_part}"
    else:
        exclude_part = "&exclude=minutely,hourly,daily,alerts"
    return f"{BASE_URL}/data/{DATA_VER}/onecall?lat={lat}&lon={lon}{exclude_part}&units=metric&appid={api_key}"


def get_station(args, registered, xkey="external_id"):
    if args.station_id:
        res = list(filter(lambda x: x[xkey] == args.station_id, registered))
        if len(res) > 1:
            # looks strange, but ... since ...
            # external id is not checked to be unique during creation
            print("WARNING", "double entry", args.station_id)
            return res[0]
        return res[0] if len(res) == 1 else None


def remote_func(args):
    registered = request_stations(args.api_key)
    debug and print("stations", registered)

    # xkey = "external_id" if args.x_station_id else "id"
    station_id = get_station(args, registered, xkey="id") if args.station_id else None
    station_def = (
        get_station(args, registered, xkey="external_id") if args.station_id else None
    )

    station = station_def if station_def else station_id

    if args.station_list:
        res = registered
        if args.station_id:
            res = station
        print("remote", json.dumps(res, indent=4))
        return

    elif args.register_xid:
        myid = None
        if station and "id" in station:
            # read online
            myid = station["id"]
            print("found on openweathermap")

        station_cfg = get_station(args, args.cfg.stations, xkey="station_id")

        exid = station_cfg["station_id"]
        if "lat" not in station_cfg:
            lat, lon = request_zip_lat_lon(
                station_cfg.zip_code, station_cfg.country_code, args.api_key
            )
        else:
            lat = station_cfg["lat"]
            lon = station_cfg["lon"]

        name = station_cfg["name"]
        alt = station_cfg["alt"] if "alt" in station_cfg else None

        print("station", myid, "ref", exid, station)
        resp = register_update_station(myid, exid, name, lat, lon, alt, args.api_key)
        return resp.read().decode()

    elif args.unregister_xid:
        myid = None
        exid = None
        if station:
            # read online
            myid = station["id"] if "id" in station else None
        if myid is None:
            # read config
            station = get_station(args, args.cfg.stations, xkey="station_id")
            myid = station["id"] if "id" in station else None
        delele_station(myid, args.api_key)


#


def local_func(args):
    # registered = request_stations(args.api_key)
    # debug and print("stations", registered)

    if not args.x_station_id:
        raise Exception("only local stations with station_id as external_id supported")

    station_cfg = get_station(args, args.cfg.stations, xkey="station_id")

    exid = station_cfg["station_id"]
    if "lat" not in station_cfg:
        lat, lon = request_zip_lat_lon(
            station_cfg.zip_code, station_cfg.country_code, args.api_key
        )
    else:
        lat = station_cfg["lat"]
        lon = station_cfg["lon"]

    url = build_lat_lon_url(lat, lon, args.api_key)
    resp = urlopen(url)
    if resp.status != 200:
        raise Exception(f"failed to load {url} with error {resp.status}")

    cont = resp.read()
    jso = json.loads(cont)
    debug and print(jso)

    now = time.time()
    tm = list(time.gmtime(now))
    res = {
        "time": tm[0:6],
        "time_ux": now,
        "utc": True,
    }

    if args.raw is False:
        current = jso["current"]
        res.update({"temperature": current["temp"], "pressure": current["pressure"]})
    else:
        res.update({"data": jso})

    print(res)


#

debug = False

#


def main_func():

    global debug

    parser = argparse.ArgumentParser(
        prog="temprespub",
        usage="python3 -m %(prog)s [options]",
        description="interface to OpenWeatherMap",
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s {VERSION}"
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
        "-api-key",
        "-app",
        dest="api_key",
        action="store",
        type=str,
        help="api key",
        default=None,
    )

    #

    subparsers = parser.add_subparsers(help="sub-command --help")

    #

    remote_parser = subparsers.add_parser("remote", help="remote --help")
    remote_parser.set_defaults(func=remote_func)

    remote_parser.add_argument(
        "-register",
        "-reg",
        dest="register_xid",
        action="store_true",
        help="register station with station_id",
        default=False,
    )

    remote_parser.add_argument(
        "-unregister",
        "-unreg",
        "-del",
        dest="unregister_xid",
        action="store_true",
        help="unregister station with station_id",
        default=False,
    )

    remote_parser.add_argument(
        "-list",
        "-ls",
        dest="station_list",
        action="store_true",
        help="list stations, or station with '-id'",
        default=False,
    )

    remote_parser.add_argument(
        "-station",
        "-id",
        dest="station_id",
        metavar="ID",
        action="store",
        type=str,
        help="name of station",
        default=None,
    )

    remote_parser.add_argument(
        "-xstation",
        "-xid",
        dest="x_station_id",
        action="store_true",
        help="id is external id (default: %(default)s)",
        default=False,
    )

    remote_parser.add_argument(
        "-raw",
        dest="raw",
        action="store_true",
        help="returns raw data where possible (default: %(default)s)",
        default=False,
    )

    #

    local_parser = subparsers.add_parser("local", help="local --help")
    local_parser.set_defaults(func=local_func)

    local_parser.add_argument(
        "-load",
        "-get",
        dest="get_data",
        action="store_true",
        help="load data from station with station_id",
        default=False,
    )

    local_parser.add_argument(
        "-station",
        "-id",
        dest="station_id",
        metavar="ID",
        action="store",
        type=str,
        help="name of station",
        default=None,
    )

    local_parser.add_argument(
        "-xstation",
        "-xid",
        dest="x_station_id",
        action="store_true",
        help="id is external id (default: %(default)s)",
        default=False,
    )

    local_parser.add_argument(
        "-raw",
        dest="raw",
        action="store_true",
        help="returns raw data where possible (default: %(default)s)",
        default=False,
    )

    #

    global args
    args = parser.parse_args()

    debug = args.debug

    if args.debug:
        print("arguments", args)

    cfg_ = read_conf()
    cfg = cfg_()

    api_key = args.api_key if args.api_key is not None else cfg.api_key
    args.api_key = api_key
    debug and print("api_key", api_key)

    cfg = read_conf()
    cfg_ = cfg()

    args.cfg = cfg_

    if "func" in args:
        debug and print("call func", args.func.__name__)

        rc = args.func(args)
        debug and print(rc)

        rc = rc if rc != None else 0
        return rc


# todo add save with tag (same filename and folder structure as tempres.main)


if __name__ == "__main__":

    main_func()
