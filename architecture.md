# PWA Architecture Specification: Fotballens Makrostruktur

Dette dokumentet beskriver på et overordnet nivå hvordan Streamlit/Python-prototypen kan oversettes til en fullverdig, klientside Progressive Web App (PWA).

## 1. Hovedarkitektur (Client-Side Only)
Siden appen kun krever statiske data (en dictionary med nasjoner og klubber) og matematiske beregninger, kan hele appen kjøre lokalt i brukerens nettleser som en PWA. Dette eliminerer behovet for en backend-server.

*   **Hosting:** Statisk hosting (f.eks. GitHub Pages, Vercel, Netlify).
*   **PWA-funksjonalitet:** Implementeres via en Service Worker som cacher statiske ressurser og `manifest.json`, slik at appen kan installeres på mobil/desktop og fungere offline.

## 2. Teknologistakk
For å gjenskape funksjonaliteten fra Python-miljøet i JavaScript:

*   **Frontend-rammeverk:** React, Vue, Svelte, eller Vanilla JS (avhengig av preferanse).
*   **Nettverksanalyse (graf og matematikk):**
    *   *Grafstruktur og algoritmer:* **Graphology** (JS-bibliotek for grafer) eller **Cytoscape.js**. Graphology har innebygde funksjoner for Betweenness Centrality og Louvain community detection.
    *   *Matematikk (Cosinus-likhet):* Enkle JS-funksjoner (eller lette biblioteker som `mathjs`) for vektor-matematikk for å beregne cosinus-likhet mellom landene.
*   **Visualisering:**
    *   *Nettverksgraf:* **Sigma.js** (integrerer sømløst med Graphology og bruker WebGL for ekstrem ytelse) eller **Cytoscape.js** (fysikk-basert rendering og drag-and-drop).
    *   *Stolpediagram (Centrality):* **Chart.js** eller **Plotly.js** for responsivt design.
*   **Styling:** Tailwind CSS eller ren CSS for et responsivt, app-lignende mobilgrensesnitt.

## 3. Dataflyt
1.  **Initialisering:** JS-appen laster inn et statisk JSON-objekt med rådataene (land -> klubber -> antall spillere).
2.  **Vektorisering:** En intern funksjon bygger en liste over alle unike klubber og genererer tall-vektorer for hvert land (tilsvarende `np.zeros` logikken i Python).
3.  **Filtrering og Grafbygging:**
    *   Brukeren drar i en HTML-slider (terskel).
    *   JS filtrerer kantene basert på kosinus-likhet $\ge$ terskel.
    *   Bygger den interaktive grafstrukturen for rendering.
4.  **Analyse (Kalkulering):**
    *   Graphology / Cytoscape beregner Betweenness Centrality for de aktive nodene.
    *   Louvain-algoritmen kjøres for å oppdatere nodenes fargekode (community).
5.  **Rendering:** Nettverket og stolpediagrammet oppdateres reaktivt.

## 4. Fordeler med PWA-tilnærmingen
*   **Fysikk og Interaktivitet:** Ved å bruke Cytoscape.js/Sigma.js kan nodene gjøres fritt dra-bare ("draggable") med ekte fjærfysikk i nettleseren, noe som løser Plotly sine mobilbegrensninger.
*   **Ytelse:** Null server-latency; grafen oppdateres umiddelbart når brukeren drar i slideren.
*   **Tilgjengelighet:** Kan installeres som en app på hjemskjermen via `manifest.json`.
