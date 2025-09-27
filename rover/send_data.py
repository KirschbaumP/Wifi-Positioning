import requests
from collections import defaultdict
from datetime import datetime

def sende_messdaten(messdaten, project_id, sensor_id, api_url, x, y):
    """
    Sendet Messdaten an die API, gruppiert nach Timestamp.

    :param messdaten: Liste der Dictionaries mit den Messdaten
    :param project_id: Projekt-ID (int)
    :param sensor_id: Sensor-ID (int)
    :param api_url: Die URL des API-Endpunkts (String)
    """
    # Gruppiere Daten nach Timestamp
    gruppierte_daten = defaultdict(list)
    for datensatz in messdaten:
        timestamp_str = datensatz['TIMESTAMP']
        # Optional: Formatierung des Timestamps anpassen, z.B. ISO 8601
        # Beispiel: Convert to ISO 8601 Format
        dt_obj = datetime.fromisoformat(timestamp_str)
        timestamp_iso = dt_obj.isoformat()
        gruppierte_daten[timestamp_iso].append(datensatz)

    # Für jeden Timestamp einen Request schicken
    for timestamp, daten_liste in gruppierte_daten.items():
        # Erzeuge die Signal-Liste
        signale = []
        for daten in daten_liste:
            signale.append({
                "bssid": daten["BSSID"],
                "essid": daten["ESSID"],
                "rssi": daten["RSSI"]
            })

        # Erstelle den Body
        body = {
            "sensor_id": sensor_id,
            "timestamp": timestamp,
            "position_x": x,  # falls bekannt, sonst auf 0 setzen
            "position_y": y,  # falls bekannt, sonst auf 0 setzen
            "project_id": project_id,
            "signals": signale
        }

        # Optional: Debug-Ausdruck
        print(f"Sende Daten für Timestamp: {timestamp}")
#        print(body)

        # Sende den POST Request
        try:
            response = requests.post(api_url, json=body)
            response.raise_for_status()
            print(f"Erfolg für {timestamp}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Fehler beim Senden für {timestamp}: {e}")

# Beispielaufruf:
# messdaten = [...] # Deine Datenliste
# sende_messdaten(messdaten, project_id=1, sensor_id=1, api_url="https://deine.api/deendpoint")
