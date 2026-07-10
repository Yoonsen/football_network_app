let network = null;
let nodesDataSet = new vis.DataSet();
let edgesDataSet = new vis.DataSet();
let rawData = { nodes: [], edges: [] };

const colors = [
    "#ff3366", // Cluster 0
    "#33ccff", // Cluster 1
    "#33ff99", // Cluster 2
    "#ffcc00", // Cluster 3
    "#cc66ff", // Cluster 4
    "#ff9933"  // Cluster 5
];

const domElements = {
    btn2026: document.getElementById('btn-2026'),
    btn2022: document.getElementById('btn-2022'),
    slider: document.getElementById('threshold-slider'),
    thresholdVal: document.getElementById('threshold-val'),
    container: document.getElementById('mynetwork'),
    detailsPanel: document.getElementById('details-panel'),
    detailTitle: document.getElementById('detail-title'),
    detailContent: document.getElementById('detail-content')
};

// Initialize
async function init() {
    setupListeners();
    await loadDataset('graph_2026.json');
}

function setupListeners() {
    domElements.btn2026.addEventListener('click', () => {
        domElements.btn2026.classList.add('active');
        domElements.btn2022.classList.remove('active');
        loadDataset('graph_2026.json');
    });

    domElements.btn2022.addEventListener('click', () => {
        domElements.btn2022.classList.add('active');
        domElements.btn2026.classList.remove('active');
        loadDataset('graph_2022.json');
    });

    domElements.slider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value).toFixed(2);
        domElements.thresholdVal.innerText = val;
    });

    domElements.slider.addEventListener('change', () => {
        updateGraphFromThreshold();
    });

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });
}

async function loadDataset(filename) {
    try {
        const response = await fetch(filename);
        rawData = await response.json();
        updateGraphFromThreshold();
    } catch (e) {
        console.error("Failed to load dataset", e);
    }
}

function renderLists(visNodes) {
    // Render Clusters
    const clusterContainer = document.getElementById('cluster-list-container');
    const clusters = {};
    visNodes.forEach(n => {
        if (!n.isSingleton) {
            if (!clusters[n.group]) clusters[n.group] = [];
            clusters[n.group].push(n.label);
        }
    });
    
    let clusterHtml = '';
    Object.keys(clusters).forEach(groupId => {
        clusterHtml += `<div class="cluster-block" style="border-left-color: ${colors[groupId % colors.length]}">
            <strong>Klynge ${parseInt(groupId) + 1}</strong>
            <p>${clusters[groupId].join(', ')}</p>
        </div>`;
    });
    clusterContainer.innerHTML = clusterHtml || '<p style="color:gray; font-size:13px">Ingen klynger ved denne terskelen.</p>';

    // Render Clubs
    const clubContainer = document.getElementById('club-list-container');
    let clubHtml = '';
    if (rawData.club_totals) {
        rawData.club_totals.slice(0, 50).forEach(c => {
            clubHtml += `<div class="club-item">
                <span>${c.club}</span>
                <span class="club-count">${c.count}</span>
            </div>`;
        });
    }
    clubContainer.innerHTML = clubHtml;
}

function updateGraphFromThreshold() {
    const threshold = parseFloat(domElements.slider.value);
    
    // Finn hvilke noder som er tilkoblet
    const filteredEdges = rawData.edges.filter(e => e.weight >= threshold);
    const connectedNodes = new Set();
    filteredEdges.forEach(e => {
        connectedNodes.add(e.from);
        connectedNodes.add(e.to);
    });

    // Tell antall singletons for å sentrere dem horisontalt
    let numSingletons = 0;
    rawData.nodes.forEach(n => {
        if (!connectedNodes.has(n.id)) numSingletons++;
    });
    
    // Start X slik at rekken blir sentrert rundt 0
    let singletonX = -(numSingletons * 80) / 2; 

    const visNodes = rawData.nodes.map(n => {
        const isSingleton = !connectedNodes.has(n.id);
        
        const color = isSingleton ? 'rgba(80, 80, 80, 0.8)' : colors[n.group % colors.length];
        const size = 15 + (n.betweenness * 50);
        
        let nodeConfig = {
            id: n.id,
            label: n.label,
            group: n.group,
            top_clubs: n.top_clubs,
            size: size,
            color: {
                background: color,
                border: '#ffffff',
                hover: { background: color, border: '#ffffff' },
                highlight: { background: color, border: '#ffffff' }
            },
            font: { color: '#ffffff', size: 14, strokeWidth: 0 },
            borderWidth: 1,
            shadow: true,
            originalColor: color,
            isSingleton: isSingleton,
            fixed: false
        };

        if (isSingleton) {
            nodeConfig.x = singletonX;
            nodeConfig.y = 400; // Nærmere sentrum så de ikke havner utenfor skjermen
            nodeConfig.fixed = { x: true, y: true };
            nodeConfig.size = 12;
            singletonX += 80;
        }

        return nodeConfig;
    });

    const visEdges = filteredEdges.map(e => ({
        id: `${e.from}-${e.to}`,
        from: e.from,
        to: e.to,
        value: e.weight,
        shared: e.shared,
        color: { color: 'rgba(255,255,255,0.2)', hover: 'rgba(255,255,255,0.8)', highlight: '#ffffff' },
        smooth: { type: 'continuous' }
    }));

    nodesDataSet.clear();
    edgesDataSet.clear();
    nodesDataSet.add(visNodes);
    edgesDataSet.add(visEdges);

    renderLists(visNodes);

    if (!network) {
        drawNetwork();
    } else {
        // La fysikken stabilisere seg et øyeblikk, og tving deretter kameraet til å vise alle nodene
        setTimeout(() => {
            network.fit({ animation: { duration: 1000, easingFunction: 'easeInOutQuad' } });
        }, 100);
    }
}

function drawNetwork() {
    const data = {
        nodes: nodesDataSet,
        edges: edgesDataSet
    };
    const options = {
        interaction: {
            hover: true,
            hoverConnectedEdges: false,
            selectConnectedEdges: false,
            tooltipDelay: 100,
            dragView: false,  // Skrur av panorering
            zoomView: false   // Skrur av zoom
        },
        physics: {
            forceAtlas2Based: {
                gravitationalConstant: -150,
                centralGravity: 0.01,
                springLength: 200,
                springConstant: 0.08,
                damping: 0.4
            },
            minVelocity: 0.75,
            solver: "forceAtlas2Based",
            stabilization: {
                iterations: 150,
                fit: true
            }
        },
        nodes: {
            shape: 'dot',
            scaling: { min: 10, max: 40 }
        },
        edges: {
            scaling: { min: 1, max: 5 }
        }
    };

    network = new vis.Network(domElements.container, data, options);

    // Event: Hover Node
    network.on("hoverNode", function (params) {
        const hoveredNodeId = params.node;
        const hoveredNode = nodesDataSet.get(hoveredNodeId);
        
        // Find cluster/group
        const clusterId = hoveredNode.group;

        // Dim everything except this cluster
        const updateArray = [];
        nodesDataSet.forEach((node) => {
            if (node.group !== clusterId) {
                updateArray.push({ id: node.id, color: { background: 'rgba(100,100,100,0.1)', border: 'rgba(100,100,100,0.1)' }, font: {color: 'rgba(255,255,255,0.2)'} });
            } else {
                updateArray.push({ id: node.id, color: { background: node.originalColor, border: '#ffffff' }, font: {color: '#ffffff'} });
            }
        });
        nodesDataSet.update(updateArray);

        // Dim all edges except those completely within the cluster
        const edgeUpdates = [];
        edgesDataSet.forEach((edge) => {
            const fromNode = nodesDataSet.get(edge.from);
            const toNode = nodesDataSet.get(edge.to);
            if (fromNode && toNode && fromNode.group === clusterId && toNode.group === clusterId) {
                edgeUpdates.push({ id: edge.id, color: { color: 'rgba(255,255,255,0.6)' } });
            } else {
                edgeUpdates.push({ id: edge.id, color: { color: 'rgba(255,255,255,0.05)' } });
            }
        });
        edgesDataSet.update(edgeUpdates);

        showNodeDetails(hoveredNode);
    });

    // Event: Blur Node
    network.on("blurNode", function (params) {
        resetStyles();
        hideDetails();
    });

    // Event: Hover Edge
    network.on("hoverEdge", function (params) {
        const edge = edgesDataSet.get(params.edge);
        showEdgeDetails(edge);
    });

    network.on("blurEdge", function (params) {
        hideDetails();
    });
}

function resetStyles() {
    const updateArray = [];
    nodesDataSet.forEach((node) => {
        updateArray.push({ id: node.id, color: { background: node.originalColor, border: '#ffffff' }, font: {color: '#ffffff'} });
    });
    nodesDataSet.update(updateArray);

    const edgeUpdates = [];
    edgesDataSet.forEach((edge) => {
        edgeUpdates.push({ id: edge.id, color: { color: 'rgba(255,255,255,0.2)' } });
    });
    edgesDataSet.update(edgeUpdates);
}

function showNodeDetails(node) {
    domElements.detailsPanel.classList.remove('hidden');
    domElements.detailTitle.innerText = node.label;
    
    let html = `<div><strong style="color:var(--text-secondary)">Klynge:</strong> ${node.group + 1}</div>`;
    html += `<div style="margin-top:16px; margin-bottom:8px; font-weight:bold; color:var(--text-secondary)">Topp 5 Klubber</div>`;
    
    node.top_clubs.forEach(c => {
        html += `<div class="club-item">
            <span>${c.club}</span>
            <span class="club-count">${c.count}</span>
        </div>`;
    });
    
    domElements.detailContent.innerHTML = html;
}

function showEdgeDetails(edge) {
    domElements.detailsPanel.classList.remove('hidden');
    domElements.detailTitle.innerText = `${edge.from} 🤝 ${edge.to}`;
    
    let html = `<div><strong style="color:var(--text-secondary)">Cosinus-likhet:</strong> ${edge.value.toFixed(3)}</div>`;
    html += `<div class="shared-edge-info"><strong>Felles klubber:</strong><br>`;
    
    edge.shared.forEach(c => {
        html += `<div class="club-item">
            <span>${c.club}</span>
            <span class="club-count">${c.count} x2</span>
        </div>`;
    });
    html += `</div>`;
    
    domElements.detailContent.innerHTML = html;
}

function hideDetails() {
    domElements.detailsPanel.classList.add('hidden');
}

// Start
init();

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then(registration => {
      console.log('SW registered: ', registration);
    }).catch(registrationError => {
      console.log('SW registration failed: ', registrationError);
    });
  });
}
