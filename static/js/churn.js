/**
 * Customer Churn Machine Learning Prediction UI Logic
 */

let rocCurveChart = null;
let featureImportanceChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadChurnOverview();
  setupPredictionForm();
});

async function loadChurnOverview() {
  try {
    const res = await App.fetchAPI('/api/churn/overview');
    if (res.success) {
      renderMetrics(res.metrics);
      renderConfusionMatrix(res.metrics.confusion_matrix);
      renderFeatureImportances(res.metrics.feature_importances);
      renderROCCurve(res.metrics.roc_curve);
      renderRiskCounts(res.risk_overview);
    }
  } catch (err) {
    console.error('Failed to load churn overview:', err);
  }
}

function renderMetrics(metrics) {
  document.getElementById('metricAccuracy').innerText = App.formatPercent(metrics.accuracy * 100);
  document.getElementById('metricPrecision').innerText = App.formatPercent(metrics.precision * 100);
  document.getElementById('metricRecall').innerText = App.formatPercent(metrics.recall * 100);
  document.getElementById('metricF1').innerText = Number(metrics.f1_score).toFixed(3);
  document.getElementById('metricROCAUC').innerText = Number(metrics.roc_auc).toFixed(3);
  document.getElementById('modelNameBadge').innerText = metrics.model_name || 'Random Forest';
}

function renderConfusionMatrix(cm) {
  if (!cm) return;
  document.getElementById('cmTN').innerText = cm.true_negatives;
  document.getElementById('cmFP').innerText = cm.false_positives;
  document.getElementById('cmFN').innerText = cm.false_negatives;
  document.getElementById('cmTP').innerText = cm.true_positives;
}

function renderRiskCounts(risk) {
  if (!risk) return;
  document.getElementById('churnHighCount').innerText = `${App.formatNumber(risk.high_risk_count)} (${risk.high_risk_pct}%)`;
  document.getElementById('churnMedCount').innerText = `${App.formatNumber(risk.medium_risk_count)} (${risk.medium_risk_pct}%)`;
  document.getElementById('churnLowCount').innerText = `${App.formatNumber(risk.low_risk_count)} (${risk.low_risk_pct}%)`;
}

function renderFeatureImportances(features) {
  const ctx = document.getElementById('featureImportanceCanvas')?.getContext('2d');
  if (!ctx || !features) return;

  if (featureImportanceChart) featureImportanceChart.destroy();

  featureImportanceChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: features.map(f => f.feature.replace('_', ' ')),
      datasets: [{
        label: 'Importance Weight',
        data: features.map(f => f.importance),
        backgroundColor: '#2563eb',
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { beginAtZero: true }
      }
    }
  });
}

function renderROCCurve(roc) {
  const ctx = document.getElementById('rocCurveCanvas')?.getContext('2d');
  if (!ctx || !roc) return;

  if (rocCurveChart) rocCurveChart.destroy();

  rocCurveChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: roc.fpr,
      datasets: [
        {
          label: 'ROC Curve (Random Forest)',
          data: roc.tpr,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.1,
          borderWidth: 2.5
        },
        {
          label: 'Random Guess Baseline',
          data: roc.fpr,
          borderColor: '#94a3b8',
          borderDash: [4, 4],
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: 'False Positive Rate (FPR)' } },
        y: { title: { display: true, text: 'True Positive Rate (TPR)' } }
      }
    }
  });
}

function setupPredictionForm() {
  const form = document.getElementById('singlePredictForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const custId = document.getElementById('predictCustomerIdInput')?.value.trim();
    if (!custId) return;

    try {
      const res = await App.fetchAPI(`/api/churn/predict/${custId}`);
      if (res.success) {
        renderSinglePredictionResult(res);
      }
    } catch (err) {
      console.error('Prediction error:', err);
    }
  });
}

function renderSinglePredictionResult(data) {
  const resultCard = document.getElementById('predictionResultContainer');
  if (!resultCard) return;

  resultCard.style.display = 'block';
  document.getElementById('resCustomerName').innerText = `${data.customer_name} (${data.customer_code})`;
  document.getElementById('resProbability').innerText = `${data.churn_probability}%`;
  
  const riskBadge = document.getElementById('resRiskBadge');
  riskBadge.innerText = data.churn_risk_level;
  riskBadge.className = `badge ${data.churn_risk_level === 'High Risk' ? 'badge-danger' : data.churn_risk_level === 'Medium Risk' ? 'badge-warning' : 'badge-success'}`;

  document.getElementById('resDriversList').innerHTML = data.key_drivers.map(d => `<li>${d}</li>`).join('');
  document.getElementById('resRecommendation').innerText = data.recommended_action;
}
