// Main JavaScript for Quant Trading System

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Set current year in footer
    document.getElementById('current-year').textContent = new Date().getFullYear();
});

// Generic AJAX function
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            try {
                const response = JSON.parse(xhr.responseText);
                successCallback(response);
            } catch (e) {
                console.error('Error parsing JSON response:', e);
                if (errorCallback) errorCallback('Invalid response format');
            }
        } else {
            if (errorCallback) errorCallback('Request failed: ' + xhr.status);
        }
    };
    
    xhr.onerror = function() {
        if (errorCallback) errorCallback('Network error');
    };
    
    xhr.send(JSON.stringify(data));
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.getElementById('notification-toast');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true" id="notification-toast">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Add to DOM
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.innerHTML = toastHTML;
    document.body.appendChild(toastContainer);
    
    // Show toast
    const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
    toast.show();
    
    // Remove after hidden
    toastContainer.querySelector('.toast').addEventListener('hidden.bs.toast', function() {
        toastContainer.remove();
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY'
    }).format(amount);
}

// Format percentage
function formatPercentage(value) {
    return (value * 100).toFixed(2) + '%';
}

// Update element content
function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

// Update element HTML
function updateElementHTML(id, html) {
    const element = document.getElementById(id);
    if (element) {
        element.innerHTML = html;
    }
}

// Toggle element visibility
function toggleElement(id, show) {
    const element = document.getElementById(id);
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
}

// Add loading state to button
function setButtonLoading(button, loading) {
    if (loading) {
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        button.disabled = true;
    } else {
        // Restore original content
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
        button.disabled = false;
    }
}

// Save original button text
function saveButtonOriginalText(button) {
    if (!button.getAttribute('data-original-text')) {
        button.setAttribute('data-original-text', button.innerHTML);
    }
}

// Handle form submission with loading state
function handleFormSubmission(formId, submitHandler) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                saveButtonOriginalText(submitButton);
                setButtonLoading(submitButton, true);
            }
            
            // Call the submit handler
            submitHandler(new FormData(form), function() {
                // Reset loading state
                if (submitButton) {
                    setButtonLoading(submitButton, false);
                }
            });
        });
    }
}

// Example usage of the functions
console.log('Quant Trading System JavaScript loaded');

// Export functions for use in other scripts
window.ajaxRequest = ajaxRequest;
window.showNotification = showNotification;
window.formatCurrency = formatCurrency;
window.formatPercentage = formatPercentage;
window.updateElement = updateElement;
window.updateElementHTML = updateElementHTML;
window.toggleElement = toggleElement;
window.setButtonLoading = setButtonLoading;
window.saveButtonOriginalText = saveButtonOriginalText;
window.handleFormSubmission = handleFormSubmission;

