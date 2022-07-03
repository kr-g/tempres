import sys

import time
import json
import argparse

from urllib.request import urlopen

from pyjsoncfg import Config

VERSION = "v0.0.0.1"

DEFAULT_PATH = "~/.tempres/"

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


def register_update_station(station_id, name, lat, lon, alt, api_key):

    raise Exception("untested")

    stations = request_stations(api_key, station_id, False)
    update = len(stations) > 0

    data = {
        "external_id": station_id,
        "name": name,
        "latitude": lat,
        "longitude": lon,
    }
    if alt is not None:
        data.update({"altitude": alt})

    id = stations[0]["id"] if len(stations) > 0 else None

    data = json.dumps(data)
    url = build_station_url(api_key, id)
    resp = urlopen(url, data=data, method="POST" if update is False else None)
    if resp.status != 204:
        raise Exception(f"failed to load {url} with error {resp.status}")
    return resp


def delele_station(station_id, api_key):

    raise Exception("untested")

    stations = request_stations(api_key, station_id, False)
    url = build_station_url(api_key, station_id)
    resp = urlopen(url, data=data, method="DELETE")
    if resp.status != 200:
        raise Exception(f"failed to load {url} with error {resp.status}")
    return resp


#


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
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {VERSION}",
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
        help="returns raw data  (default: %(default)s)",
        default=False,
    )

    list_group = parser.add_argument_group("list", "list options")
    list_group.add_argument(
        "-list-stations",
        "-ls",
        dest="station_list",
        action="store_true",
        help="list all stations, or station with '-id'",
        default=False,
    )
    list_group.add_argument(
        "-is-owm-id",
        "-isid",
        dest="station_no_ext_id",
        action="store_true",
        help="true if id is open weather map id, or station_id from config file (default: %(default)s)",
        default=False,
    )

    global args
    args = parser.parse_args()

    if args.debug:
        print("arguments", args)

    debug = args.debug

    cfg = read_conf()
    cfg_ = cfg()

    api_key = args.api_key if args.api_key is not None else cfg_.api_key
    debug and print("api_key", api_key)

    if args.station_list:
        rc = request_stations(api_key, args.station_id, not args.station_no_ext_id)
        print(rc)
        return

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
