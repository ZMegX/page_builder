(function () {
  const $ = window.jQuery;
  function byId(id) { return document.getElementById(id); }
  function setVal(el, v) { if (el) el.value = v ?? ''; }
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }
  // Elements
  const modalEl = byId('addressModal');
  if (!modalEl) return;

  const listSection = byId('address-list-section');
  const listContainer = byId('address-list-container');
  const formSection = byId('address-form-section');
  const showFormBtn = byId('show-address-form');
  const cancelBtn = byId('cancel-add-address');
  const form = byId('addressForm');
  const errorBox = byId('address-form-errors');

  const addrInput = byId('id_address');
  const idInput = byId('id_address_id');

  const streetInput = byId('id_street');
  const cityInput = byId('id_city');
  const stateInput = byId('id_state');
  const zipcodeInput = byId('id_zipcode');
  const countryInput = byId('id_country');
  const latInput = byId('id_latitude');
  const lngInput = byId('id_longitude');

  // Google Maps state
  let gmap, marker, geocoder, autocomplete;
  let mapReady = false;
  let apiLoaded = false;
  let mode = 'add'; // or 'edit'

  function parseComponents(place) {
    if (!place || !place.address_components) return;
    const map = {};
    place.address_components.forEach(c => c.types.forEach(t => map[t] = c));

    const streetNumber = map.street_number ? map.street_number.long_name : '';
    const route = map.route ? map.route.long_name : '';
    const street = [streetNumber, route].filter(Boolean).join(' ').trim();

    const city =
      (map.locality && map.locality.long_name) ||
      (map.postal_town && map.postal_town.long_name) ||
      (map.sublocality_level_1 && map.sublocality_level_1.long_name) || '';

    const state = map.administrative_area_level_1 ? map.administrative_area_level_1.long_name : '';
    const zipcode = map.postal_code ? map.postal_code.long_name : '';
    const country = map.country ? map.country.long_name : '';

    setVal(streetInput, street);
    setVal(cityInput, city);
    setVal(stateInput, state);
    setVal(zipcodeInput, zipcode);
    setVal(countryInput, country);
  }

  function setPosition(latLng, pan = true) {
    if (!latLng) return;
    setVal(latInput, latLng.lat());
    setVal(lngInput, latLng.lng());
    if (marker) marker.setPosition(latLng);
    if (gmap && pan) gmap.panTo(latLng);
  }

  function reverseGeocode(latLng) {
    geocoder = geocoder || new google.maps.Geocoder();
    geocoder.geocode({ location: latLng }, (results, status) => {
      if (status === 'OK' && results && results[0]) {
        const place = results[0];
        if (addrInput) addrInput.value = place.formatted_address;
        parseComponents(place);
      }
    });
  }

  function initMap() {
    if (mapReady) return;
    const lat = parseFloat(latInput && latInput.value);
    const lng = parseFloat(lngInput && lngInput.value);
    const hasCoords = !isNaN(lat) && !isNaN(lng);

    const center = hasCoords ? { lat, lng } : { lat: 51.5074, lng: -0.1278 };

    gmap = new google.maps.Map(byId('addressMap'), {
      center,
      zoom: hasCoords ? 15 : 12,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });

    marker = new google.maps.Marker({
      map: gmap,
      position: center,
      draggable: true,
    });

    if (!hasCoords) {
      setPosition(new google.maps.LatLng(center.lat, center.lng), false);
    }

    marker.addListener('dragend', function () {
      const pos = marker.getPosition();
      setPosition(pos, false);
      reverseGeocode(pos);
    });

    gmap.addListener('click', function (e) {
      setPosition(e.latLng);
      reverseGeocode(e.latLng);
    });

    if (addrInput) {
      const options = {
        fields: ['address_components', 'geometry', 'formatted_address'],
      };
      autocomplete = new google.maps.places.Autocomplete(addrInput, options);
      autocomplete.addListener('place_changed', function () {
        const place = autocomplete.getPlace();
        if (!place || !place.geometry || !place.geometry.location) return;
        addrInput.value = place.formatted_address || addrInput.value;
        parseComponents(place);
        const loc = place.geometry.location;
        setPosition(loc);
        gmap.setZoom(16);
      });
    }

    // Improve suggestions with browser geolocation (optional)
    if (navigator.geolocation && autocomplete) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const circle = new google.maps.Circle({
            center: { lat: pos.coords.latitude, lng: pos.coords.longitude },
            radius: pos.coords.accuracy,
          });
          autocomplete.setBounds(circle.getBounds());
        },
        () => {}
      );
    }

    mapReady = true;

    setTimeout(() => {
      if (gmap) google.maps.event.trigger(gmap, 'resize');
      if (marker) gmap.panTo(marker.getPosition());
    }, 200);
  }

  function loadGoogleMaps(cb) {
  if (window.google && window.google.maps) { cb(); return; }

  const apiKey = formSection.dataset.apiKey || '';
  if (!apiKey) { console.warn('Missing GOOGLE_MAPS_API_KEY'); return; }

  const existing = document.querySelector('script[data-googlemaps="1"]');
  if (existing) {
    if (window.google && window.google.maps) { cb(); return; }
    existing.addEventListener('load', () => cb(), { once: true });
    return;
  }

  const s = document.createElement('script');
  s.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&libraries=places`;
  s.async = true;
  s.defer = true;
  s.setAttribute('loading', 'async'); // <-- add this to silence the warning
  s.dataset.googlemaps = '1';
  s.onload = cb;
  document.head.appendChild(s);
}

  function toggleForm(show) {
    if (show) {
      listSection.style.display = 'none';
      formSection.style.display = '';
    } else {
      formSection.style.display = 'none';
      listSection.style.display = '';
      if (form) form.reset();
      if (addrInput) addrInput.value = '';
      mapReady = false; // force re-init next time
      mode = 'add';
      setVal(idInput, '');
      [streetInput, cityInput, stateInput, zipcodeInput, countryInput, latInput, lngInput].forEach(el => setVal(el, ''));
    }
    errorBox.textContent = '';
  }

  function prefillForEdit(addressId) {
    const apiKey = formSection.dataset.apiKey || '';
    const tpl = formSection.dataset.urlDetailTemplate || '';
    if (!tpl) return;
    const url = tpl.replace(/0(?!.*0)/, String(addressId)); // replace last '0' with id

    $.get(url)
      .done(function (data) {
        // Fill hidden fields
        setVal(idInput, data.id);
        setVal(streetInput, data.street);
        setVal(cityInput, data.city);
        setVal(stateInput, data.state);
        setVal(zipcodeInput, data.zipcode);
        setVal(countryInput, data.country);
        if (data.latitude && data.longitude) {
          setVal(latInput, data.latitude);
          setVal(lngInput, data.longitude);
        }
        setVal(addrInput, data.formatted || '');

        // Ensure map is ready and centered on coords (or geocode text)
        const afterMaps = function () {
          mapReady = false; // rebuild for fresh coords
          initMap();
          const hasCoords = data.latitude !== null && data.longitude !== null && data.latitude !== '' && data.longitude !== '';
          if (!hasCoords && addrInput.value) {
            // Try geocoding address_search to set position
            const gc = new google.maps.Geocoder();
            gc.geocode({ address: addrInput.value }, (results, status) => {
              if (status === 'OK' && results[0]) {
                const loc = results[0].geometry.location;
                setPosition(loc);
                parseComponents(results[0]);
              }
            });
          }
        };

        if (window.google && window.google.maps) {
          afterMaps();
        } else {
          loadGoogleMaps(apiKey, afterMaps);
        }
      })
      .fail(function () {
        errorBox.textContent = 'Failed to load the address for editing.';
      });
  }

  // Show Add form
  showFormBtn.addEventListener('click', function () {
    mode = 'add';
    toggleForm(true);
    const apiKey = formSection.dataset.apiKey || '';
    if (!apiKey) {
      console.warn('Missing GOOGLE_MAPS_API_KEY');
      return;
    }
    loadGoogleMaps(apiKey, function () {
      mapReady = false;
      initMap();
    });
  });

  // Cancel add/edit
  cancelBtn.addEventListener('click', function () {
    toggleForm(false);
  });

  // Delegate Edit button clicks (inside modal list)
  listContainer.addEventListener('click', function (e) {
    const btn = e.target.closest('.js-edit-address');
    if (!btn) return;
    const addressId = btn.getAttribute('data-address-id');
    if (!addressId) return;

    mode = 'edit';
    toggleForm(true);
    prefillForEdit(addressId);
  });

  // Optionally also delegate from the main list outside the modal
  const mainList = document.getElementById('addressesListMain');
  if (mainList) {
    mainList.addEventListener('click', function (e) {
      const btn = e.target.closest('.js-edit-address');
      if (!btn) return;
      e.preventDefault();
      const addressId = btn.getAttribute('data-address-id');
      mode = 'edit';
      // Ensure modal is shown
      const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
      bsModal.show();
      // Switch view
      toggleForm(true);
      prefillForEdit(addressId);
    });
  }

  // Submit Add/Edit via AJAX
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      errorBox.textContent = '';

      if (!streetInput.value || !cityInput.value || !countryInput.value) {
        errorBox.textContent = 'Please select a full address from the suggestions or place the marker.';
        return;
      }

      // Choose endpoint
      let url;
      if (mode === 'edit') {
        const tpl = formSection.dataset.urlUpdateTemplate || '';
        const id = idInput.value;
        url = tpl.replace(/0(?!.*0)/, String(id));
      } else {
        url = formSection.dataset.urlAdd;
      }

      const data = $(form).serialize();
      $.ajax({
        url: url,
        method: 'POST',
        data: data,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (res) {
          if (res.address_list_html) {
            // Update list inside modal
            listContainer.innerHTML = res.address_list_html;
            // Update main list if present
            if (mainList) mainList.innerHTML = res.address_list_html;
          }
          toggleForm(false);
        },
        error: function (xhr) {
          const json = xhr.responseJSON;
          if (json && json.errors) {
            errorBox.innerHTML = json.errors;
          } else {
            errorBox.textContent = 'An error occurred while saving the address.';
          }
        }
      });
    });
  }

  // Auto-init map when modal is shown and form is visible
  modalEl.addEventListener('shown.bs.modal', function () {
    if (formSection.style.display !== 'none') {
      const apiKey = formSection.dataset.apiKey || '';
      if (!apiKey) return;
      loadGoogleMaps(apiKey, function () {
        if (!mapReady) initMap();
      });
    }
  });
})();