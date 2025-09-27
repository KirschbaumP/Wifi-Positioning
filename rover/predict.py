import scan
import json
import requests

api_url = "http://192.168.1.101:3001/api/predict"

networks =  scan.scan_wifi()

ap1 = [ap for ap in networks if ap['BSSID'] == '18:D6:C7:0F:63:8A']
ap2 = [ap for ap in networks if ap['BSSID'] == '18:D6:C7:0A:8A:1F']
ap3 = [ap for ap in networks if ap['BSSID'] == '60:E3:27:1C:2C:A4']
ap4 = [ap for ap in networks if ap['BSSID'] == '18:D6:C7:0C:AB:C7']

#print(json.dumps(networks, indent=2))
#print(json.dumps(ap1, indent=2))
print(str(ap1[0]['RSSI']) + ',' + str(ap2[0]['RSSI']) + ',' + str(ap3[0]['RSSI']) + ',' + str(ap4[0]['RSSI']))

body = [{
        "18:D6:C7:0F:63:8A": ap1[0]['RSSI'],
        "18:D6:C7:0A:8A:1F": ap2[0]['RSSI'],
        "60:E3:27:1C:2C:A4": ap3[0]['RSSI'],
        "18:D6:C7:0C:AB:C7": ap4[0]['RSSI']
}]
print(json.dumps(body))

        # Optional: Debug-Ausdruck
print(f"Sende Daten")
#        print(body)

        # Sende den POST Request
try:
    response = requests.post(api_url, json=body)
    response.raise_for_status()
    print(f"Position: {response.json()}")
except requests.RequestException as e:
    print(f"Fehler beim Senden {e}")
