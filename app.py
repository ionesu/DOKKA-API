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
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__)) + '/upload/'
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if 'file' not in request.files or file.filename == '':
            print('Failed to receive file. Or format is not supported.')

            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return get_addresses(os.path.join(app.config['UPLOAD_FOLDER'], filename))


@app.route("/getAddresses", methods=['POST'])
def get_addresses(points):
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

    with open(points, newline='') as csv_file:
        points = []
        points_address = []
        links = []

        for row in csv.DictReader(csv_file, delimiter=';'):
            p = {"name": list(row.items())[0][1], "address": (list(row.items())[1][1], list(row.items())[2][1])}
            points.append(p)
            geo = Nominatim(user_agent="Ivan_dokka")
            location = geo.reverse(f'{list(row.items())[1][1]}, {list(row.items())[2][1]}')
            b = {"name": list(row.items())[0][1], "address": location.address.encode().decode('UTF-8')}
            points_address.append(b)

    z = []
    for point in points:
        for v in point.values():
            z.append(v)

    for i in range(0, len(z) - 1, 2):
        if i > 0:
            for j in range(i - 2, 0, -2):
                links.append({'name': z[i] + z[j],
                              'distance': calculate_distance(float(z[i + 1][0]), float(z[i + 1][1]), float(z[j + 1][0]),
                                                             float(z[j + 1][1]))})
        else:
            for j in range(i + 2, len(z), 2):
                links.append({'name': z[i] + z[j],
                              'distance': calculate_distance(float(z[i + 1][0]), float(z[i + 1][1]), float(z[j + 1][0]),
                                                             float(z[j + 1][1]))})

    uuid_db = str(uuid.uuid4())
    new_result = ApiResults(uuid_db, str(points_address), str(links))

    db.session.add(new_result)
    db.session.commit()

    return json.dumps(dict(points=points_address, links=links, result_id=uuid_db), ensure_ascii=False)


@app.route("/getResult/<uuid_code>", methods=['GET'])
def get_result(uuid_code):
    """
    /api/getResult GET API . It is an API to retrieve results of “/api/getAddresses” API
    identified by result_id.
    """
    result = ApiResults.query.get(uuid_code).serialize()

    return json.dumps(dict(result), ensure_ascii=False)
