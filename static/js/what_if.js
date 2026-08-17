/**
 * What-If Financial Scenario Simulator UI Logic
 */

let scenarioComparisonChart = null;

document.addEventListener('DOMContentLoaded', () => {
  setupSimulatorControls();
  runSimulation();
});

function setupSimulatorControls() {
  const sliders = [
    { id: 'sliderPrice', valId: 'valPrice', suffix: '%' },
    { id: 'sliderDiscount', valId: 'valDiscount', suffix: '%' },
    { id: 'sliderQuantity', valId: 'valQuantity', suffix: '%' },
    { id: 'sliderMarketing', valId: 'valMarketing', prefix: '$', suffix: '' }
  ];

  sliders.forEach(s => {
    const el = document.getElementById(s.id);
    const valEl = document.getElementById(s.valId);
    if (el && valEl) {
      el.addEventListener('input', () => {
        let val = Number(el.value);
        if (s.prefix) {
          valEl.innerText = `${s.prefix}${val.toLocaleString()}`;
        } else {
          valEl.innerText = `${val > 0 ? '+' : ''}${val}${s.suffix}`;
        }
        runSimulation();
      });
    }
  });

  const resetBtn = document.getElementById('resetScenarioBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      document.getElementById('sliderPrice').value = 0;
      document.getElementById('valPrice').innerText = '0%';
      document.getElementById('sliderDiscount').value = 0;
      document.getElementById('valDiscount').innerText = '0%';
      document.getElementById('sliderQuantity').value = 0;
      document.getElementById('valQuantity').innerText = '0%';
      document.getElementById('sliderMarketing').value = 0;
      document.getElementById('valMarketing').innerText = '$0';
      runSimulation();
    });
  }
}

async function runSimulation() {
  const price = parseFloat(document.getElementById('sliderPrice')?.value || 0);
  const discount = parseFloat(document.getElementById('sliderDiscount')?.value || 0);
  const qty = parseFloat(document.getElementById('sliderQuantity')?.value || 0);
  const marketing = parseFloat(document.getElementById('sliderMarketing')?.value || 0);

  const params = new URLSearchParams({
    price_change_pct: price,
    discount_change_pct: discount,
    quantity_change_pct: qty,
    marketing_spend: marketing
  });

  try {
    const res = await App.fetchAPI(`/api/what-if?${params.toString()}`);
    if (res.success && res.scenario) {
      renderScenarioResults(res.scenario);
      renderScenarioChart(res.scenario);
    }
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

function renderScenarioResults(data) {
  // Baseline
  document.getElementById('baseRevenue').innerText = App.formatCurrency(data.baseline.revenue);
  document.getElementById('baseCost').innerText = App.formatCurrency(data.baseline.cost);
  document.getElementById('baseProfit').innerText = App.formatCurrency(data.baseline.profit);
  document.getElementById('baseMargin').innerText = App.formatPercent(data.baseline.margin_pct);

  // Simulated
  document.getElementById('simRevenue').innerText = App.formatCurrency(data.simulated.revenue);
  document.getElementById('simCost').innerText = App.formatCurrency(data.simulated.cost);
  document.getElementById('simProfit').innerText = App.formatCurrency(data.simulated.profit);
  document.getElementById('simMargin').innerText = App.formatPercent(data.simulated.margin_pct);

  // Variances
  const revDeltaEl = document.getElementById('varRevenue');
  revDeltaEl.innerText = `${data.variance.revenue_delta >= 0 ? '+' : ''}${App.formatCurrency(data.variance.revenue_delta)} (${data.variance.revenue_delta_pct}%)`;
  revDeltaEl.style.color = data.variance.revenue_delta >= 0 ? '#10b981' : '#ef4444';

  const profDeltaEl = document.getElementById('varProfit');
  profDeltaEl.innerText = `${data.variance.profit_delta >= 0 ? '+' : ''}${App.formatCurrency(data.variance.profit_delta)} (${data.variance.profit_delta_pct}%)`;
  profDeltaEl.style.color = data.variance.profit_delta >= 0 ? '#10b981' : '#ef4444';

  const marginDeltaEl = document.getElementById('varMargin');
  marginDeltaEl.innerText = `${data.variance.margin_delta_pct >= 0 ? '+' : ''}${data.variance.margin_delta_pct}%`;
  marginDeltaEl.style.color = data.variance.margin_delta_pct >= 0 ? '#10b981' : '#ef4444';

  document.getElementById('scenarioRecommendation').innerText = data.recommendation;
}

function renderScenarioChart(data) {
  const ctx = document.getElementById('scenarioComparisonCanvas')?.getContext('2d');
  if (!ctx) return;

  if (scenarioComparisonChart) scenarioComparisonChart.destroy();

  scenarioComparisonChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Net Revenue', 'Total Operating Cost', 'Net Operating Profit'],
      datasets: [
        {
          label: 'Baseline Scenario ($)',
          data: [data.baseline.revenue, data.baseline.cost, data.baseline.profit],
          backgroundColor: '#94a3b8',
          borderRadius: 6
        },
        {
          label: 'What-If Simulated Scenario ($)',
          data: [data.simulated.revenue, data.simulated.cost, data.simulated.profit],
          backgroundColor: data.variance.profit_delta >= 0 ? '#10b981' : '#ef4444',
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
