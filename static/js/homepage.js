
console.log('Loading Google Maps...');

async function loadGoogleMaps() {
  console.log('Inside loadGoogleMaps, window.addresses:', window.addresses);
  const { Map, InfoWindow } = await google.maps.importLibrary('maps');
  const Marker = google.maps.Marker;
  const LatLngBounds = google.maps.LatLngBounds;
  if (!window.addresses.length) return;
  const map = new Map(document.getElementById('restaurants-map'), {
    zoom: 12,
    center: {lat: window.addresses[0].lat || 48.8566, lng: window.addresses[0].lng || 2.3522},
    mapTypeControl: false,
    streetViewControl: false,
  });

  const bounds = new LatLngBounds();
  let hasMarker = false;

  window.addresses.forEach(r => {
    if (r.lat && r.lng) {
      hasMarker = true;
      const marker = new Marker({
        position: {lat: r.lat, lng: r.lng},
        map: map,
        title: r.name,
      });
      bounds.extend(marker.getPosition());
      const infowindow = new InfoWindow({
        content: `
          <div class="homepage" style="min-width:180px;max-width:240px;">
            ${r.logo ? `<img src="${r.logo}" class="homepage" style="width:100%;max-height:80px;object-fit:cover;border-radius:8px;margin-bottom:6px;">` : ''}
            <strong>${r.name}</strong><br>
            ${r.address}<br>
            ${r.url !== '#' ? `<a href="${r.url}" class="btn btn-sm btn-primary mt-2 homepage">View Page</a>` : ''}
          </div>
        `
      });
      marker.addListener('click', function() {
        infowindow.open(map, marker);
      });
    }
  });

  if (hasMarker) {
    map.fitBounds(bounds);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  if (window.google && google.maps && google.maps.importLibrary) {
    loadGoogleMaps();
  } else {
    // fallback: load script dynamically if not present
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${window.GOOGLE_MAPS_API_KEY || ''}&libraries=maps`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      if (google.maps.importLibrary) loadGoogleMaps();
    };
    document.head.appendChild(script);
  }
});

(function(g){
  var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;
  b=b[c]||(b[c]={});
  var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{
    await (a=m.createElement("script"));
    e.set("libraries",[...r]+"");
    for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);
    e.set("callback",c+".maps."+q);
    a.src=`https://maps.${c}apis.com/maps/api/js?`+e;
    d[q]=f;
    a.onerror=()=>h=n(Error(p+" could not load."));
    a.nonce=m.querySelector("script[nonce]")?.nonce||"";
    m.head.append(a);
  }));
  d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))
})({
  key: window.GOOGLE_MAPS_API_KEY,
  v: "weekly"
});
