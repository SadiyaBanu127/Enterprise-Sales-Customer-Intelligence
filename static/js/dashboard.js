/**
 * Executive Dashboard Dynamic Charts & Multi-Filter Logic
 */

let revenueTrendChart = null;
let regionDonutChart = null;
let categoryBarChart = null;
let segmentPieChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
  setupFilterListeners();
});

function setupFilterListeners() {
  const filterInputs = ['filterStartDate', 'filterEndDate', 'filterRegion', 'filterCategory', 'filterSegment'];
  filterInputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', () => loadDashboardData());
    }
  });

  const resetBtn = document.getElementById('resetFiltersBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      filterInputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = (id === 'filterStartDate' || id === 'filterEndDate') ? '' : 'all';
      });
      loadDashboardData();
    });
  }
}

async function loadDashboardData() {
  const startDate = document.getElementById('filterStartDate')?.value || '';
  const endDate = document.getElementById('filterEndDate')?.value || '';
  const regionId = document.getElementById('filterRegion')?.value || 'all';
  const categoryId = document.getElementById('filterCategory')?.value || 'all';
  const segment = document.getElementById('filterSegment')?.value || 'all';

  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
    region_id: regionId,
    category_id: categoryId,
    segment: segment
  });

  try {
    const res = await App.fetchAPI(`/api/dashboard?${params.toString()}`);
    if (res.success) {
      renderKPIs(res.kpis);
      renderTrendChart(res.monthly_trend);
      renderRegionDonut(res.regional_breakdown);
      renderCategoryBar(res.category_breakdown);
      renderSegmentPie(res.segment_distribution);
      renderTopProductsTable(res.top_products);
      renderTopCustomersTable(res.top_customers);
      renderInsights(res.insights);
    }
  } catch (e) {
    console.error('Error loading dashboard:', e);
  }
}

function renderKPIs(kpis) {
  document.getElementById('kpiRevenue').innerText = App.formatCurrency(kpis.total_revenue);
  document.getElementById('kpiProfit').innerText = App.formatCurrency(kpis.total_profit);
  document.getElementById('kpiMargin').innerText = App.formatPercent(kpis.profit_margin);
  document.getElementById('kpiOrders').innerText = App.formatNumber(kpis.total_orders);
  document.getElementById('kpiCustomers').innerText = App.formatNumber(kpis.total_customers);
  document.getElementById('kpiAOV').innerText = App.formatCurrency(kpis.average_order_value);
  document.getElementById('kpiRetention').innerText = App.formatPercent(kpis.retention_rate);
  document.getElementById('kpiChurn').innerText = App.formatPercent(kpis.churn_rate);
}

function renderTrendChart(data) {
  const ctx = document.getElementById('revenueTrendCanvas')?.getContext('2d');
  if (!ctx) return;

  if (revenueTrendChart) revenueTrendChart.destroy();

  revenueTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [
        {
          label: 'Revenue ($)',
          data: data.revenues,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.08)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5
        },
        {
          label: 'Net Profit ($)',
          data: data.profits,
          borderColor: '#10b981',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { font: { family: 'Inter', size: 12 } } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${App.formatCurrency(ctx.parsed.y)}`
          }
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          ticks: {
            callback: (v) => `$${(v / 1000).toFixed(0)}k`
          },
          grid: { color: '#f1f5f9' }
        }
      }
    }
  });
}

function renderRegionDonut(data) {
  const ctx = document.getElementById('regionDonutCanvas')?.getContext('2d');
  if (!ctx) return;

  if (regionDonutChart) regionDonutChart.destroy();

  regionDonutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.labels,
      datasets: [{
        data: data.revenues,
        backgroundColor: ['#2563eb', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 11 } } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.label}: ${App.formatCurrency(ctx.parsed)}`
          }
        }
      },
      cutout: '70%'
    }
  });
}

function renderCategoryBar(data) {
  const ctx = document.getElementById('categoryBarCanvas')?.getContext('2d');
  if (!ctx) return;

  if (categoryBarChart) categoryBarChart.destroy();

  categoryBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels.map(l => l.length > 18 ? l.substring(0, 18) + '...' : l),
      datasets: [
        {
          label: 'Revenue ($)',
          data: data.revenues,
          backgroundColor: '#3b82f6',
          borderRadius: 6
        },
        {
          label: 'Profit ($)',
          data: data.profits,
          backgroundColor: '#10b981',
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { font: { family: 'Inter', size: 11 } } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${App.formatCurrency(ctx.parsed.y)}`
          }
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` },
          grid: { color: '#f1f5f9' }
        }
      }
    }
  });
}

function renderSegmentPie(data) {
  const ctx = document.getElementById('segmentPieCanvas')?.getContext('2d');
  if (!ctx) return;

  if (segmentPieChart) segmentPieChart.destroy();

  segmentPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: data.chart_labels,
      datasets: [{
        data: data.chart_counts,
        backgroundColor: ['#10b981', '#3b82f6', '#06b6d4', '#f59e0b', '#ef4444', '#64748b'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { font: { family: 'Inter', size: 11 } } }
      }
    }
  });
}

function renderTopProductsTable(products) {
  const tbody = document.getElementById('topProductsTableBody');
  if (!tbody) return;

  tbody.innerHTML = products.map((p, idx) => `
    <tr>
      <td><span class="badge badge-primary">#${idx + 1}</span></td>
      <td><strong>${p.product_name}</strong></td>
      <td><span class="badge badge-info">${p.category_name}</span></td>
      <td>${App.formatCurrency(p.revenue)}</td>
      <td>${App.formatCurrency(p.profit)}</td>
      <td><span class="badge ${p.margin_pct >= 40 ? 'badge-success' : 'badge-warning'}">${p.margin_pct}%</span></td>
    </tr>
  `).join('');
}

function renderTopCustomersTable(customers) {
  const tbody = document.getElementById('topCustomersTableBody');
  if (!tbody) return;

  tbody.innerHTML = customers.map((c, idx) => `
    <tr>
      <td><strong>${c.customer_name}</strong><br><small class="text-muted">${c.company_name}</small></td>
      <td><span class="badge badge-primary">${c.segment}</span></td>
      <td>${c.region_name}</td>
      <td>${App.formatNumber(c.total_orders)}</td>
      <td><strong>${App.formatCurrency(c.total_spend)}</strong></td>
      <td>
        <span class="badge ${c.churn_risk_level === 'High Risk' ? 'badge-danger' : c.churn_risk_level === 'Medium Risk' ? 'badge-warning' : 'badge-success'}">
          ${c.churn_risk_level}
        </span>
      </td>
    </tr>
  `).join('');
}

function renderInsights(insights) {
  const container = document.getElementById('dynamicInsightsContainer');
  if (!container) return;

  container.innerHTML = insights.map(ins => `
    <div class="insight-card insight-${ins.type}">
      <div class="insight-title">[${ins.category}] ${ins.title}</div>
      <div class="insight-desc">${ins.summary}</div>
      <div class="insight-action">💡 Recommendation: ${ins.action}</div>
    </div>
  `).join('');
}
