import pandas as pd
import requests
import json
import io
import time

teams = {
    "Algeria": "Algeria_national_football_team",
    "Argentina": "Argentina_national_football_team",
    "Australia": "Australia_men%27s_national_soccer_team",
    "Austria": "Austria_national_football_team",
    "Belgium": "Belgium_national_football_team",
    "Bosnia and Herzegovina": "Bosnia_and_Herzegovina_national_football_team",
    "Brazil": "Brazil_national_football_team",
    "Canada": "Canada_men%27s_national_soccer_team",
    "Cape Verde": "Cape_Verde_national_football_team",
    "Colombia": "Colombia_national_football_team",
    "Croatia": "Croatia_national_football_team",
    "Cura\u00e7ao": "Cura\u00e7ao_national_football_team",
    "Czech Republic": "Czech_Republic_national_football_team",
    "DR Congo": "DR_Congo_national_football_team",
    "Ecuador": "Ecuador_national_football_team",
    "Egypt": "Egypt_national_football_team",
    "England": "England_national_football_team",
    "France": "France_national_football_team",
    "Germany": "Germany_national_football_team",
    "Ghana": "Ghana_national_football_team",
    "Haiti": "Haiti_national_football_team",
    "Iran": "Iran_national_football_team",
    "Iraq": "Iraq_national_football_team",
    "Ivory Coast": "Ivory_Coast_national_football_team",
    "Japan": "Japan_national_football_team",
    "Jordan": "Jordan_national_football_team",
    "Mexico": "Mexico_national_football_team",
    "Morocco": "Morocco_national_football_team",
    "Netherlands": "Netherlands_national_football_team",
    "New Zealand": "New_Zealand_men%27s_national_football_team",
    "Norway": "Norway_national_football_team",
    "Panama": "Panama_national_football_team",
    "Paraguay": "Paraguay_national_football_team",
    "Portugal": "Portugal_national_football_team",
    "Qatar": "Qatar_national_football_team",
    "Saudi Arabia": "Saudi_Arabia_national_football_team",
    "Scotland": "Scotland_national_football_team",
    "Senegal": "Senegal_national_football_team",
    "South Africa": "South_Africa_national_football_team",
    "South Korea": "South_Korea_national_football_team",
    "Spain": "Spain_national_football_team",
    "Sweden": "Sweden_national_football_team",
    "Switzerland": "Switzerland_national_football_team",
    "Tunisia": "Tunisia_national_football_team",
    "Turkey": "Turkey_national_football_team",
    "United States": "United_States_men%27s_national_soccer_team",
    "Uruguay": "Uruguay_national_football_team",
    "Uzbekistan": "Uzbekistan_national_football_team"
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
            player_col = None
            if 'Player' in df.columns:
                player_col = 'Player'
            elif 'Name' in df.columns:
                player_col = 'Name'
                
            if player_col and 'Club' in df.columns:
                df = df.dropna(subset=[player_col, 'Club'])
                
                # Hvis Caps finnes, bruk det for å finne de 14 beste
                if 'Caps' in df.columns:
                    df["CapsNum"] = pd.to_numeric(df["Caps"].astype(str).str.extract(r"(\d+)")[0], errors="coerce").fillna(0)
                    top_players = df.sort_values(by="CapsNum", ascending=False).head(14)
                else:
                    # Fallback hvis Caps mangler (sjelden)
                    top_players = df.head(14)
                    
                clubs = top_players['Club'].value_counts().to_dict()
                network_data[nation] = clubs
                found = True
                print(f"  Fant {len(clubs)} unike klubber i topp 14 for {nation}")
                break
                
        if not found:
            print(f"  ADVARSEL: Fant ikke klubb-tabell for {nation}!")
            
    except Exception as e:
        print(f"  FEIL ved henting av {nation}: {e}")
        
    # Unngå å spamme Wikipedia
    time.sleep(0.5)

print("\nFerdig! Lagrer data_2026.json...")
with open('data_2026.json', 'w') as f:
    json.dump(network_data, f, indent=4)
print("data_2026.json lagret vellykket.")
