import os
import glob
import json
import uuid

from sqlalchemy import Column

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean

from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


DEFAULT_PATH = "~/.tempres/"
DEFAULT_PATH_INQ = os.path.join(DEFAULT_PATH, "inq")

Base = declarative_base()


def create_id():
    return uuid.uuid4().hex


_a_id = create_id()
LEN_ID = len(_a_id)


class TempRec(Base):
    __tablename__ = "temp_rec"

    id = Column(String(LEN_ID), primary_key=True)

    tag = Column(String(LEN_ID < 1), nullable=True)

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)

    year_month_day = Column(String(8), nullable=False)
    year_month = Column(String(6), nullable=False)
    month_day = Column(String(4), nullable=False)

    hour = Column(Integer, nullable=False)
    minute = Column(Integer, nullable=False)
    second = Column(Integer, nullable=False)

    is_utc = Column(Boolean, default=True)
    time_stamp = Column(Float, nullable=False)

    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)

    def __repr__(self):
        flds = {}
        for f in [
            "id",
            "tag",
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "is_utc",
            "time_stamp",
            "temperature",
            "pressure",
        ]:
            flds[f] = self.__dict__[f]
        return f"TempRec({flds})"


def get_db_path(path=None):
    if path is None:
        path = DEFAULT_PATH
    db_path = os.path.join(path, "tempres.db")
    db_path = os.path.expanduser(db_path)
    db_path = os.path.expandvars(db_path)
    return db_path


def open_db(db_path):
    db_path = "sqlite://" + os.sep + db_path
    print("db_path", db_path)
    engine = create_engine(db_path, echo=False)
    meta = Base.metadata.create_all(engine)
    return engine


def strip_tag(tag):
    if tag is not None:
        tag = tag.strip()
        if len(tag) == 0:
            tag = None
    return tag


def insert_rec(engine, data, tag=None):

    tag = strip_tag(tag)

    _time = data["time"]

    _temperature = float(data["temperature"])
    _pressure = float(data["pressure"])
    _utc = data["utc"]
    _time_stamp = float(data["time_ux"])

    with Session(engine) as session:
        db_rec = TempRec(
            id=create_id(),
            tag=tag,
            year=_time[0],
            month=_time[1],
            day=_time[2],
            year_month_day=f"{_time[0]:04}{_time[1]:02}{_time[2]:02}",
            year_month=f"{_time[0]:04}{_time[1]:02}",
            month_day=f"{_time[1]:02}{_time[2]:02}",
            hour=_time[3],
            minute=_time[4],
            second=_time[5],
            is_utc=_utc,
            time_stamp=_time_stamp,
            temperature=_temperature,
            pressure=_pressure,
        )
        session.add(db_rec)
        session.commit()


def get_date(data):
    year = data["time"][0]
    month = data["time"][1]
    day = data["time"][2]

    hour = data["time"][3]
    minute = data["time"][4]
    second = data["time"][5]

    return year, month, day, hour, minute, second


def build_date_qry(session, data, tag=None, exclude_tag=False, full=False):
    tag = strip_tag(tag)
    year, month, day, hour, minute, second = get_date(data)
    qry = (
        (session.query(TempRec) if full else session.query(TempRec.id))
        .where(TempRec.year.is_(year))
        .where(TempRec.month.is_(month))
        .where(TempRec.day.is_(day))
        .where(TempRec.hour.is_(hour))
        .where(TempRec.minute.is_(minute))
        .where(TempRec.second.is_(second))
    )
    if not exclude_tag:
        qry = qry.where(TempRec.tag.is_(tag))

    return qry


def qry_date(engine, data, tag=None, exclude_tag=False, full=False):
    with Session(engine) as session:
        qry = build_date_qry(session, data, tag, exclude_tag, full)
        return qry.all()


def qry_all(engine, tag=None, exclude_tag=False, full=False):
    with Session(engine) as session:
        qry = session.query(TempRec) if full else session.query(TempRec.id)
        if not exclude_tag:
            qry = qry.where(TempRec.tag.is_(tag))
        return qry.all()


def qry_count_date(engine, data, tag=None, exclude_tag=False):
    with Session(engine) as session:
        qry = build_date_qry(session, data, tag, exclude_tag, False)
        return qry.count()


def qry_count_all(engine, tag=None, exclude_tag=False):
    tag = strip_tag(tag)
    with Session(engine) as session:
        qry = session.query(TempRec.id)
        if not exclude_tag:
            qry = qry.where(TempRec.tag.is_(tag))
        return qry.count()


db_path = get_db_path()

print("db exists", os.path.exists(db_path))

engine = open_db(db_path)


pat = os.path.join(DEFAULT_PATH_INQ, "**", "tempres-*.json")
pat = os.path.expanduser(pat)
pat = os.path.expandvars(pat)
print("pattern", pat)

# todo
tag = " "

tag = strip_tag(tag)

skip_existing = 0
inserted = 0

for fe in glob.iglob(pat, recursive=True):
    with open(fe) as f:
        cont = f.read()
        data = json.loads(cont)
        if qry_count_date(engine, data, tag) > 0:
            skip_existing = skip_existing + 1
        else:
            insert_rec(engine, data, tag=tag)
            inserted = inserted + 1

found = 0
for dbrec in qry_all(engine, tag=tag, exclude_tag=False, full=False):
    print(dbrec)
    found = found + 1

print("skip_existing", skip_existing)
print("inserted", inserted)

print("found", found)
print("all tag", tag, qry_count_all(engine, tag=tag, exclude_tag=False))
print("all", qry_count_all(engine, tag=tag, exclude_tag=True))
