/**
 * Customer Analytics & RFM Segmentation UI Logic
 */

let rfmDistributionChart = null;
let currentPage = 1;

document.addEventListener('DOMContentLoaded', () => {
  loadCustomerKPIs();
  loadRFMSegments();
  loadCustomerTable(1);
  setupTableListeners();
});

function setupTableListeners() {
  const searchInput = document.getElementById('customerSearchInput');
  const segmentSelect = document.getElementById('customerSegmentFilter');
  const riskSelect = document.getElementById('customerRiskFilter');

  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => loadCustomerTable(1), 350);
    });
  }

  if (segmentSelect) segmentSelect.addEventListener('change', () => loadCustomerTable(1));
  if (riskSelect) riskSelect.addEventListener('change', () => loadCustomerTable(1));
}

async function loadCustomerKPIs() {
  try {
    const res = await App.fetchAPI('/api/customers?page=1&per_page=1');
    if (res.success && res.kpis) {
      document.getElementById('custTotal').innerText = App.formatNumber(res.kpis.total_customers);
      document.getElementById('custNew').innerText = App.formatNumber(res.kpis.new_customers);
      document.getElementById('custRepeat').innerText = App.formatPercent(res.kpis.repeat_purchase_rate);
      document.getElementById('custCLV').innerText = App.formatCurrency(res.kpis.average_customer_clv);
    }
  } catch (err) {
    console.error('Failed to load customer KPIs:', err);
  }
}

async function loadRFMSegments() {
  try {
    const res = await App.fetchAPI('/api/segments');
    if (res.success) {
      renderRFMChart(res.rfm);
      renderRFMTable(res.rfm.segments);
      renderKMeansClusters(res.kmeans.clusters);
    }
  } catch (err) {
    console.error('Failed to load segments:', err);
  }
}

function renderRFMChart(rfmData) {
  const ctx = document.getElementById('rfmDistributionCanvas')?.getContext('2d');
  if (!ctx) return;

  if (rfmDistributionChart) rfmDistributionChart.destroy();

  rfmDistributionChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: rfmData.chart_labels,
      datasets: [{
        label: 'Total Revenue ($)',
        data: rfmData.chart_revenues,
        backgroundColor: ['#10b981', '#3b82f6', '#06b6d4', '#f59e0b', '#ef4444', '#64748b'],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => `Revenue: ${App.formatCurrency(ctx.parsed.y)}`
          }
        }
      },
      scales: {
        y: {
          ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
        }
      }
    }
  });
}

function renderRFMTable(segments) {
  const tbody = document.getElementById('rfmSummaryTableBody');
  if (!tbody) return;

  tbody.innerHTML = segments.map(s => `
    <tr>
      <td><strong>${s.segment}</strong></td>
      <td>${App.formatNumber(s.count)} <small class="text-muted">(${s.percentage}%)</small></td>
      <td><strong>${App.formatCurrency(s.total_revenue)}</strong></td>
      <td>${App.formatCurrency(s.avg_spend)}</td>
      <td>${s.avg_recency} days</td>
      <td>${s.avg_frequency} orders</td>
    </tr>
  `).join('');
}

function renderKMeansClusters(clusters) {
  const container = document.getElementById('kmeansClustersContainer');
  if (!container) return;

  container.innerHTML = clusters.map(c => `
    <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 14px 18px; margin-bottom: 10px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <strong style="color: var(--primary); font-size: 0.9rem;">${c.name}</strong>
        <span class="badge badge-primary">${c.customer_count} Customers (${c.percentage}%)</span>
      </div>
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; font-size: 0.82rem; color: var(--text-muted);">
        <div>Avg Spend: <strong style="color: var(--text-main);">${App.formatCurrency(c.avg_monetary_spend)}</strong></div>
        <div>Avg Frequency: <strong style="color: var(--text-main);">${c.avg_frequency_orders} orders</strong></div>
        <div>Avg Recency: <strong style="color: var(--text-main);">${c.avg_recency_days} days</strong></div>
      </div>
    </div>
  `).join('');
}

async function loadCustomerTable(page = 1) {
  currentPage = page;
  const search = document.getElementById('customerSearchInput')?.value || '';
  const segment = document.getElementById('customerSegmentFilter')?.value || 'all';
  const risk = document.getElementById('customerRiskFilter')?.value || 'all';

  const params = new URLSearchParams({
    page: page,
    per_page: 15,
    search: search,
    segment: segment,
    risk_level: risk
  });

  try {
    const res = await App.fetchAPI(`/api/customers?${params.toString()}`);
    if (res.success) {
      renderTableRows(res.data.items);
      renderPagination(res.data.page, res.data.total_pages, res.data.total);
    }
  } catch (err) {
    console.error('Failed to load customers table:', err);
  }
}

function renderTableRows(items) {
  const tbody = document.getElementById('customerTableBody');
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" class="text-center text-muted" style="padding: 30px;">No matching customer records found.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map(c => `
    <tr>
      <td><strong>${c.customer_code}</strong></td>
      <td><strong>${c.customer_name}</strong><br><small class="text-muted">${c.company_name || 'N/A'}</small></td>
      <td><span class="badge badge-info">${c.region_name}</span></td>
      <td>${c.total_orders_count}</td>
      <td><strong>${App.formatCurrency(c.total_spend)}</strong></td>
      <td>${App.formatCurrency(c.average_order_value)}</td>
      <td>${c.last_purchase_date || 'N/A'}<br><small class="text-muted">${c.recency_days}d ago</small></td>
      <td><span class="badge badge-primary">RFM: ${c.rfm_score}</span></td>
      <td><span class="badge badge-info">${c.segment}</span></td>
      <td>
        <span class="badge ${c.churn_risk_level === 'High Risk' ? 'badge-danger' : c.churn_risk_level === 'Medium Risk' ? 'badge-warning' : 'badge-success'}">
          ${c.churn_risk_level} (${(c.churn_risk_score * 100).toFixed(0)}%)
        </span>
      </td>
    </tr>
  `).join('');
}

function renderPagination(page, totalPages, totalItems) {
  const container = document.getElementById('customerPaginationContainer');
  if (!container) return;

  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: var(--text-muted);">
      <div>Showing Page <strong>${page}</strong> of <strong>${totalPages || 1}</strong> (${App.formatNumber(totalItems)} total customers)</div>
      <div style="display: flex; gap: 8px;">
        <button class="btn btn-outline" ${page <= 1 ? 'disabled' : ''} onclick="loadCustomerTable(${page - 1})">Previous</button>
        <button class="btn btn-outline" ${page >= totalPages ? 'disabled' : ''} onclick="loadCustomerTable(${page + 1})">Next</button>
      </div>
    </div>
  `;
}
