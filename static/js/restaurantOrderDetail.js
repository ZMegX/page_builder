document.addEventListener('DOMContentLoaded', function() {
  var printBtn = document.getElementById('confirmPrintBtn');
  var statusDropdown = document.getElementById('statusDropdown');
  var statusForm = document.getElementById('statusForm');
  if (printBtn) {
    printBtn.addEventListener('click', function() {
      // Before printing, set status to Confirmed if not already
      if (statusDropdown && statusDropdown.value !== 'confirmed') {
        statusDropdown.value = 'confirmed';
        if (statusForm) {
          statusForm.submit();
        }
      }
      // Hide modal before printing
      var modal = document.getElementById('printModal');
      if (modal) {
        var modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) modalInstance.hide();
      }
      setTimeout(function() {
        window.print();
      }, 300);
    });
  }
});
