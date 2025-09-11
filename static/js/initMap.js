window.initMap = function () {
  (function () {
    // --- Django Formset Logic ---
    function setupFormset(containerId, addBtnId, rowClass, removeBtnClass) {
      const container = document.getElementById(containerId);
      const addBtn = document.getElementById(addBtnId);
      if (!container || !addBtn) return;

      const prefix = container.dataset.prefix;
      const totalInput = container.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
      const template = document.getElementById(containerId.replace('-formset', '-empty-form'));

      function reindex(html, index) {
        return html
          .replaceAll(/__prefix__/g, index)
          .replaceAll(new RegExp(`${prefix}-\\d+`, 'g'), `${prefix}-${index}`);
      }

      addBtn.addEventListener('click', () => {
        const idx = parseInt(totalInput.value || "0", 10);
        const html = reindex(template.innerHTML, idx);
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        while (wrapper.firstChild) container.appendChild(wrapper.firstChild);
        totalInput.value = idx + 1;
      });

      container.addEventListener('click', (e) => {
        const btn = e.target.closest(`.${removeBtnClass}`);
        if (!btn) return;
        const row = btn.closest(`.${rowClass}`);
        if (row) row.remove();
      });
    }

    document.addEventListener('DOMContentLoaded', function () {
      setupFormset('social-formset', 'add-social-row', 'social-form-row', 'remove-social-row');
      setupFormset('hours-formset', 'add-hours-row', 'hours-form-row', 'remove-hours-row');
    });

    // --- Google Maps + Places ---
    let map, marker, geocoder;

    function q(id) { return document.getElementById(id); }
    function setVal(el, v) { if (el) el.value = v ?? ''; }

    function fillComponents(place) {
      if (!place || !place.address_components) return;
      const comp = {};
      place.address_components.forEach(c => c.types.forEach(t => comp[t] = c));

      const streetNumber = comp.street_number ? comp.street_number.long_name : '';
      const route = comp.route ? comp.route.long_name : '';
      const street = [streetNumber, route].filter(Boolean).join(' ').trim();

      const city =
        (comp.locality && comp.locality.long_name) ||
        (comp.postal_town && comp.postal_town.long_name) ||
        (comp.sublocality_level_1 && comp.sublocality_level_1.long_name) || '';

      const state = comp.administrative_area_level_1 ? comp.administrative_area_level_1.long_name : '';
      const zipcode = comp.postal_code ? comp.postal_code.long_name : '';
      const country = comp.country ? comp.country.long_name : '';

      setVal(q('id_street'), street);
      setVal(q('id_city'), city);
      setVal(q('id_state'), state);
      setVal(q('id_zipcode'), zipcode);
      setVal(q('id_country'), country);
    }

    function setPos(latLng, pan = true) {
      setVal(q('id_latitude'), latLng.lat());
      setVal(q('id_longitude'), latLng.lng());
      if (marker) marker.setPosition(latLng);
      if (map && pan) map.panTo(latLng);
    }

    function reverseGeocode(latLng) {
      geocoder = geocoder || new google.maps.Geocoder();
      geocoder.geocode({ location: latLng }, (results, status) => {
        if (status === 'OK' && results && results[0]) {
          const place = results[0];
          fillComponents(place);
        }
      });
    }

    window.addEventListener('load', function () {
      if (!(window.google && window.google.maps)) return;

      const lat = parseFloat(q('id_latitude')?.value || '');
      const lng = parseFloat(q('id_longitude')?.value || '');
      const hasCoords = !isNaN(lat) && !isNaN(lng);
      const center = hasCoords ? { lat, lng } : { lat: 51.5074, lng: -0.1278 };

      map = new google.maps.Map(q('map'), {
        center,
        zoom: hasCoords ? 15 : 12,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
      });

      marker = new google.maps.Marker({ map, position: center, draggable: true });
      if (!hasCoords) setPos(new google.maps.LatLng(center.lat, center.lng), false);

      marker.addListener('dragend', () => {
        const pos = marker.getPosition();
        setPos(pos, false);
        reverseGeocode(pos);
      });

      google.maps.event.addListener(map, 'click', (e) => {
        setPos(e.latLng);
        reverseGeocode(e.latLng);
      });

      // --- Place Autocomplete Integration ---
      const autocompleteElement = document.getElementById('address-autocomplete');
      const addressInputHidden = document.getElementById('address-input-hidden');
      const latInput = document.getElementById('id_latitude');
      const lngInput = document.getElementById('id_longitude');

      if (autocompleteElement) {
        autocompleteElement.addEventListener('gmpx-placechange', (event) => {
          const place = event.detail;
          if (place) {
            addressInputHidden.value = place.formatted_address || '';
            if (place.geometry && place.geometry.location) {
              latInput.value = place.geometry.location.lat;
              lngInput.value = place.geometry.location.lng;
              setPos(new google.maps.LatLng(
                place.geometry.location.lat,
                place.geometry.location.lng
              ));
              map.setZoom(16);
            }
            fillComponents(place);
          }
        });
      }
    });
  })();
};