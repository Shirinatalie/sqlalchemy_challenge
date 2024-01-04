# Import necessary libraries
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Create engine to connect to SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the classes named station and measurement
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create a session to interact with the database
session = Session(bind=engine)

# Flask application setup
app = Flask(__name__)

# Precipitation route
@app.route("/api/v1.0/precipitation")
def get_precipitation():
    """Return jsonified precipitation data for the last year."""
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (np.datetime64(last_date) - np.timedelta64(365, 'D')).astype(str)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Stations route
@app.route("/api/v1.0/stations")
def get_stations():
    """Return jsonified data of all stations in the database."""
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    # Convert the query results to a list of dictionaries
    stations_data = [{"station": station, "name": name} for station, name in results]

    return jsonify(stations_data)

# Temperature observations (tobs) route
@app.route("/api/v1.0/tobs")
def get_tobs():
    """Return jsonified data for the most active station for the last year."""
    # Find the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()

    if most_active_station:
        most_active_station = most_active_station[0]

        # Calculate the date 1 year ago from the last data point in the database
        last_date = session.query(func.max(Measurement.date)).scalar()
        one_year_ago = (np.datetime64(last_date) - np.timedelta64(365, 'D')).astype(str)

        # Query temperature observations for the most active station in the last year
        results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date >= one_year_ago).all()

        # Convert the query results to a list of dictionaries
        tobs_data = [{"date": date, "tobs": tobs} for date, tobs in results]

        return jsonify(tobs_data)

    return jsonify({"error": "No stations found"})

# Dynamic route with start date parameter
@app.route("/api/v1.0/<start>")
def get_temperatures_start(start):
    """Return min, max, and average temperatures from the given start date to the end of the dataset."""
    # Query temperatures for the specified start date to the end of the dataset
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert the query results to a list of dictionaries
    temperature_data = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]

    return jsonify(temperature_data)

# Dynamic route with start and end date parameters
@app.route("/api/v1.0/<start>/<end>")
def get_temperatures_start_end(start, end):
    """Return min, max, and average temperatures from the given start date to the given end date."""
    # Query temperatures for the specified start and end dates
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Convert the query results to a list of dictionaries
    temperature_data = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]

    return jsonify(temperature_data)

# Close the session after using it
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)



