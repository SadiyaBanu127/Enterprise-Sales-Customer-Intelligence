/**
 * Product Analytics & 4-Quadrant Profitability Matrix
 */

let productMatrixChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadProductAnalytics();
});

async function loadProductAnalytics() {
  try {
    const res = await App.fetchAPI('/api/products');
    if (res.success) {
      renderQuadrantCounts(res.data.quadrant_counts);
      renderProfitabilityMatrix(res.data.all_products, res.data.benchmarks);
      renderLeaderboards(res.data);
      renderAllProductsTable(res.data.all_products);
    }
  } catch (err) {
    console.error('Failed to load product analytics:', err);
  }
}

function renderQuadrantCounts(counts) {
  document.getElementById('countStars').innerText = counts['Star Performers'] || 0;
  document.getElementById('countVolume').innerText = counts['Volume Drivers'] || 0;
  document.getElementById('countNiche').innerText = counts['Niche High Margin'] || 0;
  document.getElementById('countUnder').innerText = counts['Underperformers'] || 0;
}

function renderProfitabilityMatrix(products, benchmarks) {
  const ctx = document.getElementById('profitabilityMatrixCanvas')?.getContext('2d');
  if (!ctx) return;

  if (productMatrixChart) productMatrixChart.destroy();

  const datasets = [
    {
      label: 'Star Performers',
      data: products.filter(p => p.quadrant.includes('Star')).map(p => ({ x: p.total_revenue, y: p.total_profit, name: p.name, margin: p.margin_pct })),
      backgroundColor: '#10b981',
      borderColor: '#059669',
      pointRadius: 7
    },
    {
      label: 'Volume Drivers',
      data: products.filter(p => p.quadrant.includes('Volume')).map(p => ({ x: p.total_revenue, y: p.total_profit, name: p.name, margin: p.margin_pct })),
      backgroundColor: '#3b82f6',
      borderColor: '#2563eb',
      pointRadius: 6
    },
    {
      label: 'Niche High Margin',
      data: products.filter(p => p.quadrant.includes('Niche')).map(p => ({ x: p.total_revenue, y: p.total_profit, name: p.name, margin: p.margin_pct })),
      backgroundColor: '#f59e0b',
      borderColor: '#d97706',
      pointRadius: 6
    },
    {
      label: 'Underperformers',
      data: products.filter(p => p.quadrant.includes('Under')).map(p => ({ x: p.total_revenue, y: p.total_profit, name: p.name, margin: p.margin_pct })),
      backgroundColor: '#ef4444',
      borderColor: '#dc2626',
      pointRadius: 6
    }
  ];

  productMatrixChart = new Chart(ctx, {
    type: 'scatter',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const raw = ctx.raw;
              return `${raw.name}: Rev ${App.formatCurrency(raw.x)}, Profit ${App.formatCurrency(raw.y)} (Margin: ${raw.margin}%)`;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Total Revenue ($)' },
          ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
        },
        y: {
          title: { display: true, text: 'Total Net Profit ($)' },
          ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
        }
      }
    }
  });
}

function renderLeaderboards(data) {
  const renderList = (items, targetId, isCurrency = true) => {
    const el = document.getElementById(targetId);
    if (!el) return;
    el.innerHTML = items.map(p => `
      <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border-subtle); font-size: 0.83rem;">
        <span style="font-weight: 500; color: var(--text-main);">${p.name.substring(0, 24)}...</span>
        <strong>${isCurrency ? App.formatCurrency(p.total_revenue || p.total_profit) : p.units_sold + ' units'}</strong>
      </div>
    `).join('');
  };

  renderList(data.top_by_revenue, 'topRevList', true);
  renderList(data.top_by_profit, 'topProfitList', true);
  renderList(data.top_by_units, 'topUnitsList', false);
}

function renderAllProductsTable(products) {
  const tbody = document.getElementById('allProductsTableBody');
  if (!tbody) return;

  tbody.innerHTML = products.map(p => `
    <tr>
      <td><strong>${p.sku}</strong></td>
      <td><strong>${p.name}</strong></td>
      <td><span class="badge badge-info">${p.category}</span></td>
      <td>${App.formatCurrency(p.unit_price)}</td>
      <td>${App.formatNumber(p.units_sold)}</td>
      <td><strong>${App.formatCurrency(p.total_revenue)}</strong></td>
      <td>${App.formatCurrency(p.total_profit)}</td>
      <td><span class="badge ${p.margin_pct >= 40 ? 'badge-success' : 'badge-warning'}">${p.margin_pct}%</span></td>
      <td><span class="badge badge-primary">${p.quadrant}</span></td>
      <td><small style="color: var(--text-muted);">${p.recommendation}</small></td>
    </tr>
  `).join('');
}
