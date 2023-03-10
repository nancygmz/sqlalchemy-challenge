# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


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

# Flask routes
@app.route("/")
def first_page():
    
    return (

        f"Honolulu and Hawaii Climate :<br/>"
        f"Available routes:<br/>"
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
    recent_date_result = session.query(func.max(Measurement.date)).one()[0]
    for recent_date in recent_date_result:
        recent_date = dt.datetime.strptime(recent_date_result, "%Y-%m-%d")

    # Calculate one year ago and query data
    one_year_ago = recent_date - timedelta(days=365)
    
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

#JSON Station List
@app.route("/api/v1.0/stations")
def stations():

    # Create session
    session = Session(bind=engine) 

    # Create Query and close session
    stations = session.query(station.station, station.name).all()
    session.close()

    # Convert results to dictionary and return results
    all_stations = []
    for id,name in stations:
        station_dict = {}
        station_dict["Station ID"] = id
        station_dict["Station Name"] = name
        all_stations.append(station_dict)
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create session and query
    session = Session(bind=engine) 

    active_station = session.query(measurement.station,func.count(measurement.station)).\
           group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station = active_station[0]

    # Find the most recent date in the data set.
    recent_date_result=session.query(measurement.date).order_by(measurement.date.desc()).first()
    for result in recent_date_result:
        recent_date = result
    recent_date = dt.datetime.strptime(recent_date,"%Y-%m-%d")
    # Calculate one year ago and query data
    year_ago = recent_date - dt.timedelta(days=365)

    # Query results
    year_temps = session.query(measurement.date,measurement.tobs).\
                  filter(measurement.date > year_ago).\
                  filter(measurement.station == most_active_station).\
                  group_by(measurement.date).all()
    session.close()
    # Convert results to dictionary and return results
    results = []
    for date,temp in year_temps:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = temp
        results.append(temp_dict)
    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(bind=engine)
    # Return a JSON list of the min, max,avg temp for a specified start or start-end range
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    
    results = []
    for min, avg, max in start_results:
        start_dict = {}
        start_dict["Min Temp"] = min
        start_dict["Average Temp"] = avg
        start_dict["Max Temp"] = max
        results.append(start_dict) 
        return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(bind=engine)

    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
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


