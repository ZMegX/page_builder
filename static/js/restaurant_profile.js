// users/static/js/restaurant_profile.js
// Opening Hours: Quick Set, Clear, Copy to All Days
function updateTimeInputsVisibility(row) {
  const isClosed = row.querySelector('.is-closed-checkbox')?.checked;
  row.querySelectorAll('.open-time-input, .close-time-input').forEach(function(input) {
    input.style.display = isClosed ? 'none' : '';
  });
}

document.addEventListener('DOMContentLoaded', function() {
  // Opening Hours logic
  document.querySelectorAll('.hours-row').forEach(function(row) {
    const closedCheckbox = row.querySelector('.is-closed-checkbox');
    if (closedCheckbox) {
      closedCheckbox.addEventListener('change', function() {
        updateTimeInputsVisibility(row);
      });
      updateTimeInputsVisibility(row);
    }
  });

  document.querySelectorAll('.set-closed-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const row = btn.closest('.hours-row');
      if (!row) return;
      row.querySelector('.is-closed-checkbox').checked = true;
      updateTimeInputsVisibility(row);
      row.querySelectorAll('.open-time-input, .close-time-input').forEach(function(input) {
        input.value = '';
      });
    });
  });

  document.querySelectorAll('.set-24h-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const row = btn.closest('.hours-row');
      if (!row) return;
      // Uncheck closed, show inputs
      const closedCheckbox = row.querySelector('.is-closed-checkbox');
      if (closedCheckbox) {
        closedCheckbox.checked = false;
        updateTimeInputsVisibility(row);
      }
      // Set open/close times
      const openInput = row.querySelector('.open-time-input');
      const closeInput = row.querySelector('.close-time-input');
      if (openInput) {
        openInput.style.display = '';
        openInput.value = '00:00';
      }
      if (closeInput) {
        closeInput.style.display = '';
        closeInput.value = '23:59';
      }
    });
  });

  document.querySelectorAll('.clear-hours-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const row = btn.closest('.hours-row');
      if (!row) return;
      row.querySelector('.is-closed-checkbox').checked = false;
      updateTimeInputsVisibility(row);
      row.querySelectorAll('.open-time-input, .close-time-input').forEach(function(input) {
        input.value = '';
      });
    });
  });

  const copyHoursBtn = document.getElementById('copy-hours-btn');
  if (copyHoursBtn) {
    copyHoursBtn.addEventListener('click', function() {
      const firstRow = document.querySelector('.hours-row');
      if (!firstRow) return;
      const firstOpen = firstRow.querySelector('.open-time-input')?.value || '';
      const firstClose = firstRow.querySelector('.close-time-input')?.value || '';
      const firstClosed = firstRow.querySelector('.is-closed-checkbox')?.checked || false;
      document.querySelectorAll('.hours-row').forEach(function(row) {
        row.querySelector('.open-time-input').value = firstOpen;
        row.querySelector('.close-time-input').value = firstClose;
        row.querySelector('.is-closed-checkbox').checked = firstClosed;
        updateTimeInputsVisibility(row);
      });
    });
  }
});
