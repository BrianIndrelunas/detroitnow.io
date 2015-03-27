/*
* Active data representing live content
* aggregated from ChartBeat, updated every 5 seconds
*/

var first_time = true;
var active_chart;

function connect_socket() {
  // Websocket used for constant streaming of data
  var ws = new WebSocket("ws://" + socket_domain  + "/active-socket");
  // Server sent a message to the client, update active map
  ws.onmessage = function(e) {
    var response = jQuery.parseJSON(e.data);
    var time = Math.round((new Date()).getTime() / 1000);

    if (response.hasOwnProperty("active")) {
      var active = response.active;
      //console.log(active);
      var act = active.read + active.write;
      var total = act + active.idle;
      var new_ratio = act / total;
      var new_percentage = parseInt(new_ratio * 100);
      var prev_percentage = parseInt($("#activity").text().replace(/,/g, ""));

      $("#activity")
      .prop("number", prev_percentage)
      .animateNumber({
        "number": new_percentage
      });

      var class_up = "fa-sort-asc";
      var class_down = "fa-sort-desc";

      $("#delta")
      .removeClass(class_up)
      .removeClass(class_down)
      .css("color", "#000");

      if (new_percentage > prev_percentage) {
        $("#delta").addClass(class_up).css("color", "#76b729");
      } else if (new_percentage < prev_percentage) {
        $("#delta").addClass(class_down).css("color", "#f04e55");
      }

      if (first_time == true) {
        //active_gauge = $("#active_gauge").epoch({ "type": "time.gauge", "value": new_ratio });
        chart = $("#line_chart").epoch({
          "type": "time.line",
          "axes": ["left", "bottom"],
          "data": [{
            "label": "Viewers",
            "values": [{ "time": time, "y": new_percentage }]
          }]
        });
        first_time = false;
      } else {
        //active_gauge.push(act / total);
        chart.push([{ "time": time, "y": new_percentage }]);
      }
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

