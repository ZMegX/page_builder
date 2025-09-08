(function () {
  // Helpers
  function qs(id) { return document.getElementById(id); }
  function setVal(input, val) { if (input) input.value = val || ''; }

  // Map state
  let map, marker, geocoder, autocomplete;

  // Parse address components from Google Place into your fields
  function applyAddressComponents(place) {
    if (!place || !place.address_components) return;

    const components = {};
    place.address_components.forEach((comp) => {
      comp.types.forEach((type) => { components[type] = comp; });
    });

    // Street = street_number + route
    const streetNumber = components.street_number ? components.street_number.long_name : '';
    const route = components.route ? components.route.long_name : '';
    const street = [streetNumber, route].filter(Boolean).join(' ').trim();

    // City can be 'locality', sometimes 'postal_town' or 'sublocality_level_1'
    const city =
      (components.locality && components.locality.long_name) ||
      (components.postal_town && components.postal_town.long_name) ||
      (components.sublocality_level_1 && components.sublocality_level_1.long_name) ||
      '';

    const state = components.administrative_area_level_1 ? components.administrative_area_level_1.long_name : '';
    const zipcode = components.postal_code ? components.postal_code.long_name : '';
    const country = components.country ? components.country.long_name : '';

    setVal(qs('id_street'), street);
    setVal(qs('id_city'), city);
    setVal(qs('id_state'), state);
    setVal(qs('id_zipcode'), zipcode);
    setVal(qs('id_country'), country);
  }

  // Update lat/lng fields and marker position
  function setPosition(latLng, moveMarker = true, panMap = true) {
    const latInput = qs('id_latitude');
    const lngInput = qs('id_longitude');
    if (!latLng) return;
    setVal(latInput, latLng.lat());
    setVal(lngInput, latLng.lng());
    if (marker && moveMarker) marker.setPosition(latLng);
    if (map && panMap) map.panTo(latLng);
  }

  // Reverse geocode a LatLng into fields and set address_search text
  function reverseGeocode(latLng) {
    if (!geocoder) geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: latLng }, (results, status) => {
      if (status === 'OK' && results && results[0]) {
        const place = results[0];
        // Fill the visible address input with the formatted address
        const addrInput = qs('id_address');
        if (addrInput) addrInput.value = place.formatted_address;
        // Fill components
        applyAddressComponents(place);
      }
    });
  }

  // Public callback from Google script tag
  window.initAddressMap = function () {
    const addrInput = qs('id_address');
    const lat = parseFloat((qs('id_latitude') && qs('id_latitude').value) || '');
    const lng = parseFloat((qs('id_longitude') && qs('id_longitude').value) || '');

    const hasInitialCoords = !isNaN(lat) && !isNaN(lng);
    const defaultCenter = hasInitialCoords ? { lat: lat, lng: lng } : { lat: 51.5074, lng: -0.1278 }; // London default; change if you like

    map = new google.maps.Map(qs('map'), {
      center: defaultCenter,
      zoom: hasInitialCoords ? 15 : 12,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });

    marker = new google.maps.Marker({
      map,
      position: defaultCenter,
      draggable: true,
    });

    setPosition(new google.maps.LatLng(defaultCenter.lat, defaultCenter.lng), false, false);

    // Places Autocomplete
    if (addrInput) {
      const options = {
        fields: ['address_components', 'geometry', 'formatted_address'],
        // componentRestrictions: { country: ['us', 'gb'] }, // optionally restrict countries
      };
      autocomplete = new google.maps.places.Autocomplete(addrInput, options);
      autocomplete.addListener('place_changed', function () {
        const place = autocomplete.getPlace();
        if (!place || !place.geometry || !place.geometry.location) return;

        applyAddressComponents(place);
        const loc = place.geometry.location;
        setPosition(loc, true, true);
        map.setZoom(16);
      });
    }

    // Marker drag updates lat/lng + reverse geocode to fill text/components
    marker.addListener('dragend', function () {
      const pos = marker.getPosition();
      setPosition(pos, true, false);
      reverseGeocode(pos);
    });

    // Optional: click map to move marker
    map.addListener('click', function (e) {
      setPosition(e.latLng, true, false);
      reverseGeocode(e.latLng);
    });

    // Optional: geolocate to improve suggestions (does not set position)
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const circle = new google.maps.Circle({
            center: { lat: pos.coords.latitude, lng: pos.coords.longitude },
            radius: pos.coords.accuracy,
          });
          if (autocomplete) autocomplete.setBounds(circle.getBounds());
        },
        () => {}
      );
    }
  };
})();