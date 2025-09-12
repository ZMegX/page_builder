let map, marker, autocomplete;

function initAutocompleteAndMap() {
  const defaultLocation = { lat: 40.7128, lng: -74.0060 }; // Default: New York City

  // Initialize the map
  map = new google.maps.Map(document.getElementById("map"), {
    center: defaultLocation,
    zoom: 13,
  });

  // Initialize the marker at the default location
  marker = new google.maps.Marker({
    map: map,
    position: defaultLocation,
  });

  // Set up autocomplete on the input field
  const input = document.getElementById("autocomplete");
  autocomplete = new google.maps.places.Autocomplete(input, { types: ["geocode"] });

  // Listen for place selection
  autocomplete.addListener("place_changed", function () {
    const place = autocomplete.getPlace();
    if (!place.geometry) {
      alert('No details available for input: ' + input.value);
      return;
    }

    // Update map and marker
    map.setCenter(place.geometry.location);
    map.setZoom(17);
    marker.setPosition(place.geometry.location);

    // Fill hidden fields with address and coordinates
    document.getElementById("address").value = place.formatted_address || '';
    document.getElementById("lat").value = place.geometry.location.lat();
    document.getElementById("lng").value = place.geometry.location.lng();
  });
}

// Attach to window for the API callback
window.initAutocompleteAndMap = initAutocompleteAndMap;