/**
 * Downloadable PDF Reports Handler
 */

document.addEventListener('DOMContentLoaded', () => {
  setupReportDownloadButtons();
});

function setupReportDownloadButtons() {
  const buttons = document.querySelectorAll('.download-report-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const reportType = btn.dataset.reportType;
      App.showToast(`Generating ${reportType.replace('_', ' ')} PDF...`, 'info');
      // Link will trigger standard browser attachment download
    });
  });
}
