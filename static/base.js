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