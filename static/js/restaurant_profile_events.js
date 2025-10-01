// users/static/js/restaurant_profile_events.js
// JS for users/restaurant_profile.html

document.addEventListener('DOMContentLoaded', function() {
  // Responsive tab-to-dropdown logic
  var dropdown = document.getElementById('profileTabDropdown');
  if (dropdown) {
    dropdown.addEventListener('change', function() {
      var tabId = this.value;
      var tabButton = document.getElementById(tabId + '-tab');
      if (tabButton) {
        var tab = new bootstrap.Tab(tabButton);
        tab.show();
      } else {
        // Directly show tab pane if tab button is hidden (mobile)
        var tabContent = document.getElementById('profileTabContent');
        var panes = tabContent.querySelectorAll('.tab-pane');
        panes.forEach(function(pane) {
          pane.classList.remove('show', 'active');
        });
        var activePane = document.getElementById(tabId);
        if (activePane) {
          activePane.classList.add('show', 'active');
        }
      }
    });

    // Also update dropdown value when tab is changed by clicking tab buttons
    var tabButtons = document.querySelectorAll('.redesigned-tab-btn');
    tabButtons.forEach(function(btn) {
      btn.addEventListener('shown.bs.tab', function(e) {
        var tabId = btn.getAttribute('data-bs-target').replace('#', '');
        dropdown.value = tabId;
      });
    });
  }

  // Add any other event listeners here for buttons, forms, etc.
  // Example: If you had <button onclick="doSomething()">, replace with:
  // document.getElementById('yourButtonId').addEventListener('click', doSomething);

  // Example: If you had <form onsubmit="return validateForm()">, replace with:
  // document.getElementById('yourFormId').addEventListener('submit', function(e) {
  //   if (!validateForm()) e.preventDefault();
  // });

  // Add tooltip initialization if needed
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Add any functions that were previously inline here
// function doSomething() { ... }
// function validateForm() { ... }
