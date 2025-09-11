let map, marker, autocomplete;

function initAutocompleteAndMap() {
  const defaultLocation = { lat: 40.7128, lng: -74.0060 }; // New York City

  // Initialize map
  map = new google.maps.Map(document.getElementById("map"), {
    center: defaultLocation,
    zoom: 13,
  });

  // Initialize marker
  marker = new google.maps.Marker({
    map: map,
    position: defaultLocation,
  });

  // Initialize autocomplete
  const input = document.getElementById("autocomplete");
  autocomplete = new google.maps.places.Autocomplete(input, { types: ["geocode"] });

  autocomplete.addListener("place_changed", function () {
    const place = autocomplete.getPlace();
    if (!place.geometry) {
      alert('No details available for input: ' + input.value);
      return;
    }
    map.setCenter(place.geometry.location);
    map.setZoom(17);
    marker.setPosition(place.geometry.location);

    // Fill hidden fields for testing
    document.getElementById("address").value = place.formatted_address || '';
    document.getElementById("lat").value = place.geometry.location.lat();
    document.getElementById("lng").value = place.geometry.location.lng();
  });
}

window.initAutocompleteAndMap = initAutocompleteAndMap;