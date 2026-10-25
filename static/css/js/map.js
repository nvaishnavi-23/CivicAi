/**
 * Map functionality for CivicAI
 * Uses Leaflet.js and OpenStreetMap
 */

let map;
let markers = [];
let heatmapData = [];

const MAP_DEFAULT_LAT = 28.6139;
const MAP_DEFAULT_LON = 77.2090;
const MAP_DEFAULT_ZOOM = 13;

/**
 * Initialize map
 */
function initializeMap(elementId = 'map') {
    const mapElement = document.getElementById(elementId);
    if (!mapElement) return;

    // Create map
    map = L.map(elementId).setView([MAP_DEFAULT_LAT, MAP_DEFAULT_LON], MAP_DEFAULT_ZOOM);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Load complaints
    loadComplaintsOnMap();

    // Add map click event
    map.on('click', function(e) {
        handleMapClick(e);
    });
}

/**
 * Load complaints and display on map
 */
function loadComplaintsOnMap() {
    fetch('/api/complaints/map')
        .then(response => response.json())
        .then(complaints => {
            displayComplaints(complaints);
        })
        .catch(error => console.error('Error loading complaints:', error));
}

/**
 * Display complaints as markers
 */
function displayComplaints(complaints) {
    // Clear existing markers
    markers.forEach(marker => marker.remove());
    markers = [];
    heatmapData = [];

    complaints.forEach(complaint => {
        if (complaint.latitude && complaint.longitude) {
            // Add marker
            const marker = addMarker(complaint);
            markers.push(marker);

            // Add to heatmap data
            heatmapData.push([
                complaint.latitude,
                complaint.longitude,
                getPriorityWeight(complaint.priority)
            ]);
        }
    });

    // Show heatmap if data available
    if (heatmapData.length > 0) {
        showHeatmap();
    }
}

/**
 * Add marker to map
 */
function addMarker(complaint) {
    const priorityColor = getPriorityColor(complaint.priority);
    const statusSymbol = getStatusSymbol(complaint.status);

    const markerHtml = `
        <div style="background: ${priorityColor}; color: white; width: 30px; height: 30px; 
                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                    font-weight: bold; border: 3px solid white;">
            ${statusSymbol}
        </div>
    `;

    const customMarker = L.divIcon({
        html: markerHtml,
        iconSize: [36, 36],
        className: 'custom-marker'
    });

    const marker = L.marker([complaint.latitude, complaint.longitude], {
        icon: customMarker
    }).addTo(map);

    // Popup content
    const popupContent = `
        <div style="width: 250px;">
            <h6 style="margin-bottom: 0.5rem;">${complaint.complaint_id}</h6>
            <p style="margin-bottom: 0.5rem;"><strong>${complaint.title}</strong></p>
            <p style="margin-bottom: 0.5rem; font-size: 0.9rem;">${complaint.category}</p>
            <div style="margin-bottom: 0.5rem;">
                <span class="badge priority-${complaint.priority.toLowerCase()}" 
                      style="margin-right: 0.5rem;">${complaint.priority}</span>
                <span class="badge status-${complaint.status.toLowerCase().replace(' ', '-')}">${complaint.status}</span>
            </div>
            <p style="margin-bottom: 0.5rem; font-size: 0.85rem; color: #666;">
                📍 ${complaint.address}
            </p>
            <a href="/admin/complaint/${complaint.complaint_id}" class="btn btn-sm btn-primary" 
               style="width: 100%; margin-top: 0.5rem;">View Details</a>
        </div>
    `;

    marker.bindPopup(popupContent);

    return marker;
}

/**
 * Get priority color for marker
 */
function getPriorityColor(priority) {
    const colors = {
        'Low': '#10b981',
        'Medium': '#f59e0b',
        'High': '#ef4444',
        'Critical': '#7c3aed'
    };
    return colors[priority] || '#6b7280';
}

/**
 * Get priority weight for heatmap
 */
function getPriorityWeight(priority) {
    const weights = {
        'Low': 1,
        'Medium': 2,
        'High': 3,
        'Critical': 4
    };
    return weights[priority] || 1;
}

/**
 * Get status symbol
 */
function getStatusSymbol(status) {
    const symbols = {
        'Submitted': '📋',
        'Assigned': '👤',
        'In Progress': '⚙️',
        'Resolved': '✓',
        'Rejected': '✗'
    };
    return symbols[status] || '?';
}

/**
 * Show heatmap layer
 */
function showHeatmap() {
    // Remove existing heatmap
    const existingHeatmap = document.querySelector('.leaflet-heatmap-pane');
    if (existingHeatmap) {
        existingHeatmap.remove();
    }

    // Create simple heatmap using circles
    heatmapData.forEach(point => {
        const radius = point[2] * 30; // Scale radius based on priority
        const color = getHeatmapColor(point[2]);

        L.circle([point[0], point[1]], {
            radius: radius,
            color: color,
            fillColor: color,
            fillOpacity: 0.1,
            weight: 2,
            opacity: 0.3
        }).addTo(map);
    });
}

/**
 * Get heatmap color based on intensity
 */
function getHeatmapColor(intensity) {
    if (intensity >= 4) return '#7c3aed'; // Critical - purple
    if (intensity >= 3) return '#ef4444'; // High - red
    if (intensity >= 2) return '#f59e0b'; // Medium - orange
    return '#10b981'; // Low - green
}

/**
 * Handle map click
 */
function handleMapClick(e) {
    const lat = e.latlng.lat.toFixed(6);
    const lon = e.latlng.lng.toFixed(6);

    // Fill coordinates in form if available
    const latInput = document.querySelector('input[name="latitude"]');
    const lonInput = document.querySelector('input[name="longitude"]');

    if (latInput) latInput.value = lat;
    if (lonInput) lonInput.value = lon;

    // Show temporary marker
    const marker = L.marker([lat, lon], {
        icon: L.icon({
            iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%231e40af"><path d="M12 2C7.58 2 4 5.58 4 10c0 5.25 8 13 8 13s8-7.75 8-13c0-4.42-3.58-8-8-8zm0 11c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/></svg>',
            iconSize: [24, 24]
            }
        })
    }).addTo(map);

    setTimeout(() => map.removeLayer(marker), 3000);
}

/**
 * Filter complaints on map
 */
function filterComplaints(filterType, filterValue) {
    fetch(`/api/complaints/map?${filterType}=${filterValue}`)
        .then(response => response.json())
        .then(complaints => {
            displayComplaints(complaints);
        })
        .catch(error => console.error('Error filtering complaints:', error));
}

/**
 * Center map on complaint
 */
function centerMapOnComplaint(latitude, longitude) {
    if (map && latitude && longitude) {
        map.setView([latitude, longitude], 15);
    }
}