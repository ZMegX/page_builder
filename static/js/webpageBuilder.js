document.addEventListener("DOMContentLoaded", () => {
  // Advanced Options Toggle
  const toggleAdvanced = document.getElementById('toggle-advanced');
  const advForm = document.getElementById('advanced-form');
  toggleAdvanced.addEventListener('change', () => {
    advForm.style.display = toggleAdvanced.checked ? '' : 'none';
    document.querySelectorAll('.advanced-component-fields').forEach(el => el.style.display = toggleAdvanced.checked ? '' : 'none');
  });

  // Component Forms Logic
  function toggleMenuItemFields(form) {
    const typeSelect = form.querySelector('[name$="-type"]');
    const menuFields = form.querySelector('.menu-item-fields');
    menuFields.style.display = (typeSelect.value === 'menu_item') ? '' : 'none';
  }

  document.querySelectorAll('.component-form').forEach(form => {
    toggleMenuItemFields(form);
    form.querySelector('[name$="-type"]').addEventListener('change', () => toggleMenuItemFields(form));
  });

  const componentsList = document.getElementById('components-list');
  const addBtn = document.getElementById('add-component-btn');
  const totalForms = document.getElementById('id_form-TOTAL_FORMS');

  function reindexForms() {
    document.querySelectorAll('.component-form').forEach((form, idx) => {
      form.dataset.index = idx;
      form.querySelectorAll('input, select, textarea').forEach(el => {
        if (el.name) el.name = el.name.replace(/form-\d+-/, `form-${idx}-`);
        if (el.id) el.id = el.id.replace(/form-\d+-/, `form-${idx}-`);
        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/form-\d+-/, `form-${idx}-`);
      });
    });
    totalForms.value = document.querySelectorAll('.component-form').length;
  }

  function updateRemoveButtons() {
    document.querySelectorAll('.btn-remove-component').forEach(btn => {
      btn.onclick = () => {
        const forms = document.querySelectorAll('.component-form');
        if (forms.length === 1) {
          btn.closest('.component-form').querySelectorAll('input, select, textarea').forEach(el => {
            if (el.type !== 'checkbox') el.value = '';
            else el.checked = false;
          });
        } else {
          btn.closest('.component-form').remove();
          reindexForms();
        }
      };
    });
  }
  updateRemoveButtons();

  addBtn.addEventListener('click', e => {
    e.preventDefault();
    const lastForm = document.querySelectorAll('.component-form');
    const newForm = lastForm[lastForm.length - 1].cloneNode(true);
    newForm.querySelectorAll('input, select, textarea').forEach(el => {
      if (el.type !== 'checkbox') el.value = '';
      else el.checked = false;
    });
    componentsList.appendChild(newForm);
    reindexForms();
    updateRemoveButtons();
    toggleMenuItemFields(newForm);
    if (toggleAdvanced.checked) newForm.querySelector('.advanced-component-fields').style.display = '';
  });

  // Google Maps + Autocomplete
  const input = document.getElementById("id_address");
  const latField = document.getElementById("id_latitude");
  const lngField = document.getElementById("id_longitude");

  const map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 59.9139, lng: 10.7522 },
    zoom: 13,
  });
  const marker = new google.maps.Marker({ map: map });

  if (latField.value && lngField.value) {
    const loc = { lat: parseFloat(latField.value), lng: parseFloat(lngField.value) };
    map.setCenter(loc);
    map.setZoom(15);
    marker.setPosition(loc);
  }

  const autocomplete = new google.maps.places.Autocomplete(input);
  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();
    if (!place.geometry) return alert("No details available for this address.");
    map.setCenter(place.geometry.location);
    map.setZoom(15);
    marker.setPosition(place.geometry.location);
    latField.value = place.geometry.location.lat();
    lngField.value = place.geometry.location.lng();
  });
});
