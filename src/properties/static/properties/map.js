function initMap() {
    // Initial Map Setup
    const centerMap = { lat: 54.3739089, lng: 18.6143757 };

    const map = new google.maps.Map(document.getElementById("google-map"), {
        center: centerMap,
        zoom: 15,
        disableDefaultUi: true
    });

    const infoWindow = new google.maps.InfoWindow();
    const bounds = new google.maps.LatLngBounds();

    // Loop through markers
    for (let i = 0; i < markers.length; i++) {
        const markerData = markers[i];

        const marker = new google.maps.Marker({
            position: { lat: markerData.lat, lng: markerData.lng },
            map: map,
            title: markerData.name
        });

        const infoWindowContent = `
            <div>
                <h3>${markerData.locationName}</h3>
                <address>
                    <p>${markerData.address}</p>
                </address>
            </div>`;

        // Add Click Listener to Marker
        google.maps.event.addListener(marker, 'click', function() {
            infoWindow.setContent(infoWindowContent);
            infoWindow.open(map, marker);
        });

        bounds.extend(new google.maps.LatLng(markerData.lat, markerData.lng));
    }
}
