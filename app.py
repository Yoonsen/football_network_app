import streamlit as st
import pandas as pd
import numpy as np
import math
import networkx as nx
import plotly.graph_objects as go
from itertools import combinations

# --- DATA ---
data = {
  "Norge": {
    "Manchester City": 2, "Arsenal": 1, "Atletico Madrid": 1, "Bodø/Glimt": 1, 
    "Bologna": 1, "Borussia Dortmund": 1, "Brentford": 1, "Fulham": 1, 
    "RB Leipzig": 1, "Sevilla": 1, "Wolves": 1
  },
  "England": {
    "Arsenal": 2, "Manchester City": 2, "Aston Villa": 1, "Bayer Leverkusen": 1, 
    "Bayern München": 1, "Everton": 1, "Newcastle United": 1, "Nottingham Forest": 1, 
    "Real Madrid": 1
  },
  "Argentina": {
    "Atlético Madrid": 4, "Inter Miami CF": 2, "Olympique Marseille": 2, "Aston Villa": 1, 
    "Bayer Leverkusen": 1, "Benfica": 1, "Botafogo": 1, "Bournemouth": 1, 
    "Brighton & Hove Albion": 1, "Chelsea": 1, "Inter Milan": 1, "Juventus": 1, 
    "Liverpool": 1, "Lyon": 1, "Manchester United": 1, "Real Betis": 1, 
    "Real Madrid": 1, "River Plate": 1, "Roma": 1, "SE Palmeiras": 1, "Tottenham Hotspur": 1
  },
  "Spania": {
    "Barcelona": 8, "Arsenal": 3, "Athletic Bilbao": 3, "Atletico Madrid": 3, 
    "Bayer Leverkusen": 1, "Celta Vigo": 1, "Chelsea": 1, "Crystal Palace": 1, 
    "Manchester City": 1, "Osasuna": 1, "PSG": 1, "Real Sociedad": 1, "Tottenham Hotspur": 1
  },
  "Belgia": {
    "Club Brugge KV": 3, "LOSC Lille": 3, "AC Milan": 2, "Aston Villa": 2, 
    "SSC Napoli": 2, "Arsenal": 1, "Atalanta BC": 1, "Brighton & Hove Albion": 1, 
    "Chelsea": 1, "Eintracht Frankfurt": 1, "Fulham": 1, "Girona FC": 1, 
    "Manchester City": 1, "Manchester United": 1, "Rangers F.C.": 1, 
    "RC Strasbourg Alsace": 1, "Real Madrid": 1, "S.L. Benfica": 1, "Sporting CP": 1
  },
  "Frankrike": {
    "Bayern München": 4, "Real Madrid": 3, "AC Milan": 2, "Juventus": 2,
    "Barcelona": 2, "PSG": 2, "Arsenal": 1, "Tottenham Hotspur": 1,
    "Atletico Madrid": 1, "Manchester United": 1, "Liverpool": 1,
    "Eintracht Frankfurt": 1, "Monaco": 1, "Olympique Marseille": 1, "Rennes": 1
  },
  "Brasil": {
    "Real Madrid": 3, "Juventus": 3, "Manchester United": 3, "Arsenal": 2,
    "Chelsea": 1, "Tottenham Hotspur": 1, "Liverpool": 2, "PSG": 2,
    "Barcelona": 1, "Newcastle United": 1, "West Ham": 1, "Flamengo": 2,
    "SE Palmeiras": 1, "Sevilla": 1
  },
  "Portugal": {
    "Manchester City": 3, "Manchester United": 2, "Wolves": 3, "PSG": 3,
    "Porto": 3, "S.L. Benfica": 2, "Sporting CP": 1, "AC Milan": 1,
    "RB Leipzig": 1, "Fulham": 1, "Atletico Madrid": 1, "Borussia Dortmund": 1
  },
  "Nederland": {
    "Ajax": 7, "PSV": 3, "Barcelona": 2, "Bayern München": 2, "Inter Milan": 2,
    "Liverpool": 1, "Manchester City": 1, "Manchester United": 1, "Atalanta BC": 1,
    "Bayer Leverkusen": 1, "Club Brugge KV": 1
  },
  "Sveits": {
    "Borussia Mönchengladbach": 3, "Torino": 2, "Arsenal": 1, "Bayer Leverkusen": 1,
    "Manchester City": 1, "Chelsea": 1, "Monaco": 2, "Bologna": 2, "Inter Milan": 1
  },
  "Polen": {
    "Juventus": 2, "SSC Napoli": 1, "Barcelona": 1, "Aston Villa": 1, 
    "Arsenal": 1, "Roma": 1, "Feyenoord": 1, "RC Lens": 1
  },
  "USA": {
    "Chelsea": 1, "Juventus": 2, "AC Milan": 1, "PSV": 1, "Fulham": 2, 
    "Borussia Dortmund": 1, "Crystal Palace": 1, "Bournemouth": 1
  },
  "Senegal": {
    "Chelsea": 1, "Everton": 1, "Tottenham Hotspur": 1, "Bayern München": 1, 
    "Olympique Marseille": 2, "Monaco": 1, "Nottingham Forest": 1
  },
  "Kroatia": {
    "Dinamo Zagreb": 4, "Real Madrid": 1, "Chelsea": 1, "Tottenham Hotspur": 1,
    "Inter Milan": 1, "Atalanta BC": 1, "RB Leipzig": 1, "Rennes": 1,
    "Osasuna": 1, "VfL Wolfsburg": 1, "Torino": 1, "Sassuolo": 1
  },
  "Marokko": {
    "Sevilla": 2, "Angers SCO": 2, "PSG": 1, "Chelsea": 1, "Bayern München": 1,
    "Fiorentina": 1, "Toulouse": 1, "Sampdoria": 1, "Standard Liège": 1,
    "Besiktas": 1, "Wydad AC": 3
  },
  "Japan": {
    "Celtic": 3, "Brighton & Hove Albion": 1, "Arsenal": 1, "Real Sociedad": 1,
    "SC Freiburg": 1, "Eintracht Frankfurt": 1, "VfL Bochum": 1, "Sporting CP": 1,
    "Monaco": 1
  },
  "Australia": {
    "Celtic": 2, "Heart of Midlothian": 2, "FC St. Pauli": 1, "Hellas Verona": 1,
    "Middlesbrough": 1, "Cádiz CF": 1, "FC Copenhagen": 1
  },
  "Sør-Korea": {
    "Tottenham Hotspur": 1, "Wolves": 1, "Bayern München": 1, "PSG": 1,
    "FSV Mainz 05": 1, "FC Midtjylland": 1, "Napoli": 1, "Olympiacos": 1
  },
  "Elfenbenskysten": {
    "Nottingham Forest": 2, "Roma": 1, "Borussia Dortmund": 1, "Galatasaray": 1,
    "Sporting CP": 1, "Bayer Leverkusen": 1, "Brighton & Hove Albion": 1,
    "Manchester United": 1, "Monaco": 1
  }
}

# Hjelpefunksjon for å kartlegge klubb til liga
def get_league(club):
    premier_league = [
        "Manchester City", "Arsenal", "Brentford", "Fulham", "Wolves", "Aston Villa", 
        "Everton", "Newcastle United", "Nottingham Forest", "Bournemouth", "Brighton & Hove Albion", 
        "Chelsea", "Liverpool", "Tottenham Hotspur", "Manchester United", "Crystal Palace", "West Ham", "QPR"
    ]
    la_liga = [
        "Atletico Madrid", "Atlético Madrid", "Sevilla", "Real Madrid", "Real Betis", "Barcelona", 
        "Athletic Bilbao", "Celta Vigo", "Osasuna", "Real Sociedad", "Girona FC"
    ]
    serie_a = [
        "Bologna", "Inter Milan", "Juventus", "Roma", "AC Milan", "SSC Napoli", "Atalanta BC", "Torino", "Fiorentina"
    ]
    bundesliga = [
        "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "Bayern München", "Eintracht Frankfurt", "Hoffenheim"
    ]
    ligue_1 = [
        "Olympique Marseille", "Lyon", "PSG", "LOSC Lille", "RC Strasbourg Alsace", "Rennes", "Monaco", "Angers", "Toulouse"
    ]
    eredivisie = ["Ajax", "PSV"]
    primeira_liga = ["Porto", "Benfica", "S.L. Benfica", "Sporting CP"]
    
    if club in premier_league: return "Premier League"
    if club in la_liga: return "La Liga"
    if club in serie_a: return "Serie A"
    if club in bundesliga: return "Bundesliga"
    if club in ligue_1: return "Ligue 1"
    if club in eredivisie: return "Eredivisie"
    if club in primeira_liga: return "Primeira Liga"
    return "Resten av verden"

st.set_page_config(page_title="Fotballens Makrostruktur", layout="wide")
st.title("⚽️ Fotballens Makrostruktur: Nettverk og Entropi")

tab1, tab2 = st.tabs(["Nettverksgraf (Cosinus-likhet)", "Entropi (Effektive Ligaer)"])

# --- TAB 1: NETTVERKSGRAF ---
with tab1:
    st.markdown("### Nettverksanalyse av landslag basert på klubb-overlapp")
    threshold = st.slider("Cosinus-likhet terskel", 0.0, 0.5, 0.1, 0.05)
    
    # Bygg en liste av alle unike klubber for å lage vektorer
    all_clubs = set()
    for nation, clubs in data.items():
        all_clubs.update(clubs.keys())
    all_clubs = list(all_clubs)
    
    # Lag vektorer
    vectors = {}
    for nation, clubs in data.items():
        vec = np.zeros(len(all_clubs))
        for i, club in enumerate(all_clubs):
            vec[i] = clubs.get(club, 0)
        vectors[nation] = vec

    def cosine_similarity(v1, v2):
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        return dot / norm if norm > 0 else 0

    # Bygg graf med ALLE kanter for å beregne faste posisjoner (unngår krasj og hopping)
    G_full = nx.Graph()
    G_full.add_nodes_from(data.keys())
    for n1, n2 in combinations(data.keys(), 2):
        sim = cosine_similarity(vectors[n1], vectors[n2])
        if sim > 0:
            G_full.add_edge(n1, n2, weight=sim)
            
    # k-parameteren gir mer "frastøtning" mellom nodene slik at de får mer plass
    pos = nx.spring_layout(G_full, seed=42, k=0.6, iterations=100)

    # Bygg den faktiske grafen for den valgte terskelen
    G = nx.Graph()
    G.add_nodes_from(data.keys())
        
    for n1, n2 in combinations(data.keys(), 2):
        sim = cosine_similarity(vectors[n1], vectors[n2])
        if sim >= threshold:
            G.add_edge(n1, n2, weight=sim)

    from networkx.algorithms.community import louvain_communities
    import plotly.express as px

    # Beregn Betweenness Centrality på den filtrerte grafen
    centrality = nx.betweenness_centrality(G)
    
    # Beregn Louvain communities (klynger) for fargelegging
    if len(G.edges()) > 0:
        communities = louvain_communities(G, seed=42)
    else:
        communities = [{n} for n in G.nodes()]
        
    colors = px.colors.qualitative.Pastel
    node_colors = []
    for node in G.nodes():
        for i, comm in enumerate(communities):
            if node in comm:
                node_colors.append(colors[i % len(colors)])
                break
    
    edge_x, edge_y, edge_weights = [], [], []
    edge_hover_x, edge_hover_y, edge_hover_text = [], [], []
    
    for edge in G.edges(data=True):
        n1, n2 = edge[0], edge[1]
        x0, y0 = pos[n1]
        x1, y1 = pos[n2]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_weights.append(edge[2]['weight'])
        
        # Midpoint for hover
        edge_hover_x.append((x0 + x1) / 2)
        edge_hover_y.append((y0 + y1) / 2)
        
        # Finn felles klubber
        shared = set(data[n1].keys()).intersection(set(data[n2].keys()))
        shared_details = []
        for c in shared:
            shared_details.append(f"{c} ({data[n1][c]} + {data[n2][c]})")
            
        shared_str = "<br>".join(shared_details) if shared_details else "Ingen (svak kosinus-likhet)"
        edge_hover_text.append(f"<b>{n1} & {n2}</b><br>Felles klubber:<br>{shared_str}")

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines')

    edge_hover_trace = go.Scatter(
        x=edge_hover_x, y=edge_hover_y,
        mode='markers',
        marker=dict(size=14, color='rgba(0,0,0,0)'),
        hovertext=edge_hover_text,
        hoverinfo='text'
    )

    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_text = list(G.nodes())
    
    hover_text = []
    for n in G.nodes():
        top_clubs = sorted(data[n].items(), key=lambda x: x[1], reverse=True)[:4]
        clubs_str = "<br>".join([f"{c}: {cnt}" for c, cnt in top_clubs])
        hover_text.append(f"<b>{n}</b><br>Betweenness: {centrality[n]:.3f}<br><br><b>Toppklubber:</b><br>{clubs_str}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="bottom center",
        hovertext=hover_text,
        hoverinfo='text',
        marker=dict(size=40, color=node_colors, line=dict(width=2, color='white')))

    fig = go.Figure(data=[edge_trace, edge_hover_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                height=750,  # Økt høyde for å gi grafen mer pusterom
                margin=dict(b=20,l=20,r=20,t=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("#### Klynger (Communities)")
    st.write("Her er landene delt inn i sine respektive klynger. Klyngene og landene er sortert etter 'ren sentralitet' (Degree Centrality – altså antall direkte koblinger til andre land i nettverket):")
    
    # Sorterer klyngene etter det landet i klyngen som har flest koblinger
    sorted_communities = sorted(communities, key=lambda comm: max([G.degree(n) for n in comm]), reverse=True)
    
    for i, comm in enumerate(sorted_communities):
        # Sorterer landene internt i klyngen etter antall koblinger (gradsentralitet)
        sorted_nodes = sorted(list(comm), key=lambda n: G.degree(n), reverse=True)
        node_strs = [f"{n} ({G.degree(n)} koblinger)" for n in sorted_nodes]
        st.markdown(f"**Klynge {i+1}:** {', '.join(node_strs)}")
    
    st.markdown("#### Topp brokbyggere (Betweenness Centrality)")
    st.write("Måler hvor ofte et land opptrer som det korteste bindeleddet mellom to andre land i nettverket.")
    cent_df = pd.DataFrame(list(centrality.items()), columns=["Nasjon", "Centrality"]).sort_values(by="Centrality", ascending=False)
    
    fig_bar = go.Figure(data=[go.Bar(x=cent_df["Nasjon"], y=cent_df["Centrality"], marker_color='lightblue')])
    fig_bar.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis_title="", yaxis_title="Betweenness Centrality")
    st.plotly_chart(fig_bar, width='stretch')

# --- TAB 2: ENTROPI ---
with tab2:
    st.markdown("### Beregning av Shannon-entropi og $2^H$")
    
    selected_nations = st.multiselect("Velg nasjoner som skal inkluderes:", list(data.keys()), default=list(data.keys()))
    
    if selected_nations:
        league_counts = {}
        total_players = 0
        
        for nation in selected_nations:
            for club, count in data[nation].items():
                league = get_league(club)
                league_counts[league] = league_counts.get(league, 0) + count
                total_players += count
                
        # Beregn entropi
        entropy = 0
        probabilities = []
        labels = []
        for league, count in league_counts.items():
            p = count / total_players
            probabilities.append(p)
            labels.append(f"{league} ({count} spillere)")
            if p > 0:
                entropy -= p * math.log2(p)
                
        effective_leagues = 2 ** entropy
        
        col1, col2 = st.columns(2)
        col1.metric("Shannon Entropi (H)", f"{entropy:.2f} bits")
        col2.metric("Effektive Ligaer (2^H)", f"{effective_leagues:.2f}")
        
        # Stolpediagram for fordeling
        df = pd.DataFrame({"Liga": list(league_counts.keys()), "Spillere": list(league_counts.values())}).sort_values(by="Spillere", ascending=False)
        st.bar_chart(df.set_index("Liga"))
    else:
        st.warning("Velg minst én nasjon for å beregne entropi.")
