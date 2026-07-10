import streamlit as st
import pandas as pd
import numpy as np
import math
import networkx as nx
import plotly.graph_objects as go
from itertools import combinations

import json

st.set_page_config(page_title="Fotballens Makrostruktur", layout="wide")
st.title("⚽️ Fotballens Makrostruktur: Nettverk og Entropi")

dataset_choice = st.radio(
    "Velg Datasett:", 
    ["Nåværende tropper (Utvidet mot 2026)", "VM 2022 (Faktiske lag)"], 
    horizontal=True
)

if "2026" in dataset_choice:
    with open("data_2026.json", "r") as f:
        data = json.load(f)
else:
    with open("data_2022.json", "r") as f:
        data = json.load(f)

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

tab1, tab2, tab3 = st.tabs(["Nettverksgraf (Cosinus-likhet)", "Entropi (Effektive Ligaer)", "Klubbrepresentasjon"])

# --- TAB 1: NETTVERKSGRAF ---
with tab1:
    st.markdown("### Nettverksanalyse av landslag basert på klubb-overlapp")
    
    # Session state for layout seed
    if 'layout_seed' not in st.session_state:
        st.session_state.layout_seed = 42
        
    col1, col2 = st.columns([3, 1])
    with col1:
        threshold = st.slider("Cosinus-likhet terskel", 0.0, 0.5, 0.15, 0.05)
    with col2:
        st.write("") # Spacing
        st.write("") # Spacing
        if st.button("Tegn graf på nytt 🎲"):
            st.session_state.layout_seed = np.random.randint(0, 100000)
    
    # Bygg en liste av alle unike klubber for å lage vektorer
    all_clubs = set()
    for nation, clubs in data.items():
        all_clubs.update(clubs.keys())
        
    # Fjern klubbløse spillere fra vektorrommet slik at de ikke skaper falske koblinger
    if "Unattached" in all_clubs:
        all_clubs.remove("Unattached")
    if "Free agent" in all_clubs:
        all_clubs.remove("Free agent")
        
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
    pos = nx.spring_layout(G_full, seed=st.session_state.layout_seed, k=0.9, iterations=100)

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
        
        # Legger til usynlige treffpunkter langs hele kanten (25%, 50%, 75%) for mye enklere hover
        shared = set(data[n1].keys()).intersection(set(data[n2].keys()))
        shared -= {"Unattached", "Free agent"}
        
        shared_details = []
        for c in shared:
            shared_details.append(f"{c} ({data[n1][c]} + {data[n2][c]})")
        shared_str = "<br>".join(shared_details) if shared_details else "Ingen (svak kosinus-likhet)"
        hover_string = f"<b>{n1} & {n2}</b><br>Felles klubber:<br>{shared_str}"
        
        for fraction in [0.25, 0.5, 0.75]:
            edge_hover_x.append(x0 + (x1 - x0) * fraction)
            edge_hover_y.append(y0 + (y1 - y0) * fraction)
            edge_hover_text.append(hover_string)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=3.5, color='rgba(136, 136, 136, 0.3)'), # Senket alpha til 0.3 for enda bedre lesbarhet
        hoverinfo='none',
        mode='lines')

    edge_hover_trace = go.Scatter(
        x=edge_hover_x, y=edge_hover_y,
        mode='markers',
        marker=dict(size=25, color='rgba(0,0,0,0)'),
        hovertext=edge_hover_text,
        hoverinfo='text'
    )

    # Finn valgt klynge (hvis brukeren har klikket på en node)
    selected_curve = None
    if "network_graph" in st.session_state and "selection" in st.session_state.network_graph:
        points = st.session_state.network_graph["selection"].get("points", [])
        if points:
            selected_curve = points[0].get("curveNumber")

    node_traces = []
    # Sorterer klyngene etter det landet i klyngen som har flest koblinger (samme logikk som listen under grafen)
    sorted_communities_for_plot = sorted(communities, key=lambda comm: max([G.degree(n) for n in comm]), reverse=True)
    
    for i, comm in enumerate(sorted_communities_for_plot):
        comm_nodes = list(comm)
        comm_x = [pos[n][0] for n in comm_nodes]
        comm_y = [pos[n][1] for n in comm_nodes]
        comm_text = [f"<b>{n}</b>" for n in comm_nodes]
        
        comm_hover = []
        for n in comm_nodes:
            top_clubs = sorted(
                data[n].items(), 
                key=lambda x: (x[1], x[0] not in ["Unattached", "Free agent"]), 
                reverse=True
            )[:5]
            clubs_str = "<br>".join([f"{c}: {cnt}" for c, cnt in top_clubs])
            comm_hover.append(f"<b>{n}</b><br>Betweenness: {centrality[n]:.3f}<br><br><b>Topp 5 Klubber:</b><br>{clubs_str}")
            
        color = colors[i % len(colors)]
        
        # Sjekk om en klynge er klikket på. Trace 0 er kanter, trace 1 er hover-kanter, så node_traces starter på 2.
        trace_index = i + 2
        opacity = 1.0
        if selected_curve is not None and selected_curve >= 2:
            if trace_index != selected_curve:
                opacity = 0.1  # Ton ned andre klynger
        
        trace = go.Scatter(
            x=comm_x, y=comm_y,
            mode='markers+text',
            text=comm_text,
            textposition="bottom center",
            hovertext=comm_hover,
            hoverinfo='text',
            name=f"Klynge {i+1}",
            legendgroup=f"Klynge {i+1}",
            marker=dict(size=20, color=color, opacity=opacity, line=dict(width=1, color='white'))
        )
        node_traces.append(trace)

    fig = go.Figure(data=[edge_trace, edge_hover_trace] + node_traces,
             layout=go.Layout(
                showlegend=True,
                hovermode='closest',
                dragmode=False, # Slår av dra-for-å-zoome/panorere for mobilvennlig scrolling
                height=750,  # Økt høyde for å gi grafen mer pusterom
                margin=dict(b=20,l=20,r=20,t=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True))
                )
    st.plotly_chart(fig, width='stretch', config={'scrollZoom': False, 'displayModeBar': False}, on_select="rerun", selection_mode="points", key="network_graph")
    
    st.markdown("#### Klynger (Communities)")
    st.write("Her er landene delt inn i sine respektive klynger. Klyngene og landene er sortert etter 'ren sentralitet' (Degree Centrality – altså antall direkte koblinger til andre land i nettverket):")
    
    # Sorterer klyngene etter det landet i klyngen som har flest koblinger
    sorted_communities = sorted(communities, key=lambda comm: max([G.degree(n) for n in comm]), reverse=True)
    
    for i, comm in enumerate(sorted_communities):
        # Sorterer landene internt i klyngen etter antall koblinger (gradsentralitet)
        sorted_nodes = sorted(list(comm), key=lambda n: G.degree(n), reverse=True)
        node_strs = [f"{n} ({G.degree(n)} koblinger)" for n in sorted_nodes]
        st.markdown(f"**Klynge {i+1}:** {', '.join(node_strs)}")
    
    st.markdown("#### Topp brobyggere (Betweenness Centrality)")
    st.write("Måler hvor ofte et land opptrer som det korteste bindeleddet mellom to andre land i nettverket.")
    cent_df = pd.DataFrame(list(centrality.items()), columns=["Nasjon", "Centrality"]).sort_values(by="Centrality", ascending=False)
    
    fig_bar = go.Figure(data=[go.Bar(x=cent_df["Nasjon"], y=cent_df["Centrality"], marker_color='lightblue')])
    fig_bar.update_layout(
        margin=dict(l=0, r=0, t=30, b=0), 
        xaxis_title="", 
        yaxis_title="Betweenness Centrality",
        dragmode=False,
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True)
    )
    st.plotly_chart(fig_bar, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})

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

# --- TAB 3: KLUBBREPRESENTASJON ---
with tab3:
    st.markdown("### Klubber med flest spillere i mesterskapet")
    st.write("Dette viser hvilke klubber som har flest representanter på tvers av alle landslagene i valgt datasett.")
    
    # Aggreger alle klubber
    club_totals = {}
    for nation, clubs in data.items():
        for club, count in clubs.items():
            if club not in ["Unattached", "Free agent"]:
                club_totals[club] = club_totals.get(club, 0) + count
                
    # Sorter
    sorted_clubs = sorted(club_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Valg for hvor mange klubber man vil se
    top_limit = st.slider("Vis antall klubber:", 10, 50, 20, 5)
    top_clubs = sorted_clubs[:top_limit]
    
    df_clubs = pd.DataFrame(top_clubs, columns=["Klubb", "Antall spillere"])
    
    # Bruk Plotly for et pent liggende stolpediagram
    fig_clubs = px.bar(
        df_clubs, 
        x="Antall spillere", 
        y="Klubb", 
        orientation='h', 
        color="Antall spillere", 
        color_continuous_scale="Blues"
    )
    fig_clubs.update_layout(
        yaxis={'categoryorder':'total ascending'}, 
        height=max(400, top_limit * 30),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_clubs, use_container_width=True)
