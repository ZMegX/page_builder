// users/static/js/restaurant_profile.js
// Opening Hours: Quick Set, Clear, Copy to All Days
function updateTimeInputsVisibility(row) {
  const isClosed = row.querySelector('.is-closed-checkbox')?.checked;
  row.querySelectorAll('.open-time-input, .close-time-input').forEach(function(input) {
    input.style.display = isClosed ? 'none' : '';
  });
}

document.addEventListener('DOMContentLoaded', function() {
  // --- Error Alert for Form Errors ---
  var errorAlert = document.querySelector('.alert-danger');
  if (errorAlert) {
    var errorText = errorAlert.innerText.trim();
    if (errorText) {
      alert('Form Error:\n' + errorText);
    }
  }

  // --- Opening Hours logic ---
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

  // --- Address Management ---
  const feedbackMessage = document.getElementById('feedback-message');
  const addressList = document.getElementById('address-list');
  const newAddressInput = document.getElementById('new-address-input');
  const addAddressBtn = document.getElementById('add-address-btn');

  // Google Places Autocomplete for new address input
  let autocomplete = null;
  let selectedPlace = null;
  if (window.google && window.google.maps && window.google.maps.places && newAddressInput) {
    autocomplete = new google.maps.places.Autocomplete(newAddressInput);
    autocomplete.addListener('place_changed', function() {
      const place = autocomplete.getPlace();
      if (!place.formatted_address || !place.geometry || !place.geometry.location) {
        feedbackMessage.innerHTML = '<span class="text-danger">Please select a valid address from the dropdown.</span>';
        newAddressInput.classList.add('is-invalid');
        selectedPlace = null;
        return;
      }
      newAddressInput.classList.remove('is-invalid');
      newAddressInput.value = place.formatted_address;
      selectedPlace = place;
    });
  }

  if (addAddressBtn) {
    addAddressBtn.addEventListener('click', async function() {
      const addressValue = newAddressInput.value.trim();
      if (!addressValue || !selectedPlace || !selectedPlace.geometry || !selectedPlace.geometry.location) {
        feedbackMessage.innerHTML = '<span class="text-danger">Please select a valid address from the dropdown.</span>';
        newAddressInput.classList.add('is-invalid');
        return;
      }
      feedbackMessage.innerHTML = '<span class="text-primary">Saving address...</span>';
      try {
        // The URL below must be rendered by Django template
        const response = await fetch(window.ADDRESS_LIST_CREATE_URL, {
          method: "POST",
          headers: {"Content-Type": "application/json", "X-CSRFToken": window.CSRF_TOKEN},
          body: JSON.stringify({
            formatted_address: addressValue,
            latitude: selectedPlace.geometry.location.lat(),
            longitude: selectedPlace.geometry.location.lng()
          })
        });
        if (response.ok) {
          const newAddress = await response.json();
          addAddressToList(newAddress);
          feedbackMessage.innerHTML = '<span class="text-success">Address added!</span>';
          newAddressInput.value = '';
          selectedPlace = null;
        } else {
          const errorText = await response.text();
          feedbackMessage.innerHTML = `<span class="text-danger">Error: ${errorText}</span>`;
        }
      } catch (error) {
        feedbackMessage.innerHTML = '<span class="text-danger">A network error occurred.</span>';
        console.error("Save address error:", error);
      }
    });
  }

  function addAddressToList(address) {
    document.getElementById('no-addresses-alert')?.remove();
    const li = document.createElement('li');
    li.id = `address-${address.id}`;
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.innerHTML = `
      <span class="flex-grow-1 address-text">${address.formatted_address}</span>
      <input type="text" class="form-control d-none address-edit-input" value="${address.formatted_address}">
      <button type="button" class="btn btn-outline-secondary btn-sm edit-address-btn ms-2" data-address-id="${address.id}">
        <i class="bi bi-pencil"></i>
      </button>
      <button type="button" class="btn btn-outline-success btn-sm save-address-btn ms-2 d-none" data-address-id="${address.id}">
        <i class="bi bi-check"></i>
      </button>
      <button type="button" class="btn btn-outline-danger btn-sm delete-address-btn ms-2" data-address-id="${address.id}">
        <i class="bi bi-trash"></i>
      </button>
    `;
    addressList.appendChild(li);
    new bootstrap.Tooltip(li.querySelector('.delete-address-btn'));
  }

  if (addressList) {
    addressList.addEventListener('click', async function(event) {
      // Delete address
      const deleteButton = event.target.closest('.delete-address-btn');
      if (deleteButton) {
        const addressId = deleteButton.dataset.addressId;
        const url = `/locations/api/addresses/${addressId}/delete/`;
        if (!confirm('Are you sure you want to delete this address?')) return;
        try {
          const response = await fetch(url, {
            method: 'DELETE',
            headers: {'X-CSRFToken': window.CSRF_TOKEN}
          });
          if (response.ok) {
            document.getElementById(`address-${addressId}`).remove();
            if (addressList.children.length === 0) {
                addressList.innerHTML = '<li id="no-addresses-alert" class="list-group-item text-muted">No addresses saved yet.</li>';
            }
          } else {
            const errorData = await response.json();
            alert(`Failed to delete address: ${errorData.message || 'Unknown error'}`);
          }
        } catch (error) {
          console.error('Delete address error:', error);
          alert('A network error occurred while trying to delete the address.');
        }
        return;
      }
      // Edit address
      const editButton = event.target.closest('.edit-address-btn');
      if (editButton) {
        const li = editButton.closest('li');
        li.querySelector('.address-text').classList.add('d-none');
        li.querySelector('.address-edit-input').classList.remove('d-none');
        li.querySelector('.save-address-btn').classList.remove('d-none');
        editButton.classList.add('d-none');
        return;
      }
      // Save address
      const saveButton = event.target.closest('.save-address-btn');
      if (saveButton) {
        const addressId = saveButton.dataset.addressId;
        const li = saveButton.closest('li');
        const newAddress = li.querySelector('.address-edit-input').value;
        if (!newAddress.trim()) {
          alert('Address cannot be empty.');
          return;
        }
        try {
          const response = await fetch(`/locations/api/addresses/${addressId}/update/`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN},
            body: JSON.stringify({ formatted_address: newAddress })
          });
          if (response.ok) {
            li.querySelector('.address-text').textContent = newAddress;
            li.querySelector('.address-text').classList.remove('d-none');
            li.querySelector('.address-edit-input').classList.add('d-none');
            saveButton.classList.add('d-none');
            li.querySelector('.edit-address-btn').classList.remove('d-none');
          } else {
            let errorMessage = 'Unknown error';
            try {
              const errorData = await response.json();
              errorMessage = errorData.message || errorMessage;
            } catch (e) {
              errorMessage = await response.text();
            }
            alert(`Failed to update address: ${errorMessage}`);
          }
        } catch (error) {
          console.error('Update address error:', error);
          alert('A network error occurred while trying to update the address.');
        }
        return;
      }
    });
  }

  // --- Tooltips ---
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // --- Social Links Icon Auto-detect ---
  function getSocialIcon(url) {
    if (!url) return '<i class="bi bi-link-45deg text-secondary"></i>';
    url = url.toLowerCase();
    if (url.includes('facebook.com')) return '<i class="bi bi-facebook text-primary"></i>';
    if (url.includes('twitter.com') || url.includes('x.com')) return '<i class="bi bi-twitter-x text-dark"></i>';
    if (url.includes('instagram.com')) return '<i class="bi bi-instagram text-danger"></i>';
    if (url.includes('linkedin.com')) return '<i class="bi bi-linkedin text-primary"></i>';
    if (url.includes('youtube.com')) return '<i class="bi bi-youtube text-danger"></i>';
    if (url.includes('tiktok.com')) return '<i class="bi bi-tiktok text-dark"></i>';
    if (url.includes('pinterest.com')) return '<i class="bi bi-pinterest text-danger"></i>';
    if (url.includes('whatsapp.com')) return '<i class="bi bi-whatsapp text-success"></i>';
    if (url.includes('threads.net')) return '<i class="bi bi-threads text-dark"></i>';
    if (url.includes('snapchat.com')) return '<i class="bi bi-snapchat text-warning"></i>';
    return '<i class="bi bi-link-45deg text-secondary"></i>';
  }

  document.querySelectorAll('.social-icon').forEach(function(el) {
    const url = el.getAttribute('data-url');
    el.innerHTML = getSocialIcon(url);
  });

  // --- Logo Preview (for file input) ---
  const logoInput = document.querySelector('[name="logo"]');
  if (logoInput) {
    logoInput.addEventListener('change', function(event) {
      const preview = document.getElementById('logoPreview');
      const file = event.target.files[0];
      if (file) {
        preview.src = URL.createObjectURL(file);
      }
    });
  }

  // --- Expose Django variables for AJAX ---
  window.CSRF_TOKEN = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  window.ADDRESS_LIST_CREATE_URL = window.ADDRESS_LIST_CREATE_URL || '';
});
