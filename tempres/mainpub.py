import sys

import time
import json
import argparse

from urllib.request import urlopen

from pyjsoncfg import Config

DEFAULT_PATH = "~/.tempres/"

CONFIG_FNAM = "stations.json"

BASE_URL = "http://api.openweathermap.org"
GEO_VER = "1.0"
DATA_VER = "2.5"


def read_conf():
    cfg = Config(filename=CONFIG_FNAM, basepath=DEFAULT_PATH)
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


debug = False


def main_func():

    global debug

    parser = argparse.ArgumentParser(
        prog="temprespub",
        usage="python3 -m %(prog)s [options]",
        description="interface to OpenWeatherMap",
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
        "-api-key",
        "-app",
        dest="api_key",
        action="store",
        type=str,
        help="api key",
        default=None,
    )

    parser.add_argument(
        "-station",
        "-id",
        dest="station_id",
        action="store",
        type=str,
        help="name of station",
        default=None,
    )

    parser.add_argument(
        "-load",
        "-get",
        dest="load",
        action="store_true",
        help="load current data from station",
        default=False,
    )

    parser.add_argument(
        "-raw",
        dest="raw",
        action="store_true",
        help="returns raw data",
        default=False,
    )

    global args
    args = parser.parse_args()

    if args.debug:
        print("arguments", args)

    debug = args.debug

    if args.show_version:
        print("Version:", "not-yet")
        return

    cfg = read_conf()
    cfg_ = cfg()

    api_key = args.api_key if args.api_key is not None else cfg_.api_key
    debug and print("api_key", api_key)

    st = list(filter(lambda x: x.station_id == args.station_id, cfg_.stations))
    debug and print(st)

    try:
        if len(st) > 1:
            raise Exception("duplicate station_id")
        st = st[0]
    except Exception as ex:
        print(f"station {args.station_id} not found", ex)
        sys.exit(1)

    try:
        lat, lon = st.lat, st.lon
    except:
        lat, lon = request_zip_lat_lon(st.zip_code, st.country_code, api_key)

    debug and print(f"station lat: {lat}, lon: {lon}")

    if args.load:

        url = build_lat_lon_url(lat, lon, api_key)
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
            res.update(
                {"temperature": current["temp"], "pressure": current["pressure"]}
            )
        else:
            res.update({"data": jso})

        print(res)

    # todo add save with tag (same filename and folder structure as tempres.main)


if __name__ == "__main__":

    main_func()
