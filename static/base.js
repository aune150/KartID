function vedOppdateringAvTyp (t) {
    if (t.type == "change") {t = t.target};

    var h = document.getElementById("hva");
    var e = document.getElementById("eventorID");
    if (t.value == "Trening") {
        h.selectedIndex = 0;

        e.hidden = true;
        e.labels[0].hidden = true;
        document.getElementById("eventorIDRow").hidden = true;
    } else {
        h.selectedIndex = 3;

        e.hidden = false;
        e.labels[0].hidden = false;
        document.getElementById("eventorIDRow").hidden = false;
    };

    for (let i; i<3; i++) {
        h.children[i].hidden = !(t.value == "Trening")
    };
    for (let i=3; i<10; i++) {
        h.children[i].hidden = t.value == "Trening"
    };
};

var O = L.icon({
    iconUrl: "/static/O.png",
    iconSize: [25, 25],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15],
});

function a (e) {
    document.getElementById("lat").value = marker.getLatLng()["lat"]
    document.getElementById("lng").value = marker.getLatLng()["lng"]
};

function visKart () {
    const map = L.map('map').setView([63.43, 10.39], 10);
    
    
    const topo4 = L.tileLayer(
        'https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo4&zoom={z}&x={x}&y={y}', {
            attribution: '&copy; <a href="http://www.kartverket.no">Kartverket</a>'
        });
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });
    osm.addTo(map);
    L.control.layers({
        "OpenStreetMap": osm,
        "Norgeskart": topo4
    }).addTo(map);

    return map;
}