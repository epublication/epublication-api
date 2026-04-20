import requests
import re
import os

def update_readme():
    url = 'https://epublication.ch'
    
    # Tor Proxy Konfiguration (lokal auf Port 9050)
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }
    
    json_data = {
        'page': 0, 'pageSize': 20, 
        'sort': {'field': 'businessId', 'direction': 'ASC'}
    }

    try:
        print("Versuche Verbindung über Schweizer Tor-Exit...")
        response = requests.post(url, headers=headers, json=json_data, proxies=proxies, timeout=30)
        
        # IP-Check im Log (optional, zeigt ob CH-Exit funktioniert)
        # ip_check = requests.get('https://ipify.org', proxies=proxies).text
        # print(f"Verwendete Proxy-IP: {ip_check}")

        response.raise_for_status()
        data = response.json()
        items = data if isinstance(data, list) else data.get('content', [])

        # Markdown Tabelle erstellen
        markdown_text = "| ID | Name (DE) |\n| --- | --- |\n"
        for item in items:
            name_obj = item.get('name', {})
            name = name_obj.get('de') if isinstance(name_obj, dict) else name_obj
            markdown_text += f"| {item.get('businessId', '-')} | {name} |\n"

        # README schreiben
        readme_path = "README.md"
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        start_tag, end_tag = "<!-- DATA_START -->", "<!-- DATA_END -->"
        if start_tag in content and end_tag in content:
            new_content = re.sub(f"{re.escape(start_tag)}.*?{re.escape(end_tag)}", 
                                f"{start_tag}\n\n{markdown_text}\n\n{end_tag}", 
                                content, flags=re.DOTALL)
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("README erfolgreich über Proxy aktualisiert.")
        else:
            print("Tags nicht gefunden.")

    except Exception as e:
        print(f"Fehler: {e}")
        # Falls Tor fehlschlägt, geben wir den Response-Inhalt für Debugging aus
        if 'response' in locals():
            print(f"Antwort-Text: {response.text[:200]}")

if __name__ == "__main__":
    update_readme()
