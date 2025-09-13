// This function will run once the entire page is loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Find the map element in the HTML
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error("Map element with ID 'map' not found.");
        return;
    }

    // --- 1. Read the API Key and URL from the HTML ---
    // This is the most critical part. We get the data passed from the Django template.
    const apiKey = mapElement.dataset.apiKey;
    const apiUrl = mapElement.dataset.apiUrl;

    // --- 2. Check if the API Key exists ---
    // If the key is missing, we stop everything and show an error.
    if (!apiKey) {
        console.error("CRITICAL: Google Maps API Key is missing. Check the 'data-api-key' attribute on the #map element in your HTML template.");
        mapElement.innerHTML = '<div style="padding: 20px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: .25rem;">Error: Google Maps API Key not found. The map cannot be loaded. Please check your .env configuration.</div>';
        return;
    }

    // --- 3. Load the Google Maps API ---
    // This function loads the Google Maps script and calls our initMap function when it's ready.
    function loadGoogleMaps() {
        if (window.google && window.google.maps) {
            // If maps is already loaded, just initialize
            initMap();
        } else {
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,marker&callback=initMap`;
            script.async = true;
            script.defer = true;
            // We attach our initMap function to the window object so the callback can find it.
            window.initMap = initMap;
            document.head.appendChild(script);
            script.onerror = () => {
                console.error("Failed to load Google Maps script. Check your API key and network connection.");
            };
        }
    }

    // --- 4. Initialize the map and its features ---
    // This is the main function that runs after the API is loaded.
    async function initMap() {
        const { Map, InfoWindow } = await google.maps.importLibrary("maps");
        const { PlaceAutocompleteElement } = await google.maps.importLibrary("places");
        const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

        const map = new Map(mapElement, {
            center: { lat: 40.7128, lng: -74.0060 },
            zoom: 10,
            mapId: "DELIVERY_MAP_ID"
        });

        const autocompleteEl = new PlaceAutocompleteElement({
            inputElement: document.getElementById("autocomplete"),
        });

        let selectedPlaceData = null;
        autocompleteEl.addEventListener("gmp-placechange", ({ place }) => {
            if (!place.geometry || !place.formattedAddress) {
                selectedPlaceData = null;
                return;
            }
            selectedPlaceData = {
                formatted_address: place.formattedAddress,
                latitude: place.geometry.location.lat(),
                longitude: place.geometry.location.lng(),
            };
        });

        const infoWindow = new InfoWindow();
        const addMarker = (addr) => {
            const marker = new AdvancedMarkerElement({
                position: { lat: addr.latitude, lng: addr.longitude },
                map: map,
                title: addr.formatted_address,
            });
            marker.addListener('click', () => {
                infoWindow.setContent(addr.formatted_address);
                infoWindow.open(map, marker);
            });
        };

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error('Network response was not ok');
            const addresses = await response.json();
            if (addresses.length > 0) {
                addresses.forEach(addMarker);
                map.setCenter({ lat: addresses[0].latitude, lng: addresses[0].longitude });
            }
        } catch (error) {
            console.error('Error loading addresses:', error);
        }
        
        document.getElementById('save-address').addEventListener('click', async () => {
            if (!selectedPlaceData) {
                alert("Please select a valid address from the dropdown.");
                return;
            }
            const feedbackEl = document.getElementById('feedback-message');
            const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                    body: JSON.stringify(selectedPlaceData),
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Failed to save address.');
                feedbackEl.textContent = 'Address saved successfully!';
                feedbackEl.className = 'mt-2 text-success';
                addMarker(data);
                map.setCenter({ lat: data.latitude, lng: data.longitude });
                document.getElementById('autocomplete').value = '';
                selectedPlaceData = null;
                setTimeout(() => feedbackEl.textContent = '', 3000);
            } catch (error) {
                console.error('Error saving address:', error);
                feedbackEl.textContent = error.message;
                feedbackEl.className = 'mt-2 text-danger';
            }
        });
    }

    // Start the process
    loadGoogleMaps();
});