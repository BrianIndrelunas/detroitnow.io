/*
* Viewer data representing live content
* aggregated from ChartBeat, updated every 5 seconds
*/

var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',');
var yday_data;
var chart = null;
var first = true;

var ws = connect_socket();

function get_time(start, frequency, length) {
  arr = ["x"];
  var cur_time = start;
  for (var i = 0; i < length; i++) {
    arr.push(cur_time * 1000);
    cur_time += frequency;
  }
  return arr;
}

function format_time(x) {
  var a = new Date(x * 1000);
  var hour = a.getHours();
  var min = a.getMinutes();
  //var sec = a.getSeconds();
  var ampm = "AM";
  if (hour >= 12) {
    hour = hour - 12;
    ampm = "PM";
  }
  if (hour == 0) {
    hour = 12;
  }
  min = min < 10 ? "0" + min : min;
  //sec = sec < 10 ? "0"+sec : sec;
  return hour + ":" + min + " " + ampm;
}

function connect_socket() {
  // Websocket used for constant streaming of data
  var ws = new WebSocket("ws://" + base.socket_domain  + "/viewers-socket");
  // Server sent a message to the client, update active map
  ws.onmessage = function(e) {
    var response = jQuery.parseJSON(e.data);
      //console.log(response);
      //var time = Math.round((new Date()).getTime() / 1000);

    if (response.hasOwnProperty("visits")) {
      var new_val = response.visits;
      var prev_val = parseFloat($("#viewers").text().replace(/,/g, ""));

      $("#viewers")
      .prop("number", parseFloat($("#viewers").text().replace(/,/g, "")))
      .animateNumber({
        "number": new_val,
        "numberStep": comma_separator_number_step
      });

      var class_up = "fa-sort-asc";
      var class_down = "fa-sort-desc";

      $("#delta")
        .removeClass(class_up)
        .removeClass(class_down)
        .css("color", "#000");

      if (new_val > prev_val) {
        $("#delta").addClass(class_up).css("color", "#76b729");
      } else if (new_val < prev_val) {
        $("#delta").addClass(class_down).css("color", "#f04e55");
      }
    }

    if (response.hasOwnProperty("viewers_today")) {
      var today_data = response.viewers_today.series;
      var time = get_time(response.viewers_today.start, response.viewers_today.frequency * 60, yday_data.length);
      today_data.unshift("Today");
      if (first) {
        yday_data.unshift("Yesterday");
        chart = c3.generate({
          "bindto": '#line_chart',
          "data": {
            "x": "x",
            "columns": [
              time,
              today_data,
              yday_data
            ],
            "colors": {
              "Today": "#ffee83",
              "Yesterday": "#f04e55"
            },
            "types": {
              "Today": "area-spline",
              "Yesterday": "area-spline"
            }
          },
          "axis": {
            "x": {
              "type": "timeseries",
              "tick": {
                "count": 24,
                "format": "%H:%M"
              }
            }
          },
          "tooltip": {
            "show": false
          },
          "point": {
            "show": false
          }
        });
        first = false;
      } else {
        chart.load({
          "columns": [today_data]
        });
      }
    }

    if (response.hasOwnProperty("viewers_yday")) {
      //console.log(response.viewers_yday);
      yday_data = response.viewers_yday.series;
    }
  };

  ws.onclose = function() {
    setTimeout(function() {
      connect_socket();
    }, base.reconnect_socket_timer);
  };

  return ws;
};
