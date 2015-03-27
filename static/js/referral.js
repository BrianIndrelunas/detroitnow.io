/*
* Referral data representing live content
* aggregated from ChartBeat, updated every 5 seconds
*/
$(function() {
  var source = $("#referral_template").html();
  var template = handlebars.compile(source);
  var threshold = 2;

  $("#shuffle_data").on('removed.shuffle', function(evt, $collection, shuffle) {
    shuffle_sort();
  });

  $("#shuffle_data").shuffle({
    "itemSelector": ".shuff",
    "sizer": $("#shuffle_data").find(".shuffle__sizer")
  });

  var ws = connect_socket();
});

function connect_socket() {
  // Websocket used for constant streaming of data
  var ws = new WebSocket("ws://" + base.socket_domain  + "/referral-socket");
  // Server sent a message to the client, update referral map
  ws.onmessage = function(e) {
    var response = jQuery.parseJSON(e.data);
    console.log(response);

    if (response.hasOwnProperty("referral")) {
      $(".loading").remove();

      var data = response.referral;
      for (key in data) {
        if (!data.hasOwnProperty(key)) {
          continue;
        }
        if (data[key] <= threshold) {
          continue;
        }
        var found = false;
        $("#shuffle_data").find(".referral-domain").each(function() {
          var val = $(this).text();
          if (val == key) {
            found = true;
            var val_el = $(this).parent().find(".shuff_val");
            var prev_val = val_el.text();
            val_el
                .prop("number", parseInt(prev_val))
                .animateNumber({ "number": data[key] });
          }
        });

        if (!found) {
          //add link
          var content = template({
              "domain": key
          });
          $("#shuffle_data").append(content);
          $(".shuff_val")
              .last()
              .animateNumber({ "number": data[key] });
          $("#shuffle_data").shuffle("appended", $(".shuff").last());
        }
      }

      //remove links not found in the live stream
      $("#shuffle_data").find(".referral-domain").each(function() {
        var found = false;
        for (key in data) {
          if (!data.hasOwnProperty(key)) {
            continue;
          }
          if (data[key] <= threshold) {
            continue;
          }
          var val = $(this).text();
          if (val == key) {
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

      setTimeout(shuffle_sort, 1000);
      //shuffle_sort();
    }
  };

  ws.onclose = function() {
    setTimeout(function() {
        connect_socket();
    }, base.reconnect_socket_timer);
  };

  return ws;
}

function shuffle_sort() {
  $("#shuffle_data").shuffle("sort", {
    "reverse": true,
    "by": function($el) {
      return parseInt($el.find(".shuff_val").text());
    }
  });
}