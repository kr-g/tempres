import os
import glob
import json
import uuid

DEFAULT_PATH = "~/.tempres/inq"

from sqlalchemy import Column
from sqlalchemy import ForeignKey

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean

from sqlalchemy import create_engine

from sqlalchemy import select

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

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


echo = not True
# in memory db
# todo
engine = create_engine("sqlite://", echo=echo, future=True)

meta = Base.metadata.create_all(engine)


from sqlalchemy.orm import Session


pat = os.path.join(DEFAULT_PATH, "**", "tempres-*.json")
pat = os.path.expanduser(pat)
pat = os.path.expandvars(pat)
print("pattern", pat)

tag = None

for fe in glob.iglob(pat, recursive=True):
    with open(fe) as f:
        cont = f.read()
        data = json.loads(cont)
        # print(data)

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

# get the data from database
for dbrec in session.execute(select(TempRec)):
    print("db=", dbrec)
