/*
* Viewer data representing live content
* aggregated from ChartBeat, updated every 5 seconds
*/
var first = true;
var gauge;

$(function() {
  var ws = connect_socket();
});

function connect_socket() {
  // Websocket used for constant streaming of data
  var ws = new WebSocket("ws://" + base.socket_domain  + "/popular-socket");
  // Server sent a message to the client, update active map
  ws.onmessage = function(e) {
    var response = jQuery.parseJSON(e.data);
    var time = Math.round((new Date()).getTime() / 1000);

    if (response.hasOwnProperty("recirculation")) {
      var recirc = response.recirculation;
      var article = response.article;
      var new_ratio = recirc / article;
      var new_percentage = new_ratio * 100;
      var prev_percentage = parseFloat($("#recirculation").text().replace(/,/g, ""));

      if (first) {
        gauge = $("#gauge").epoch({
          "type": "time.gauge",
          "value": new_ratio
        });
        first = false;
      } else {
        gauge.push(new_ratio);
      }
    }
  };

  ws.onclose = function() {
    setTimeout(function() {
      connect_socket();
    }, base.reconnect_socket_timer);
  };

  return ws;
}
