/**
 * Time-Series Sales Forecasting UI Logic
 */

let forecastChart = null;
let currentHorizon = 90;

document.addEventListener('DOMContentLoaded', () => {
  loadForecastData(90);
  setupHorizonButtons();
});

function setupHorizonButtons() {
  const buttons = document.querySelectorAll('.horizon-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active', 'btn-primary'));
      buttons.forEach(b => b.classList.add('btn-outline'));
      
      btn.classList.remove('btn-outline');
      btn.classList.add('active', 'btn-primary');

      const horizon = parseInt(btn.dataset.horizon, 10);
      loadForecastData(horizon);
    });
  });
}

async function loadForecastData(horizon = 90) {
  currentHorizon = horizon;
  try {
    const res = await App.fetchAPI(`/api/forecast?horizon=${horizon}`);
    if (res.success && res.data) {
      renderForecastSummary(res.data);
      renderForecastChart(res.data);
    }
  } catch (err) {
    console.error('Failed to load forecast data:', err);
  }
}

function renderForecastSummary(data) {
  document.getElementById('fcExpectedRevenue').innerText = App.formatCurrency(data.expected_revenue);
  
  const growthEl = document.getElementById('fcGrowthRate');
  growthEl.innerText = `${data.expected_growth_rate > 0 ? '+' : ''}${data.expected_growth_rate}%`;
  growthEl.className = `badge ${data.expected_growth_rate >= 0 ? 'badge-success' : 'badge-danger'}`;

  document.getElementById('fcModelName').innerText = data.model_name;
  document.getElementById('fcInterpretationText').innerText = data.interpretation;
}

function renderForecastChart(data) {
  const ctx = document.getElementById('forecastChartCanvas')?.getContext('2d');
  if (!ctx) return;

  if (forecastChart) forecastChart.destroy();

  const allLabels = [...data.historical.dates, ...data.forecast.dates];
  
  // Historical data padded with nulls for forecast period
  const histValues = [...data.historical.values, ...new Array(data.forecast.dates.length).fill(null)];
  
  // Forecast values padded with nulls for historical period (connect at last historical point)
  const fcValues = [...new Array(data.historical.dates.length - 1).fill(null), data.historical.values[data.historical.values.length - 1], ...data.forecast.values];
  const upperCI = [...new Array(data.historical.dates.length - 1).fill(null), data.historical.values[data.historical.values.length - 1], ...data.forecast.upper_ci];
  const lowerCI = [...new Array(data.historical.dates.length - 1).fill(null), data.historical.values[data.historical.values.length - 1], ...data.forecast.lower_ci];

  forecastChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: allLabels,
      datasets: [
        {
          label: 'Historical Weekly Sales ($)',
          data: histValues,
          borderColor: '#475569',
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 2
        },
        {
          label: 'Forecasted Sales ($)',
          data: fcValues,
          borderColor: '#2563eb',
          backgroundColor: 'transparent',
          borderWidth: 2.5,
          borderDash: [6, 4],
          pointRadius: 3
        },
        {
          label: 'Upper 95% Confidence Interval',
          data: upperCI,
          borderColor: 'transparent',
          backgroundColor: 'rgba(37, 99, 235, 0.12)',
          fill: '+1',
          pointRadius: 0
        },
        {
          label: 'Lower 95% Confidence Interval',
          data: lowerCI,
          borderColor: 'transparent',
          backgroundColor: 'rgba(37, 99, 235, 0.12)',
          fill: false,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: (ctx) => ctx.parsed.y !== null ? `${ctx.dataset.label}: ${App.formatCurrency(ctx.parsed.y)}` : null
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
