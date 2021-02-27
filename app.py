
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

@app.route("/")
def welcome():
    return(
        f"Avaible Routes:<br/>"
        f"<a href=/api/v1.0/percipitation>Percipitation</a><br/>"
        f"(/api/v1.0/percipitation)<br/>"
        f"<a href=/api/v1.0/stations>Stations</a><br/>"
        f"(/api/v1.0/stations)<br/>"
        f"<a href=/api/v1.0/tobs>TOBS</a><br/>"
        f"(/api/v1.0/tobs)<br/>"
        f"<a href=/api/v1.0/start>Start Date</a><br/>"
        f"(/api/v1.0/start (enter as YYYY-MM-DD))<br/>"
        f"<a href=/api/v1.0/start/end>Start Date and End Date</a><br/>"
        f"(/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD))"
   )

#Convert query results to a dictionary 
@app.route("/api/v1.0/percipitation")
def precipitation():
    session = Session(engine)
    results = (session.query(Measurement.date, Measurement.tobs)
                      .order_by(Measurement.date))
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
    ld_obj = dt.datetime.strptime(ld_str, '(%Y-%m-%d)')
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

# Calculate `TMIN`, `TAVG`, and `TMAX` for start date
@app.route("/api/v1.0/<start>")
def start_only(start):
    session = Session(engine)
    dr_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    dr_max_str = str(dr_max)
    dr_max_str = re.sub("'|,", "",dr_max_str)
    print (dr_max_str)
    dr_min = session.query(Measurement.date).first()
    dr_min_str = str(dr_min)
    dr_min_str = re.sub("'|,", "",dr_min_str)
    print (dr_min_str)


    # Check for valid entry of start date
    valid_entry = session.query(exists().where(Measurement.date == start)).scalar()
 
    if valid_entry:

    	results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    				 	  .filter(Measurement.date >= start).all())

    	tmin =results[0][0]
    	tavg ='{0:.4}'.format(results[0][1])
    	tmax =results[0][2]
    
    	result_printout =( ['Entered Start Date: ' + start,
    						'The lowest Temperature was: '  + str(tmin) + ' F',
    						'The average Temperature was: ' + str(tavg) + ' F',
    						'The highest Temperature was: ' + str(tmax) + ' F'])
    	return jsonify(result_printout)

    return jsonify({"Direction": f"Add Start Date to End of URL. Date Range is {dr_min_str} to {dr_max_str}."})

# Calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date
@app.route("/api/v1.0/<start>/<end>") 
def start_end(start, end):
    session = Session(engine)
    dr_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    dr_max_str = str(dr_max)
    dr_max_str = re.sub("'|,", "",dr_max_str)
    print (dr_max_str)
    dr_min = session.query(Measurement.date).first()
    dr_min_str = str(dr_min)
    dr_min_str = re.sub("'|,", "",dr_min_str)
    print (dr_min_str)

    # Check for valid entry of start date
    valid_entry_start = session.query(exists().where(Measurement.date == start)).scalar()
 	
 	# Check for valid entry of end date
    valid_entry_end = session.query(exists().where(Measurement.date == end)).scalar()

    if valid_entry_start and valid_entry_end:

    	results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    					  .filter(Measurement.date >= start)
    				  	  .filter(Measurement.date <= end).all())

    	tmin =results[0][0]
    	tavg ='{0:.4}'.format(results[0][1])
    	tmax =results[0][2]
    
    	result_printout =( ['Entered Start Date: ' + start,
    						'Entered End Date: ' + end,
    						'The lowest Temperature was: '  + str(tmin) + ' F',
    						'The average Temperature was: ' + str(tavg) + ' F',
    						'The highest Temperature was: ' + str(tmax) + ' F'])
    	return jsonify(result_printout)

    return jsonify({"Direction": f"Add Start Date and End Date to End of URL. Date Range is {dr_min_str} to {dr_max_str}"}), 404


if __name__ == '__main__':
    app.run(debug=True)
