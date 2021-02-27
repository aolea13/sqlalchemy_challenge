
#Set up and Routes
from flask import Flask
import numpy as np
import re
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists

from flask import Flask, jsonify

#Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Set up
app = Flask(__name__)

app.route("/")
def welcome():
    return(
        f"Avaible Routes:<br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
   )

#Convert query results to a dictionary 
@app.route("/api/v1.0/percipitation")
def percipitation():
    session = Session(engine)
    results = (session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date))

    pd_tobs = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        pd_tobs.append(dt_dict)
    return jsonify(pd_tobs)

#JSON List of Stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()
    sd = list(np.ravel(results))
    return jsonify(sd)

#Query TOBS of Most Active Station
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    ld = (session.query(Measurement.date)
                          .order_by(Measurement.date
                          .desc())
                          .first())
    ld_str = str(ld)
    ld_str = re.sub("'|,", "", ld_str)
    ld_obj = dt.datetime.strptime(ld_str, '(%Y-%m-%d')
    query_start_date = dt.date(ld_obj.year, ld_obj.month, ld_obj.day) - dt.timedelta(days = 366)
    station_list_q = (session.query(Measurement.station, func.count(Measurement.station))
                             .group_by(Measurement.station)
                             .order_by(func.count(Measurement.station).desc())
                             .all())
    station_hno = station_list_q[0][0]
    print(station_hno)
    results = (session.query(Measurement.station, Measurement.date, Measurement.tobs)
                      .filter(Measurement.date >= query_start_date)
                      .filter(Measurement.station == station_hno)
                      .all())
    tobs_list = []
    for result in results:
        line = {}
        line["Date"] = result[1]
        line["Stataion"] = result[0]
        line["Temperature"] = int(result[2])
        tobs_list.append(line)
    return jsonify(tobs_list)

