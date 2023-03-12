# import dependancies 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect tables
Base.prepare(engine,reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Initialize app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home_page():
    """List all available api routes."""
    return (
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session
    session = Session(engine)

    # Find the most recent date in the data set.
    recent_date_result = session.query(func.max(measurement.date)).one()[0]
    for recent_date in recent_date_result:
        recent_date = dt.datetime.strptime(recent_date_result, "%Y-%m-%d")

    # Calculate one year ago and query data
    year_ago = recent_date -  dt.timedelta(days=365)
    
    last_year_data = session.query(measurement.date,measurement.prcp).filter(measurement.date > year_ago).all()
    session.close()

# Create a JSON list of temperatures from the previous year
    results = []
    for date,prcp in last_year_data:
        precip_dict = {}
        precip_dict["precipitation"] = prcp
        precip_dict["date"] = date
        results.append(precip_dict)
    return jsonify(results)

#Station List
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Return JSON list of stations from the dataset
    results = session.query(measurement.station).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
# Query the dates and temperature observations of the most-active station
    total_year_temp = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == 'USC00519281').\
    filter(measurement.date >= '2016-08-23').all()
    session.close()
# Return a JSON list of temperature observations for the previous year
    results = []
    for date, tobs in total_year_temp:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperatures"] = tobs
        results.append(tobs_dict)

    return jsonify(results)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    # Return a JSON list of the min, max,avg temp for a specified start or start-end range
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()
    
    start_results = []
    for min, avg, max in results:
        start_dict = {}
        start_dict["Min Temp"] = min
        start_dict["Average Temp"] = avg
        start_dict["Max Temp"] = max
        start_results.append(start_dict) 
        return jsonify(start_results)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    start_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    
    results = []
    for min, avg, max in start_results:
        start_end_dict = {}
        start_end_dict["Min Temp"] = min
        start_end_dict["Average Temp"] = avg
        start_end_dict["Max Temp"] = max
        results.append(start_end_dict) 
        return jsonify(results)



if __name__ == '__main__':
    app.run(debug=True)