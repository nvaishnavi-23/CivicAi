/**
 * Main JavaScript file for CivicAI
 * Handles common interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    loadDashboardStats();
});

/**
 * Initialize page elements
 */
function initializeElements() {
    // Close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });

    // Highlight active menu item
    const currentLocation = location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    menuLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });

    // Image preview
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            previewImage(this);
        });
    });

    // Dismiss alerts
    const closeButtons = document.querySelectorAll('[data-dismiss="alert"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.alert').style.display = 'none';
        });
    });
}

/**
 * Validate form fields
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }

        // Email validation
        if (field.type === 'email') {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                field.classList.add('is-invalid');
                isValid = false;
            }
        }

        // Minimum length validation
        if (field.dataset.minLength) {
            if (field.value.length < parseInt(field.dataset.minLength)) {
                field.classList.add('is-invalid');
                isValid = false;
            }
        }
    });

    return isValid;
}

/**
 * Preview image before upload
 */
function previewImage(input) {
    const preview = document.querySelector('[data-preview="image"]');
    if (!preview) return;

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = `
                <div class="image-preview" style="margin-top: 1rem;">
                    <img src="${e.target.result}" alt="Preview" style="max-width: 200px; border-radius: 0.5rem;">
                    <p style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                        Image selected: ${input.files[0].name}
                    </p>
                </div>
            `;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Load dashboard statistics via API
 */
function loadDashboardStats() {
    const statsContainer = document.querySelector('[data-stats]');
    if (!statsContainer) return;

    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            // Update stats in UI if elements exist
            const elements = {
                'total': document.querySelector('[data-stat="total"]'),
                'pending': document.querySelector('[data-stat="pending"]'),
                'in_progress': document.querySelector('[data-stat="in_progress"]'),
                'resolved': document.querySelector('[data-stat="resolved"]')
            };

            for (let [key, element] of Object.entries(elements)) {
                if (element && data[key] !== undefined) {
                    element.textContent = data[key];
                }
            }
        })
        .catch(error => console.error('Error loading stats:', error));
}

/**
 * Show/hide loading spinner
 */
function showSpinner() {
    let spinner = document.querySelector('.spinner');
    if (!spinner) {
        spinner = document.createElement('div');
        spinner.className = 'spinner';
        document.body.appendChild(spinner);
    }
    spinner.style.display = 'block';
}

function hideSpinner() {
    const spinner = document.querySelector('.spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

/**
 * Get GPS coordinates
 */
function getGPSLocation() {
    if (navigator.geolocation) {
        showSpinner();
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;

                // Fill form fields
                const latInput = document.querySelector('input[name="latitude"]');
                const lonInput = document.querySelector('input[name="longitude"]');

                if (latInput) latInput.value = latitude.toFixed(6);
                if (lonInput) lonInput.value = longitude.toFixed(6);

                hideSpinner();
                showAlert('Location detected successfully!', 'success');
            },
            function(error) {
                hideSpinner();
                showAlert('Unable to get location. Please enter manually.', 'warning');
            }
        );
    } else {
        showAlert('Geolocation not supported', 'warning');
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    document.body.insertBefore(alertDiv, document.body.firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Format date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Format time
 */
function formatTime(dateString) {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleTimeString('en-US', options);
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    });
}

/**
 * Logout function
 */
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

/**
 * Export table to CSV
 */
function exportTableToCSV(tableElement, filename = 'export.csv') {
    let csv = [];
    const rows = tableElement.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        cols.forEach(col => {
            csvRow.push('"' + col.textContent.trim() + '"');
        });
        csv.push(csvRow.join(','));
    });

    downloadCSV(csv.join('\n'), filename);
}

/**
 * Download CSV file
 */
function downloadCSV(csv, filename) {
    const link = document.createElement('a');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}