import requests
import re
import os
import json

def debug_update():
    url = 'https://preview.epublication.ch/api/management/public/interface/v1/announcement-types'
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    json_data = {'page': 0, 'pageSize': 20, 'sort': {'field': 'businessId', 'direction': 'ASC'}}

    print(f"--- DEBUG START ---")
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    print(f"Dateien im Ordner: {os.listdir('.')}")

    try:
        # 1. API Call
        response = requests.post(url, headers=headers, json=json_data)
        print(f"API Status Code: {response.status_code}")
        
        data = response.json()
        items = data if isinstance(data, list) else data.get('content', [])
        print(f"Anzahl gefundene Einträge: {len(items)}")

        # 2. Markdown erstellen
        if items:
            markdown_text = "| ID | Name |\n| --- | --- |\n"
            for item in items[:3]: # Nur die ersten 3 zur Kontrolle im Log
                print(f"Beispiel-Item: {item.get('businessId')} - {item.get('name')}")
            
            for item in items:
                name_obj = item.get('name', {})
                name = name_obj.get('de') if isinstance(name_obj, dict) else name_obj
                markdown_text += f"| {item.get('businessId', '-')} | {name} |\n"
        else:
            print("WARNUNG: Keine Items in der API-Antwort gefunden!")
            markdown_text = "_Keine Daten gefunden._"

        # 3. Datei-Operation
        readme_path = "README.md"
        if not os.path.exists(readme_path):
            print(f"FEHLER: {readme_path} existiert nicht!")
            return

        with open(readme_path, "r", encoding="utf-8") as f:
            old_content = f.read()

        start_tag, end_tag = "<!-- DATA_START -->", "<!-- DATA_END -->"
        
        if start_tag in old_content and end_tag in old_content:
            new_content = re.sub(f"{re.escape(start_tag)}.*?{re.escape(end_tag)}", 
                                f"{start_tag}\n\n{markdown_text}\n\n{end_tag}", 
                                old_content, flags=re.DOTALL)
            
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("README.md wurde im Dateisystem überschrieben.")
            
            # Vergleich zur Sicherheit
            if old_content == new_content:
                print("HINWEIS: Der neue Inhalt ist identisch mit dem alten Inhalt (kein Git-Commit nötig).")
            else:
                print("ERFOLG: Inhalt hat sich geändert.")
        else:
            print(f"FEHLER: Tags {start_tag} nicht in README gefunden!")

    except Exception as e:
        print(f"KRITISCHER FEHLER: {e}")

if __name__ == "__main__":
    debug_update()
