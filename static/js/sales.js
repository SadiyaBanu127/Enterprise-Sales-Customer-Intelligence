/**
 * Sales Analytics Interactive Visualizations & Rep Leaderboard
 */

let salesTrendChart = null;
let growthRateChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadSalesAnalytics();
});

async function loadSalesAnalytics() {
  try {
    const res = await App.fetchAPI('/api/sales');
    if (res.success) {
      renderSalesTrend(res.monthly_trend);
      renderGrowthChart(res.monthly_trend);
      renderRepLeaderboard(res.sales_reps);
      renderTopProducts(res.top_products);
    }
  } catch (err) {
    console.error('Failed to load sales analytics:', err);
  }
}

function renderSalesTrend(trend) {
  const ctx = document.getElementById('salesTrendCanvas')?.getContext('2d');
  if (!ctx) return;

  if (salesTrendChart) salesTrendChart.destroy();

  salesTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: trend.labels,
      datasets: [
        {
          label: 'Total Revenue ($)',
          data: trend.revenues,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.3,
          borderWidth: 3
        },
        {
          label: 'Net Profit ($)',
          data: trend.profits,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.05)',
          fill: true,
          tension: 0.3,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${App.formatCurrency(ctx.parsed.y)}`
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

function renderGrowthChart(trend) {
  const ctx = document.getElementById('growthRateCanvas')?.getContext('2d');
  if (!ctx) return;

  if (growthRateChart) growthRateChart.destroy();

  growthRateChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: trend.labels,
      datasets: [{
        label: 'MoM Revenue Growth (%)',
        data: trend.growth_rates,
        backgroundColor: trend.growth_rates.map(v => v >= 0 ? '#10b981' : '#ef4444'),
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => `Growth: ${ctx.parsed.y.toFixed(2)}%`
          }
        }
      },
      scales: {
        y: {
          ticks: { callback: (v) => `${v}%` }
        }
      }
    }
  });
}

function renderRepLeaderboard(reps) {
  const tbody = document.getElementById('repLeaderboardBody');
  if (!tbody) return;

  tbody.innerHTML = reps.map(r => `
    <tr>
      <td><strong>${r.rep_name}</strong><br><small class="text-muted">${r.rep_code}</small></td>
      <td><span class="badge badge-info">${r.region_name}</span></td>
      <td>${App.formatCurrency(r.quota)}</td>
      <td><strong>${App.formatCurrency(r.revenue)}</strong></td>
      <td>${App.formatCurrency(r.profit)}</td>
      <td>${r.deals_closed}</td>
      <td>
        <div style="display: flex; align-items: center; gap: 8px;">
          <div style="flex: 1; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
            <div style="width: ${Math.min(r.attainment_pct, 100)}%; height: 100%; background: ${r.attainment_pct >= 100 ? '#10b981' : r.attainment_pct >= 80 ? '#3b82f6' : '#f59e0b'};"></div>
          </div>
          <span style="font-weight: 600; font-size: 0.8rem;">${r.attainment_pct}%</span>
        </div>
      </td>
      <td>
        <span class="badge ${r.status === 'Quota Exceeded' ? 'badge-success' : r.status === 'On Track' ? 'badge-primary' : 'badge-warning'}">
          ${r.status}
        </span>
      </td>
    </tr>
  `).join('');
}

function renderTopProducts(products) {
  const tbody = document.getElementById('salesProductsBody');
  if (!tbody) return;

  tbody.innerHTML = products.map((p, i) => `
    <tr>
      <td><strong>#${i + 1}</strong></td>
      <td>${p.product_name}</td>
      <td><span class="badge badge-info">${p.category_name}</span></td>
      <td>${App.formatCurrency(p.revenue)}</td>
      <td>${App.formatCurrency(p.profit)}</td>
      <td>${App.formatNumber(p.units_sold)}</td>
      <td><span class="badge badge-primary">${p.margin_pct}%</span></td>
    </tr>
  `).join('');
}
