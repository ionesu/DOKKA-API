import csv
import json
import os
import uuid

from geopy.geocoders import Nominatim
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, flash, redirect, url_for
from math import sin, cos, sqrt, atan2, radians

app = Flask(__name__, template_folder='template')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = basedir + '/upload/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = ['csv']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ApiResults(db.Model):
    """
    Responses persisted in a database with unique UUID and be
    available for querying by /api/getResult GET API.
    """
    uuid = db.Column(db.String, primary_key=True)
    points = db.Column(db.String)
    links = db.Column(db.String)

    def __init__(self, uuid, points, links):
        self.uuid = uuid
        self.points = points
        self.links = links

    def serialize(self):
        return {"points": self.points,
                "links": self.links,
                "result_id": self.uuid}


db.create_all()


@app.route('/')
def upload_form():
    return render_template('main.html')


@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return get_addresses(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            return redirect(request.url)


@app.route("/api/getAddresses", methods=['POST'])
def get_addresses(file_with_points):
    """
    /api/getAddresses POST API. It is a HTTP POST method that enables to upload a
    CSV file with point locations ( LAT/LON ).
    getAddresses method respond with JSON containing readable
    addresses ( or place names ) for each point location and all distinct links
    between each point including distance in meters.
    """

    def calculate_distance(lat1, lon1, lat2, lon2):
        radius = 6371.0 * 1000
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) * sin(dlat / 2) + cos(radians(lat1)) \
            * cos(radians(lat2)) * sin(dlon / 2) * sin(dlon / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return radius * c

    with open(file_with_points, newline='') as csv_file:
        points = []
        points_address = []
        links = []
        # Stop first iteration of cycle, when we have only one first point in points list.
        start_calculate = False

        for row in csv.DictReader(csv_file, delimiter=';'):

            points.append(row)
            # Convert latitude and longitude of the point into the address.
            geo = Nominatim(user_agent="Ivan_dokka")
            location = geo.reverse(f'{list(row.items())[1][1]}, {list(row.items())[2][1]}')
            point_address = {"name": list(row.items())[0][1],
                             "address": location.address.encode().decode('UTF-8')}
            points_address.append(point_address)

            if start_calculate:
                # Find the distance between all points in the list of points, except the last one we just added.
                for point in points[:-1]:
                    # Add in links list distance between last point in the points list and all points before.
                    links.append({'name': point['Points'] + points[-1]['Points'],
                                  'distance': calculate_distance(
                                      float(point['Latitude']),
                                      float(point['Longitude']),
                                      float(points[-1]['Latitude']),
                                      float(points[-1]['Longitude']))
                                  })
            # After we add first point in points list - we can start calculate distance,
            # because on the next step we will have 2 points.
            start_calculate = True

    uuid_db = str(uuid.uuid4())
    new_result = ApiResults(uuid_db, str(points_address), str(links))

    db.session.add(new_result)
    db.session.commit()

    return json.dumps(dict(points=points_address, links=links, result_id=uuid_db), ensure_ascii=False)


@app.route("/api/getResult/<uuid_code>", methods=['GET'])
def get_result(uuid_code):
    """
    /api/getResult GET API . It is an API to retrieve results of “/api/getAddresses” API
    identified by result_id.
    """
    result = ApiResults.query.get(uuid_code).serialize()

    return json.dumps(dict(result), ensure_ascii=False)
