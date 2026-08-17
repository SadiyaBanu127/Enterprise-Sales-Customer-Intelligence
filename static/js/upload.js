/**
 * Dataset Upload & ETL Pipeline Trigger UI Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  setupUploadForm();
  setupETLTrigger();
});

function setupUploadForm() {
  const form = document.getElementById('datasetUploadForm');
  const fileInput = document.getElementById('csvFileInput');
  const dropZone = document.getElementById('fileDropZone');

  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '#2563eb';
    });
    dropZone.addEventListener('dragleave', () => {
      dropZone.style.borderColor = '#cbd5e1';
    });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.style.borderColor = '#cbd5e1';
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelected(fileInput.files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) {
        handleFileSelected(fileInput.files[0]);
      }
    });
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!fileInput.files.length) {
        App.showToast('Please select a file to upload.', 'warning');
        return;
      }

      const formData = new FormData();
      formData.append('file', fileInput.files[0]);
      formData.append('dataset_type', document.getElementById('datasetTypeSelect')?.value || 'orders');

      const submitBtn = document.getElementById('uploadSubmitBtn');
      submitBtn.disabled = true;
      submitBtn.innerText = 'Validating & Uploading...';

      try {
        const res = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        
        if (data.success) {
          App.showToast('Dataset validated successfully!', 'success');
          renderUploadSummary(data);
        } else {
          App.showToast(data.error || 'Upload failed', 'danger');
        }
      } catch (err) {
        console.error('Upload error:', err);
        App.showToast('Upload error occurred', 'danger');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Upload & Process Dataset';
      }
    });
  }
}

function handleFileSelected(file) {
  const fileNameEl = document.getElementById('selectedFileName');
  if (fileNameEl) {
    fileNameEl.innerText = `Selected File: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    fileNameEl.style.display = 'block';
  }
}

function renderUploadSummary(data) {
  const summaryCard = document.getElementById('uploadSummaryCard');
  if (!summaryCard) return;

  summaryCard.style.display = 'block';
  document.getElementById('sumRowsReceived').innerText = App.formatNumber(data.summary.total_rows_received);
  document.getElementById('sumColsReceived').innerText = data.summary.total_columns;
  document.getElementById('sumNullsHandled').innerText = App.formatNumber(data.summary.null_values_detected);
  document.getElementById('sumDupesHandled').innerText = App.formatNumber(data.summary.duplicates_detected);
  document.getElementById('sumRowsCleaned').innerText = App.formatNumber(data.summary.cleaned_rows_ready);

  // Render Table Preview
  const previewContainer = document.getElementById('uploadPreviewTable');
  if (previewContainer && data.preview && data.preview.length > 0) {
    const cols = Object.keys(data.preview[0]);
    let html = `<table class="custom-table"><thead><tr>`;
    cols.forEach(c => html += `<th>${c}</th>`);
    html += `</tr></thead><tbody>`;
    data.preview.forEach(row => {
      html += `<tr>`;
      cols.forEach(c => html += `<td>${row[c] !== null ? row[c] : ''}</td>`);
      html += `</tr>`;
    });
    html += `</tbody></table>`;
    previewContainer.innerHTML = html;
  }
}

function setupETLTrigger() {
  const triggerBtn = document.getElementById('triggerFullETLBtn');
  if (!triggerBtn) return;

  triggerBtn.addEventListener('click', async () => {
    triggerBtn.disabled = true;
    triggerBtn.innerText = 'Executing Pipeline (Extract -> Transform -> Load)...';

    try {
      const res = await App.fetchAPI('/api/etl/trigger', { method: 'POST' });
      if (res.success) {
        App.showToast('Full ETL Pipeline executed successfully!', 'success');
        setTimeout(() => window.location.href = '/dashboard', 1500);
      }
    } catch (err) {
      console.error('ETL Trigger error:', err);
    } finally {
      triggerBtn.disabled = false;
      triggerBtn.innerText = 'Re-Run Full Production ETL Pipeline';
    }
  });
}
