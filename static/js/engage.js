/*
* Engagement data representing live content
* aggregated from ChartBeat, updated every 5 seconds
*/
$(function() {
  $("#engage_data").shuffle({
      "itemSelector": ".shuff",
      "sizer": $("#engage_data").find(".shuffle__sizer")
  });

  function connect_socket() {
    // Websocket used for constant streaming of data
    var ws = new WebSocket("ws://" + socket_domain  + "/engagesocket");
    // Server sent a message to the client, update geo map
    ws.onmessage = function(e) {
      var response = jQuery.parseJSON(e.data);

      if (response.hasOwnProperty("users")) {
          $("#concurrent").html(response['users']);
      }

      if (response.hasOwnProperty("engage")) {
        var data = response.engage;
        for (site in data) {
          var found = false;
          $("#engage_data > .shuff > div").each(function() {
            if ($(this).data("host") == site) {
              found = true;
              var val_el = $(this).find(".eng_avg");
              var prev_avg = val_el.text();
              val_el
                .prop("number", parseFloat(prev_avg))
                .animateNumber({
                    "number": data[site].avg
                });
            }
          });
          if (!found) {
            var content = '<div class="row shuff">' +
                            '<div class="col-md-12" data-host="' + site + '" data-groups="[\'engage\']">' +
                            '   <strong>' + site + '</strong>: <span class="eng_avg">0</span>' +
                            '</div>' +
                          '</div>';
            $("#engage_data").append(content);
            $(".eng_avg").last().animateNumber({ "number": data[site].avg });
            $("#engage_data").shuffle("appended", $(".shuff").last());
          }
        }

        $("#engage_data").shuffle("sort", {
          "reverse": true,
          "by": function($el) {
              return parseInt($el.find(".eng_avg").text());
          }
        });
      }
    };

    ws.onclose = function() {
      setTimeout(function() {
          connect_socket();
      }, reconnect_socket_timer);
    };

    return ws;
  };

  var ws = connect_socket();

});