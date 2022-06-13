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

following cmd-line tools are shipped within this package.


## tempres

`tempres` loads one data package from a device and stores ot under `~/.tempres/inq` (default) as json.

use `tempres --help` to see all cmd-line options.


## tempresdb

imports the data from `~/.tempres/inq` into a sqlite db `~/.tempresdb`.

currently no further cmd-line options to configure the process (todo)


## tempresplt

plots the data "temperature and pressure data over time" from `~/.tempresdb` with mathplotlib.

currently no further cmd-line options to configure the process (todo)


# platform

tested on python3, and linux


# development status

alpha state, use on your own risk!


# installation

    phyton3 -m pip install tempres
    

# license

[`LICENSE`](https://github.com/kr-g/tempres/blob/main/LICENSE.md)

