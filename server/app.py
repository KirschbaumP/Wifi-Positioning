from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import joblib
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensordaten.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MODEL_PATH = 'wifi_position_model.pkl'


# Datenmodell für Projekte
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


# Datenmodell für WLAN-Signale
class WifiSignalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    position_x = db.Column(db.Float, nullable=False)
    position_y = db.Column(db.Float, nullable=False)
    bssid = db.Column(db.String(17), nullable=False)
    essid = db.Column(db.String(100), nullable=False)
    rssi = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    project = db.relationship('Project', backref='signals')

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp.isoformat(),
            'position_x': self.position_x,
            'position_y': self.position_y,
            'bssid': self.bssid,
            'essid': self.essid,
            'rssi': self.rssi,
            'project_id': self.project_id
        }


# Datenbank initialisieren
with app.app_context():
    db.create_all()


# Projekt anlegen
@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    if not name:
        return jsonify({'error': 'Name ist erforderlich'}), 400
    new_project = Project(name=name, description=description)
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'message': 'Projekt erstellt', 'project': new_project.to_dict()}), 201


# Alle Projekte auflisten
@app.route('/api/projects', methods=['GET'])
def list_projects():
    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects])


# Projekt bearbeiten
@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    project = Project.query.get_or_404(project_id)

    # Aktualisieren der Felder
    name = data.get('name')
    description = data.get('description')

    if name:
        project.name = name
    if description:
        project.description = description

    db.session.commit()
    return jsonify({'message': 'Projekt aktualisiert', 'project': project.to_dict()})


# Projekt löschen
@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Projekt gelöscht'})


# Messdaten (Liste) empfangen und speichern
@app.route('/api/wifi', methods=['POST'])
def receive_wifi_signals():
    data = request.get_json()

    sensor_id = data.get('sensor_id')
    timestamp_str = data.get('timestamp')
    position_x = data.get('position_x')
    position_y = data.get('position_y')
    signals = data.get('signals')  # List von Signalen
    project_id = data.get('project_id')  # optional

    # Validierung
    if sensor_id is None or signals is None:
        print('sensor_id und signals sind erforderlich')
        return jsonify({'error': 'sensor_id und signals sind erforderlich'}), 400

    # Projekt validieren, falls angegeben
    if project_id:
        proj = Project.query.get(project_id)
        if not proj:
            print('Projekt nicht gefunden')
            return jsonify({'error': 'Projekt nicht gefunden'}), 400

    # Timestamp parsen
    if timestamp_str:
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            print('Ungültiges Datumsformat')
            return jsonify({'error': 'Ungültiges Datumsformat'}), 400
    else:
        timestamp = datetime.utcnow()

    # Signale speichern
    gespeicherte_signale = []
    for signal in signals:
        bssid = signal.get('bssid')
        essid = signal.get('essid')
        rssi = signal.get('rssi')
        if bssid is None or rssi is None:
            continue
        neue_signal = WifiSignalData(
            sensor_id=int(sensor_id),
            timestamp=timestamp,
            position_x=position_x,
            position_y=position_y,
            bssid=bssid,
            essid=essid,
            rssi=rssi,
            project_id=project_id
        )
        db.session.add(neue_signal)
        gespeicherte_signale.append(neue_signal.to_dict())

    db.session.commit()
    return jsonify({'message': 'Signale gespeichert', 'daten': gespeicherte_signale}), 201


@app.route('/api/wifi', methods=['GET'])
def get_filtered_signale():
    project_id = request.args.get('project_id', type=int)

    if project_id:
        daten = WifiSignalData.query.filter_by(project_id=project_id).order_by(WifiSignalData.timestamp.desc()).all()
    else:
        daten = WifiSignalData.query.order_by(WifiSignalData.timestamp.desc()).all()

    return jsonify([d.to_dict() for d in daten])


@app.route('/api/train', methods=['POST'])
def get_train():
    data = request.get_json()
    project_id = data.get('project_id')
    essids = data.get('essids')

    if not project_id:
        return jsonify({'error': 'Project_id fehlt'}), 400
    if not essids:
        return jsonify({'error': 'essids fehlt'}), 400

    import train
    X, y = train.prepare_ml_dataset('sqlite:///instance/sensordaten.db', project_id=project_id, essid_list=essids)
    regr = train.train(X, y)

    joblib.dump(regr, MODEL_PATH)

    return jsonify('ok')


@app.route('/api/predict', methods=['POST'])
def get_predict():
    model = joblib.load(MODEL_PATH)
    data = request.get_json()
    X = pd.DataFrame(data, columns=model.feature_names_in_)
    return jsonify(model.predict(X).tolist())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
