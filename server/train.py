import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor


def prepare_ml_dataset(path, measurement_filter=None, filter_value=None, project_id=None, essid_list=None):
    """
    Holt WLAN-Daten aus der Datenbank, pivotiert sie in ein ML-freundliches Format,
    gefiltert nach ProjektID und optional weiteren Kriterien, inklusive einer Essid-Liste.

    Args:
        measurement_filter (str): Name des Filters ('timestamp', 'sensor_id' etc.)
        filter_value: Wert, nach dem gefiltert wird
        project_id (int): Falls gesetzt, nur Signale dieses Projekts verwenden
        essid_list (list of str): Falls gesetzt, nur Signale mit diesen ESSID’s verwenden

    Returns:
        X (pd.DataFrame): Features (Signalstärken pro BSSID)
        y_pos_x (pd.Series): Zielvariable X-Position
        y_pos_y (pd.Series): Zielvariable Y-Position
    """
    # Verbindung zur Datenbank
    engine = create_engine(path)

    # Basis-Abfrage
    query = "SELECT sensor_id, timestamp, position_x, position_y, bssid, rssi, project_id, essid FROM wifi_signal_data"
    df = pd.read_sql(query, engine)

    # Filter nach ProjektID, falls angegeben
    if project_id is not None:
        df = df[df['project_id'] == project_id]

    # Filter nach essid list
    if essid_list is not None:
        df = df[df['essid'].isin(essid_list)]

    # Optional filtern nach weiteren Kriterien
    if measurement_filter and filter_value is not None:
        if measurement_filter == 'timestamp':
            df = df[df['timestamp'] == filter_value]
        elif measurement_filter == 'sensor_id':
            df = df[df['sensor_id'] == filter_value]
        else:
            raise ValueError("Unbekannter Filter-Name")

    # Pivot: BSSID's als Spalten, Werte rssi
    pivot_df = df.pivot_table(
        index=['sensor_id', 'timestamp', 'position_x', 'position_y'],
        columns='bssid',
        values='rssi'
    )

    # reset index, um Zeilen für ML aufzubereiten
    pivot_df = pivot_df.reset_index()

    # Features (alle BSSID-Spalten)
    X = pivot_df.drop(['sensor_id', 'timestamp', 'position_x', 'position_y'], axis=1)

    # NaNs durch einen Wert ersetzen, z.B. -100 dBm
    #X_filled = X.fillna(-100)

    y = pivot_df[['position_x', 'position_y']].copy()
    return X, y

def train(X, y):
    regr = RandomForestRegressor(random_state=0)
    regr.fit(X, y)

    return regr


# if __name__ == "__main__":
#     db_uri = 'sqlite:///instance/sensordaten.db'
#     essids = ['19BC','1209','1B45','1AD3']
#     X, y = prepare_ml_dataset(db_uri, project_id=2, essid_list=essids)
#     print("Features (X):")
#     print(X.count)
#     print("Position:")
#     print(y.count)
#     regr = train(X, y)
#     print(X.columns.values)
#     print(regr.predict([[-31,-47,-40,-31]]))
