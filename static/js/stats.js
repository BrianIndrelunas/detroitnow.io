
var tableSource = $("#stats-table-template").html();
var tableRowSource = $("#stats-row-template").html();
var tableTemplate = handlebars.compile(tableSource);
var tableRowTemplate = handlebars.compile(tableRowSource);

// Set up WebSocket
var ws = new WebSocket("ws://" + base.socket_domain + "/stats-socket")
var numUpdates = 0;

// jQuery selectors
var $pieChart = "#stat-pie-chart";
var $chartInfo = ".chart-info";

// Color pallate for the pie chart
var colorPalette = [
  "#76b729",
  "#3d97df",
  "#cac392",
  "#513629"
];

var chart;

function getChartHeight() {
  return parseInt($(window).height() * .9);
}

function getChartWidth() {
  return parseInt($(window).width() * .6);
}

// Message handler
ws.onmessage = function(e) {

  try {
    var response = $.parseJSON(e.data);
  } catch(e) {
    return;
  }

  if (response.hasOwnProperty("stats")) {
    // Get the stats from the response string
    var statValues = $.parseJSON(response.stats);
    console.log(statValues);
    // Fade out loading screen
    $(".loading").addClass("loading-done");


    // IE < 10 doesn't support transitionend :(
    setTimeout(function(){
      $(".loading").hide();
    },500);

    // Populate the table
    populateTable(statValues);
    // Draw the chart
    drawStatChart(statValues);
  }

  numUpdates += 1;
};

ws.onclose = function() {
  setTimeout(function() {
    connect_socket();
  }, reconnect_socket_timer);
};

// Populate the table like so:
//
//       | social | direct | ...
//-----------------------------  ...
// site1.com |   12   |  45    ...
// ...      ...    ...
function populateTable(statValues) {
  var tableHeaders = [];
  var tableRows = {};
  for (var stat in statValues) {
    tableHeaders.push(stat);
    var hitCounts = statValues[stat];
    for (var site in hitCounts) {
      if (site in tableRows) {
        tableRows[site].push(hitCounts[site]);
      } else {
        tableRows[site] = [hitCounts[site]];
      }
    }
  }

  // Sort the table rows
  var sortedRows = [];
  for (var row in tableRows) {
    sortedRows.push([row, tableRows[row]]);
  }

  sortedRows.sort(function(a, b) {
    var aName = a[0];
    var bName = b[0];
    var aCounts = a[1];
    var bCounts = b[1];

    // Always make sure "total" is at the bottom
    if (aName.toLowerCase() == "total") return 1;
    if (bName.toLowerCase() == "total") return -1;

    // Get totals
    var aTotal = 0;
    var bTotal = 0;
    for (var i = 0; i < aCounts.length; i++) {
      aTotal += aCounts[i];
    }

    for (var i = 0; i < bCounts.length; i++) {
      bTotal += bCounts[i];
    }

    if (aTotal > bTotal) {
      return -1; // a goes first
    }

    if (aTotal < bTotal) {
      return 1; // b goes first
    }

    return 0;
  });

  // Create the table body HTML
  var tableBodySource = "";
  for (var i = 0; i < sortedRows.length; i++) {
    var row = sortedRows[i];
    tableBodySource += "\n";
    tableBodySource += tableRowTemplate({
      "site": row[0],
      "stats": row[1]
    });
  }

  // Create the rest of the table
  var tableSource = tableTemplate({
    "headers": tableHeaders,
    "tbody": tableBodySource
  });
  // Append HTML
  $($chartInfo).html(tableSource);
}

// Draw the pie chart
function drawStatChart(statValues) {
  // Compile data for c3 pie chart
  // http://c3js.org/samples/chart_pie.html
  var columns = [];
  var colors = {};
  var colorIndex = 0;
  for (var stat in statValues) {
    // Add the stat
    columns.push([
      stat,
      statValues[stat].total
    ]);

    // Add the color
    colors[stat] = (colorIndex < colorPalette.length) ? colorPalette[colorIndex] : '#' + Math.floor(Math.random() * 16777215).toString(16);
    colorIndex++;
  }

  columns.sort(function(a, b) {
    if (a[1] > b[1]) {
      return -1; // 'a' comes first
    }

    if (a[1] < b[1]) {
      return 1; // 'b' comes first
    }

    return 0;
  });

  if (!chart) {
    // Create the chart if it doesn't yet exist
    chart = c3.generate({
      "data": {
        "columns": columns,
        "type": "pie",
        "size": {
          "width": getChartWidth(),
          "height": getChartHeight(),
        },
        "colors": colors,
      },
      "tooltip": {
        "format": {
          "value": function (value, ratio, id) {
            var format = d3.format(',');
            return format(value);
          }
        }
      },
      "onresized": function() {
        var size = {
          "height": getChartHeight(),
          "width": getChartWidth()
        }
        chart.resize(size);
      }
    });
  } else {
    // If the chart already exists, load up the new data
    chart.load({ "columns": columns });
  }
}