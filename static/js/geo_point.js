requirejs(["config"], function(config){

    requirejs(["base", "jquery", "bootstrap", "handlebars", "leaflet" ], function(base, $, bootstrap, handlebars){

        // Handlebars tempalte
        var marker_popup_template = handlebars.compile($("#marker-popup-template").html());

        handlebars.registerHelper("getPlatformImage", function(options){

            var platform = this.platform.toLowerCase();

            if (platform == "desktop"){
                return "<i class='fa fa-desktop fa-3x'></i>"
            }
            else if (platform == "mobile"){
                return "<i class='fa fa-mobile fa-5x'></i>"
            }
            else if (platform == "tablet"){
                return "<i class='fa fa-tablet fa-5x'></i>"
            }
            else{
                return platform;
            }
        });


        var map = L.map("map", { zoomControl:false })
                    .setView([39.5, -96.196289], 5);

        // create the tile layer with correct attribution
        // add an OpenStreetMap tile layer
        L.tileLayer('http://{s}.tile.stamen.com/watercolor/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        var marker;

        function toTitleCase(str) {
            return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
        }

        function connect_socket() {
            // Websocket used for constant streaming of data
            var ws = new WebSocket("ws://" + base.socket_domain  + "/geopoint-socket");
            // Server sent a message to the client, update dashboard
            ws.onmessage = function(e) {
                var response = jQuery.parseJSON(e.data);

                if (response.hasOwnProperty("users")) {
                    $("#concurrent").html(response.users);
                }

                if (response.hasOwnProperty("geo_point")) {
                    var person = response.geo_point;

                    //place marker
                    var data = {
                        "title": person.title,
                        "path": person.path,
                        "platform": person.platform,
                        "host": person.host.replace(".com", ""),
                    };

                    // Remove the currently placed point, if it exists
                    if (!marker){
                        marker = L.marker([person.lat, person.lng]).addTo(map);
                    }
                    else{
                        marker.setLatLng([person.lat, person.lng]).update();
                    }

                    map.setView([person.lat + 3, person.lng]);

                    var popup = L.popup({"className" : "marker-popup-class"}).
                                    setContent(marker_popup_template(data));
                    marker.bindPopup(popup).openPopup();

                }
            };

            ws.onclose = function() {
                setTimeout(function() {
                    connect_socket();
                }, base.reconnect_socket_timer);
            };

            return ws;
        }

        var ws = connect_socket();

    });
});
