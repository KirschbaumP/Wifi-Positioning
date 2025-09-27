import scan
import send_data
import csv
import sys
import json

networks = []
iterations = 5

sensor_id = int(sys.argv[1])
project_id = int(sys.argv[2])
x = float(sys.argv[3])
y = float(sys.argv[4])

for i in range(iterations):
    networks_scan = scan.scan_wifi()
    networks = networks + networks_scan

# DEBUG
#print(json.dumps(networks, indent=2))

with open('data_' + str(project_id) + '_' + str(sensor_id) + '_' + str(x) + '_' + str(y) + '.csv', mode='w', newline='') as datei:
    writer = csv.DictWriter(datei, fieldnames=['bssid', 'essid', 'rssi', 'x', 'y', 'sensor_id', 'project_id', 'timestamp'])
    writer.writeheader()
    for network in networks:
        # Objekt in Dictionary umwandeln:
        writer.writerow({
            'bssid': network['BSSID'],
            'essid': network['ESSID'],
            'rssi': network['RSSI'],
            'timestamp': network['TIMESTAMP'],
            'x': str(x),
            'y': str(y),
            'sensor_id': str(sensor_id),
            'project_id': str(project_id)
        })

send_data.sende_messdaten(networks, project_id, sensor_id, 'http://192.168.1.249:3001/api/wifi', x, y)
