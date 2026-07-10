import pandas as pd
import requests
import json
import io
import time

teams = {
    "Norway": "Norway_national_football_team",
    "Austria": "Austria_national_football_team",
    "Italy": "Italy_national_football_team",
    "Sweden": "Sweden_national_football_team",
    "Colombia": "Colombia_national_football_team",
    "Chile": "Chile_national_football_team",
    "Nigeria": "Nigeria_national_football_team",
    "Qatar": "Qatar_national_football_team",
    "Ecuador": "Ecuador_national_football_team",
    "Senegal": "Senegal_national_football_team",
    "Netherlands": "Netherlands_national_football_team",
    "England": "England_national_football_team",
    "Iran": "Iran_national_football_team",
    "USA": "United_States_men%27s_national_soccer_team",
    "Wales": "Wales_national_football_team",
    "Argentina": "Argentina_national_football_team",
    "Saudi Arabia": "Saudi_Arabia_national_football_team",
    "Mexico": "Mexico_national_football_team",
    "France": "France_national_football_team",
    "Australia": "Australia_men%27s_national_soccer_team",
    "Denmark": "Denmark_national_football_team",
    "Tunisia": "Tunisia_national_football_team",
    "Spain": "Spain_national_football_team",
    "Costa Rica": "Costa_Rica_national_football_team",
    "Germany": "Germany_national_football_team",
    "Japan": "Japan_national_football_team",
    "Belgium": "Belgium_national_football_team",
    "Morocco": "Morocco_national_football_team",
    "Croatia": "Croatia_national_football_team",
    "Brazil": "Brazil_national_football_team",
    "Serbia": "Serbia_national_football_team",
    "Switzerland": "Switzerland_national_football_team",
    "Cameroon": "Cameroon_national_football_team",
    "Portugal": "Portugal_national_football_team",
    "Ghana": "Ghana_national_football_team",
    "Uruguay": "Uruguay_national_football_team",
    "South Korea": "South_Korea_national_football_team",
}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

network_data = {}

for nation, url_end in teams.items():
    print(f"Henter data for {nation}...")
    url = f"https://en.wikipedia.org/wiki/{url_end}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        
        found = False
        for df in tables:
            # Sjekk etter kolonner som typisk indikerer en tropp
            if 'Club' in df.columns and 'Player' in df.columns:
                clubs = df['Club'].value_counts().to_dict()
                network_data[nation] = clubs
                found = True
                print(f"  Fant {len(clubs)} unike klubber for {nation}")
                break
            
            # Alternativ sjekk, noen ganger er kolonnenavnet annerledes
            elif 'Club' in df.columns and 'Name' in df.columns:
                clubs = df['Club'].value_counts().to_dict()
                network_data[nation] = clubs
                found = True
                print(f"  Fant {len(clubs)} unike klubber for {nation} (brukte 'Name')")
                break
                
        if not found:
            print(f"  ADVARSEL: Fant ikke klubb-tabell for {nation}!")
            
    except Exception as e:
        print(f"  FEIL ved henting av {nation}: {e}")
        
    # Unngå å spamme Wikipedia
    time.sleep(0.5)

print("\nFerdig! Lagrer data.json...")
with open('data.json', 'w') as f:
    json.dump(network_data, f, indent=4)
print("data.json lagret vellykket.")
