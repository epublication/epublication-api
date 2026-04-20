import requests
import re
import os
import json

def update_local_readme():
    url = 'https://preview.epublication.ch/api/management/public/interface/v1/announcement-types'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    json_data = {
        'page': 0, 
        'pageSize': 20, 
        'sort': {'field': 'businessId', 'direction': 'ASC'}
    }

    try:
        # 1. Daten abrufen (identisch zu deinem ersten Skript)
        response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()

        # DEBUG: Zeigt dir die Struktur in der Konsole, falls nichts gefunden wird
        print("API Antwort empfangen.")

        # 2. Daten-Extraktion (Wir suchen flexibel nach Listen)
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Prüfe gängige Felder wie 'content', 'data' oder 'items'
            items = data.get('content') or data.get('data') or data.get('items') or []
            
        if not items:
            print("Konnte keine Liste in der API-Antwort finden. Hier ist die Struktur:")
            print(json.dumps(data, indent=2))
            markdown_text = "_Keine Daten in der bekannten Struktur gefunden._"
        else:
            # 3. Markdown Tabelle bauen
            markdown_text = "| ID | Name (DE) |\n| --- | --- |\n"
            for item in items:
                # Wir versuchen verschiedene Namens-Felder
                bid = item.get('businessId') or item.get('id', 'N/A')
                
                # Prüfe ob Name ein String oder ein Dict (Sprachen) ist
                name_field = item.get('name', 'N/A')
                if isinstance(name_field, dict):
                    name = name_field.get('de') or name_field.get('en') or str(name_field)
                else:
                    name = str(name_field)
                
                markdown_text += f"| {bid} | {name} |\n"

        # 4. In lokale README.md schreiben
        readme_path = "README.md"
        if not os.path.exists(readme_path):
            print(f"Fehler: {readme_path} existiert nicht im Ordner {os.getcwd()}")
            return

        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        start_tag = "<!-- DATA_START -->"
        end_tag = "<!-- DATA_END -->"

        if start_tag in readme_content and end_tag in readme_content:
            pattern = f"{re.escape(start_tag)}.*?{re.escape(end_tag)}"
            replacement = f"{start_tag}\n\n{markdown_text}\n\n{end_tag}"
            new_readme = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
            
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_readme)
            print(f"Erfolg! {len(items)} Zeilen in die Tabelle geschrieben.")
        else:
            print("Fehler: Die Tags <!-- DATA_START --> und <!-- DATA_END --> wurden nicht gefunden.")

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    update_local_readme()
