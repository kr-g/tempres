import os

BASE_PATH = "~/.tempres"

DEFAULT_PATH = "~/.tempres/inq"

VERSION = "v0.0.2-a"


def strip_tag(tag):
    if tag is not None:
        tag = tag.strip()
        if len(tag) == 0:
            tag = None
    return tag


def get_path(tag=None, base=None):
    if base is None:
        base = BASE_PATH
    inq = "inq"
    tag = strip_tag(tag)
    if tag is not None:
        inq = inq + "-" + tag
    dest = os.path.join(base, inq)
    return dest
