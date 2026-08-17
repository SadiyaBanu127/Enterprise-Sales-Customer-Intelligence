/**
 * Enterprise Sales & Customer Intelligence Platform
 * Global Frontend Helpers & Utilities
 */

const App = {
  // Format Currency
  formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value)) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 2
    }).format(value);
  },

  // Format Large Number
  formatNumber(value) {
    if (value === null || value === undefined || isNaN(value)) return '0';
    return new Intl.NumberFormat('en-US').format(value);
  },

  // Format Percentage
  formatPercent(value) {
    if (value === null || value === undefined || isNaN(value)) return '0.0%';
    return `${Number(value).toFixed(1)}%`;
  },

  // Show Toast Notification
  showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.borderLeft = type === 'success' ? '4px solid #10b981' : 
                             type === 'danger' ? '4px solid #ef4444' : 
                             type === 'warning' ? '4px solid #f59e0b' : '4px solid #2563eb';
    toast.innerText = message;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  // Generic Fetch API Wrapper
  async fetchAPI(url, options = {}) {
    try {
      const res = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to fetch data');
      }
      return data;
    } catch (err) {
      console.error('API Error:', err);
      App.showToast(err.message, 'danger');
      throw err;
    }
  }
};

// Sidebar Toggle on Mobile
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('appSidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
});
