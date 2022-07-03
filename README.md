[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# tempres 

collect temperature and pressure data from a mpy-modcore device
running the `tempr` module


# what's new ?

Check
[`CHANGELOG`](https://github.com/kr-g/tempres/blob/main/CHANGELOG.md)
for latest ongoing, or upcoming news.


# limitations

Check 
[`BACKLOG`](https://github.com/kr-g/tempres/blob/main/BACKLOG.md)
for open development tasks and limitations.


# how to use

todo: documentation pending

following cmd-line tools are included in this package.


## tempres

`tempres` loads one data package from a device and stores it under `~/.tempres/inq` (default) as json.

use `tempres --help` to see all cmd-line options.


## tempresdb

imports the data from `~/.tempres/inq` into a sqlite db `~/.tempresdb`.

currently no further cmd-line options to configure the process (todo)


## tempresplt

plots the data "temperature and pressure data over time" from `~/.tempresdb` with mathplotlib.

currently no further cmd-line options to configure the process (todo)


## temprespub

interface to OpenWeatherMap.org 

- [one call api doc](https://openweathermap.org/api/one-call-3)
- [station api doc](https://openweathermap.org/stations#steps)


### cmd line parameters

todo documentation

### configuration

todo documentation

file `~/tempres/stations.json` 

    {
      "api_key" : "your-api-key",
      "stations" : [
        { 
          "station_id" : "your-id1",
          "name" : "your-name",
          "tag" : "a-tag",
          "zip_code" : 12456, # dummy value
          "country_code" : "de",
        },
        { 
          "station_id" : "your-id2",
          "name" : "your name 2",
          "tag" : "a second tag",
          "lat" : 1234, # dummy value
          "lon" : 215265, # dummy value
        }
      ]
    }

remark: `station_id` is mapped to openweathermap `external_id` field


# platform

tested on python3, and linux


# development status

alpha state, use on your own risk!


# installation

    phyton3 -m pip install tempres
    

# license

[`LICENSE`](https://github.com/kr-g/tempres/blob/main/LICENSE.md)

