/**
 * Regional Analytics & Geographic Performance
 */

let regionalComparisonChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadRegionalAnalytics();
});

async function loadRegionalAnalytics() {
  try {
    const res = await App.fetchAPI('/api/regions');
    if (res.success) {
      renderStandouts(res.data.standouts);
      renderRegionalChart(res.data.regional_breakdown);
      renderRegionalTable(res.data.regional_breakdown);
    }
  } catch (err) {
    console.error('Failed to load regional analytics:', err);
  }
}

function renderStandouts(standouts) {
  if (standouts.best_performing) {
    document.getElementById('bestRegionName').innerText = standouts.best_performing.region_name;
    document.getElementById('bestRegionRev').innerText = `${App.formatCurrency(standouts.best_performing.total_revenue)} (${standouts.best_performing.market_share_pct}% share)`;
  }
  if (standouts.fastest_growing) {
    document.getElementById('fastestRegionName').innerText = standouts.fastest_growing.region_name;
    document.getElementById('fastestRegionGrowth').innerText = `+${standouts.fastest_growing.recent_growth_rate}% recent growth`;
  }
  if (standouts.worst_performing) {
    document.getElementById('worstRegionName').innerText = standouts.worst_performing.region_name;
    document.getElementById('worstRegionRev').innerText = App.formatCurrency(standouts.worst_performing.total_revenue);
  }
}

function renderRegionalChart(regions) {
  const ctx = document.getElementById('regionalComparisonCanvas')?.getContext('2d');
  if (!ctx) return;

  if (regionalComparisonChart) regionalComparisonChart.destroy();

  regionalComparisonChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: regions.map(r => r.region_name),
      datasets: [
        {
          label: 'Total Revenue ($)',
          data: regions.map(r => r.total_revenue),
          backgroundColor: '#2563eb',
          borderRadius: 6
        },
        {
          label: 'Total Profit ($)',
          data: regions.map(r => r.total_profit),
          backgroundColor: '#10b981',
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
        }
      }
    }
  });
}

function renderRegionalTable(regions) {
  const tbody = document.getElementById('regionalTableBody');
  if (!tbody) return;

  tbody.innerHTML = regions.map(r => `
    <tr>
      <td><strong>${r.region_name}</strong></td>
      <td><span class="badge badge-info">${r.market_tier}</span></td>
      <td>${App.formatNumber(r.customer_count)}</td>
      <td>${r.rep_count} Reps</td>
      <td><strong>${App.formatCurrency(r.total_revenue)}</strong></td>
      <td>${App.formatCurrency(r.total_profit)}</td>
      <td><span class="badge badge-primary">${r.profit_margin_pct}%</span></td>
      <td><span class="badge ${r.recent_growth_rate >= 0 ? 'badge-success' : 'badge-danger'}">${r.recent_growth_rate > 0 ? '+' : ''}${r.recent_growth_rate}%</span></td>
      <td><strong>${r.market_share_pct}%</strong></td>
    </tr>
  `).join('');
}
