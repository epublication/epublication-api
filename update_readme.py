import requests

url = 'https://preview.epublication.ch/api/management/public/interface/v1/announcement-types'

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

json_data = {
    'page': 0,
    'pageSize': 20,
    'sort': {
        'field': 'businessId',
        'direction': 'ASC',
    },
}

response = requests.post(url, headers=headers, json=json_data)

# Ergebnis ausgeben
if response.status_code == 200:
    print(response.json())
else:
    print(f"Fehler: {response.status_code}")
    print(response.text)
