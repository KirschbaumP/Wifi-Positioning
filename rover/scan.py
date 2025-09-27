import subprocess
import json
import time
import datetime

def scan_wifi():
    # nutze 'iwlist' ( Linux-kompatibel )
    scan_output = subprocess.check_output(['iwlist', 'wlan1', 'scanning']).decode()
    timestamp = datetime.datetime.now()

    networks = []
    current_network = {}
    for line in scan_output.split('\n'):
        line = line.strip()
        if line.startswith('Cell'):
            if current_network:
                networks.append(current_network)
                current_network = {}
            # z.B. Cell 01 - Address: BSSID
            current_network['TIMESTAMP'] = str(timestamp)
            current_network['BSSID'] = line.split('Address:')[-1].strip()
        elif 'Signal level=' in line:
            # RSSI-Wert extrahieren
            rssi_part = line.split('Signal level=')[-1]
            rssi = int(rssi_part.split(' ')[0])
            current_network['RSSI'] = rssi
        elif 'ESSID:"' in line:
            # ESSID-Wert extrahieren
            current_network['ESSID'] = line.split('ESSID:')[-1].strip()[1:-1]
    if current_network:
        networks.append(current_network)
    return networks

# Beispiel: WiFi-Scan durchführen
#networks = scan_wifi()
#print(json.dumps(networks, indent=2))
