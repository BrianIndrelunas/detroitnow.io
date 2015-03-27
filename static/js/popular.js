/*
* Top pages representing the most active content
* aggregated from ChartBeat, updated every 5 seconds
*/
requirejs(["config"], function(config){
    requirejs(["jquery", "base", "handlebars", "jquery.shuffle.modernizr", "animateNumber"], function($, base, handlebars) {
        var source = $("#popular_template").html();
        var template = handlebars.compile(source);

        $("#shuffle_data").on('removed.shuffle', function(evt, $collection, shuffle) {
            shuffle_sort();
        });

        $("#shuffle_data").shuffle({
            "itemSelector": ".shuff",
            "sizer": $("#shuffle_data").find(".shuffle__sizer")
        });

        function connect_socket() {
            // Websocket used for constant streaming of data
            var ws = new WebSocket("ws://" + base.socket_domain  + "/popular-socket");
            // Server sent a message to the client, update dashboard
            ws.onmessage = function(e) {
                var response = jQuery.parseJSON(e.data);

                if (response.hasOwnProperty("visits")) {
                    var prev_val = $("#concurrent").text();
                    $("#concurrent").prop("number", parseInt(prev_val))
                                    .animateNumber({ "number": response.visits });
                }

                if (response.hasOwnProperty("popular")) {

                    $(".loading").remove();

                    var data = response.popular;
                    for (var i = 0, len = data.length; i < len; i++) {
                        var page = data[i];
                        var found = false;
                        $("#shuffle_data").find("a").each(function() {
                            if ($(this).attr("href") == "http://" + page.path) {
                                found = true;
                                var val_el = $(this).parent().find(".shuff_val");
                                var prev_val = val_el.text();
                                val_el
                                    .prop("number", parseInt(prev_val))
                                    .animateNumber({ "number": page.visits });
                            }
                        });
                        if (!found) {
                            var title = page.title.split("|");
                            title = title[0];

                            //add link
                            var content = template({
                                "href": page.path,
                                "title": title
                            });
                            $("#shuffle_data").append(content);
                            $(".shuff_val")
                                .last()
                                .animateNumber({ "number": page.visits });
                            $("#shuffle_data").shuffle("appended", $(".shuff").last());
                        }
                    }

                    //remove links not found in the live stream
                    $("#shuffle_data").find("a").each(function() {
                        var found = false;
                        for (var i = 0, len = data.length; i < len; i++) {
                            var page = data[i];
                            if ($(this).attr("href") == "http://" + page.path) {
                                found = true;
                            }
                        }
                        if (!found) {
                            var that = this
                            setTimeout(function() {
                                $("#shuffle_data").shuffle("remove", $(that).parent().parent());
                            }, 1000);
                        }
                    });

                    shuffle_sort();

                }
            };

            ws.onclose = function() {
                setTimeout(function() {
                    connect_socket();
                }, base.reconnect_socket_timer);
            };

            return ws;
        };

        var ws = connect_socket();

        function shuffle_sort() {
            $("#shuffle_data").shuffle("sort", {
                "reverse": true,
                "by": function($el) {
                    return parseInt($el.find(".shuff_val").text());
                }
            });
        };

    });
});