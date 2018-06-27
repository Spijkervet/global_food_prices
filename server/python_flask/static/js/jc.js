// d3.csv({"WFPVAM_FoodPrices_version4_Retail.csv"}).then(function(experiments) {
//
// }


var dimensions = {};
var ndx = crossfilter();

var dataset = 0;
var region_ndx = crossfilter();
var country_ndx = crossfilter();
var product_ndx = crossfilter();

function getFilteredDimension(dimension) {
  var a = Array();
  for (var i in dimension) {
    if (dimension[i]) {
      a.push(i);
    }
  }
  return a;
}

function filterDimension(dimension, filter) {
  for (var i in dimension) {
    if (filter.indexOf(i) > -1) {
      dimension[i] = true;
    }
    else {
      dimension[i] = false;
    }
  }
  return dimension;
}

function createSelectMenu(id, array) {
  $("#" + id).html('');
  $("#" + id).append('<option value=""></option>');
  var d = {}
  for (var i = 0; i < array.length; i++) {
    d[array[i]] = false;
    $("#" + id).append('<option value="' + array[i] + '">' + array[i] + '</option>');
  }
  return d;
}

var selected_regions = '';
var selected_countries = '';
var selected_products = '';

var selected_years = new Set();
var year_buttons = {};

var year_array = Array();


getYears();


$("#resetButton").on('click', function() {
  country_ndx.remove();
  product_ndx.remove();
  dimensions = {};
  deSelectAllYears();
  setMapColor(defaultMapColor);

  resetZoom();

  dc.renderAll();
});


function numberFormat(number, decimals=2) {
  return "$" + number.toFixed(decimals);
}

function create_url(endpoint) {


  var url = endpoint + "&dataset=" + dataset;

  for (var i in selected_regions) {
    if (selected_regions[i]) {
      url += "&region=" + i;
    }
  }

  for (var i in selected_countries) {
    if (selected_countries[i]) {
      url += "&country=" + i;
    }
  }

  for (var i in selected_products) {
    if (selected_products[i]) {
      url += "&product=" + i;
    }
  }

  for (var it = selected_years.values(), val=null; val=it.next().value; ) {
    url += "&year=" + val;
  }
  return url;
}



function deSelectAllYears() {

  for (var i = 0; i < year_array.length; i++) {
    selected_years.delete(year_array[i]);
    year_buttons[year_array[i]].removeClass('active');
  }
}

function getSelectedYears() {
  var years = Array();
  for (var it = selected_years.values(), val=null; val=it.next().value; ) {
    years.push(val);
  }
  return years;
}

function selectAllYears() {

  for (var i = 0; i < year_array.length; i++) {
    selected_years.add(year_array[i]);
    year_buttons[year_array[i]].addClass('active');
  }

  get_country_data();
}

function selectYear() {
  var year = $(this).html();
  // dimensions.yearDimension.filter(year);

  $(this).toggleClass('active');

  if ($(this).hasClass('active')) {
    selected_years.add(year);
  }
  else {
    selected_years.delete(year);
  }

  get_country_data();
}

function getYears() {

  $.getJSON(create_url("/years?"), function(data) {

    country_ndx.add(data);

    dimensions.yearDimension = country_ndx.dimension(function (d) {
      return d.year;
    });

    var year_el = $("#years");
    year_el.html('');

    for (var i = 0; i < data.length; i++) {
      var year = data[i].year;
      var el = $('<button type="button" class="year-btn" disabled>' + year + '</button>');
      el.click(selectYear);

      year_buttons[year] = el;
      year_el.append(el);
    }

    var el = $('<button type="button" class="year-btn">' + 'All' + '</button>');
    el.click(selectAllYears);
    year_buttons['all'] = el;
    year_el.append(el);

    var el = $('<button type="button" class="year-btn">' + 'None' + '</button>');
    el.click(deSelectAllYears);
    year_buttons['none'] = el;
    year_el.append(el);
    year_el.fadeIn();
  });

}

var country_products = {};

$.getJSON("/all_regions", function(data) {
  selected_regions = createSelectMenu('region_select', data);
});

getAllCountries();
function getAllCountries() {
  $.getJSON("/all_countries", function(data) {
    selected_countries = createSelectMenu('country_select', data);
  });
}


$("#dataset_select").change(function() {
  dataset = $(this).val()[0];
  select_countries();
});

$("#region_select").change(function(e) {

  var regions = $(this).val();
  filterDimension(selected_regions, regions);
  select_products();

  setMapColor(defaultMapColor);

  var url = create_url("/all_countries?");
  $.getJSON(url, function(data) {

    if (data) {
      selected_countries = createSelectMenu('country_select', data);
    }
    else {
      getAllCountries();
    }

    select_countries();
  });

  // getRefugees(countries);
})

$("#country_select").change(function(e) {

  var countries = $(this).val();
  filterDimension(selected_countries, countries);

  setMapColor(defaultMapColor);
  select_products();
  select_countries(true);
})

$("#product_select").change(function() {
  var products = $(this).val();
  filterDimension(selected_products, products);
  select_countries();
})



function getRefugeeDestinations() {
  var url = create_url("refugees_destinations?");
  $.getJSON(url, function (data) {

    var destinations = JSON.parse(data['destinations']);


    console.log(destinations, url);

    var frequency = Array();
    var lat_lon = Array();
    clearArcs();
    for (var d in destinations) {
      frequency.push([destinations[d][0], destinations[d][1]]);
      drawArc(destinations[d][1], destinations[d][2], destinations[d][3], destinations[d][4], destinations[d][5]);
    }


    Highcharts.chart('refugeesBarChart', {
      chart: {
        type: 'column'
      },
      title: {
        text: 'Refugees by Destination'
      },
      subtitle: {
        text: '...'
      },
      xAxis: {
        type: 'category'
      },
      yAxis: {
        min: 0,
        title: {
          text: 'Population (millions)',
          align: 'high'
        },
        labels: {
          overflow: 'justify'
        }
      },
      tooltip: {
        valueSuffix: ' millions'
      },
      legend: {
        enabled: false
      },
      plotOptions: {
        series: {
          borderWidth: 0,
          dataLabels: {
            enabled: true,
            // format: '{point.y:.1f}'
          }
        }
      },
      credits: {
        enabled: false
      },
      series: [{
        name: "Test",
        "colorByPoint": true,
        data: frequency

      }]
    });
  });
}

function getRefugees() {

  var s_years = getSelectedYears();
  if (!s_years.length) {
    $("#refugeesCountry").html("1990 - 2017");
  }
  else {
    var html = '';
    for (var i = s_years.length - 1; i >= 0; i--) {
      html += s_years[i] + ', ';
    }
    $("#refugeesCountry").html(html);
  }

  getRefugeeDestinations();

  var seriesOptions = [],
  seriesCounter = 0,
  totalRefugees = 0;

  var countries = getFilteredDimension(selected_countries);
  $.each(countries, function (i, name) {

    var url = create_url("refugees?country=" + name);
    $.getJSON(url, function (data) {

      console.log("REFUGEES", url);

      var timeData = JSON.parse(data['time']);
      totalRefugees += data.total;
      seriesOptions[i] = {
        name: name,
        data: timeData,
        point: {
          events: {
            click: function () {
              console.log(this);
            }
          }
        }
      }

      seriesCounter += 1;

      if (seriesCounter === countries.length) {
        Highcharts.setOptions(Highcharts.theme);
        var chart = Highcharts.chart('refugeesChart', {
          chart: {
            events: {
              selection: function (event) {
                attachZoomChart(event);

              }
            },
            zoomType: 'x'
          },
          title: {
            text: 'Frequency of Refugees'
          },

          subtitle: {
            text: 'Refugees'
          },

          xAxis: {
            type: 'datetime',
            labels: {
              format: '{value:%Y-%b-%e}'
            },
          },
          // rangeSelector: {
          //   floating: true,
          //   y: -65,
          //   verticalAlign: 'bottom'
          // },

          // navigator: {
          //   margin: 60
          // },
          series: seriesOptions
        });

        if (chart) {
          lineCharts.push(chart);
        }
        var counter = new CountUp('totalRefugees', 0, Number(totalRefugees), 0, 1.0);
        counter.start();
      }
    });
  });





}

function select_products() {

  var url = create_url("/country_products?");

  $.getJSON(url, function(data) {
    selected_products = createSelectMenu('product_select', data);
  });
}

function select_countries() {

  // var countries = country_select.filters();

  for (c in selected_countries) {

    var color = selected_countries[c] ? selectedMapColor : highlightMapColor;
    setMapColor(color, c);
  }
  get_country_data();
}

var lineCharts = Array();

function resetZoom() {
  for (var i = 0; i < lineCharts.length; i++) {
    if (lineCharts[i].xAxis) {
      lineCharts[i].xAxis[0].setExtremes(null,null);
    }
  }
}

function attachZoomChart(event) {
  if (event.resetSelection) {
    resetZoom();
  }
  if (event.xAxis) {
    var min = event.xAxis[0].min;
    var max = event.xAxis[0].max;

    for (var i = 0; i < lineCharts.length; i++) {
      if (lineCharts[i].xAxis) {
        lineCharts[i].xAxis[0].update({min: min, max: max});
      }
    }
  }
}

function plotPrices(div, type, data, title='') {


  var product_data = data['data'],
  seriesOptions = [];

  for (p in selected_products) {
    var timeData = [];
    for (var j = 0; j < product_data.length; j++) {
      if (p == product_data[j].cm_name) {
        timeData.push([product_data[j].datetime, product_data[j][type]]);
      }
    }

    seriesOptions.push({
      name: p,
      data: timeData,
      point: {
        events: {
          click: function () {
            console.log(this);
          }
        }
      }
    });
  }

  var chart = Highcharts.chart(div, {

    chart: {
      events: {
        selection: function (event) {

          attachZoomChart(event);

        }
      },
      zoomType: 'x'
    },

    title: {
      text: title
    },

    subtitle: {
      text: '...'
    },

    xAxis: {
      type: 'datetime',
      labels: {
        format: '{value:%Y-%b-%e}'
      },
    },
    // rangeSelector: {
    //   floating: true,
    //   y: -65,
    //   verticalAlign: 'bottom'
    // },
    //
    // navigator: {
    //   margin: 60,
    //   enabled: true
    // },
    series: seriesOptions
  });

  if (chart) {
    lineCharts.push(chart);
  }
}

function createTSNEPlot(data) {

  var tsne_data = JSON.parse(data['data']);
  var tsne_labels = data['labels'];

  Array.prototype.insert = function ( index, item ) {
    this.splice( index, 0, item );
  };


  var formatted_series = Array();
  for (var i = 0; i < tsne_labels.length; i++) {

    if (typeof(formatted_series[tsne_labels[i]]) == 'undefined') {
      formatted_series[tsne_labels[i]] = {}
      formatted_series[tsne_labels[i]]['data'] = []
    }

    formatted_series[tsne_labels[i]]['data'].push([tsne_data[i][0], tsne_data[i][1]]);
    formatted_series[tsne_labels[i]]['name'] = tsne_labels[i].toString();

    // formatted_series.insert(tsne_labels[i], tsne_data[i]);
  }


  Highcharts.chart('tsne_plot', {
    chart: {
      type: 'scatter',
      zoomType: 'xy'
    },
    title: {
      text: 'TSNE'
    },
    subtitle: {
      text: '...'
    },
    xAxis: {
      visible: false
    },
    yAxis: {
      visible: false
    },
    legend: {
      title: {
        text: 'Cluster ID',
      },
      layout: 'vertical',
      align: 'left',
      verticalAlign: 'top',
      floating: true,
      backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
      borderWidth: 1
    },
    plotOptions: {
      scatter: {
        marker: {
          radius: 5,
          states: {
            hover: {
              enabled: true,
              lineColor: 'rgb(100,100,100)'
            }
          }
        },
        states: {
          hover: {
            marker: {
              enabled: false
            }
          }
        },
        tooltip: {
          headerFormat: '<b>{series.name}</b><br>',
          pointFormat: '{point.x}, {point.y}'
        }
      }
    },
    series: formatted_series
    // , {
    //   name: 'TEST',
    //   color: '',
    //   data: []
    // }

  });

}


function clusterData() {

  var url = create_url("/cluster?");

  $.getJSON(url, function (data) {

    var kmeans = data['kmeans'];
    var table = '<thead><tr><th>ID</th><th>Cluster</th></tr></thead>';
    table += '<tbody>';

    for (var i = 0; i < kmeans.length; i++) {
      table += '<tr>';

      table += '<td>' + Number(kmeans[i]['label']) + '</td>';

      table += '<td>';
      for (var j = 0; j < kmeans[i]['cluster_group'].length; j++) {
        table += kmeans[i]['cluster_group'][j] + ', ';
      }
      table += '</td>';
      table += '</tr>';
    }

    table += '</tbody>';
    $("#cluster_table").html(table);

    $("#cluster_table").dataTable();

    var tsne = data['tsne'];
    createTSNEPlot(tsne);
  });
}

function get_country_data() {


  getRefugees();
  $('.year-btn').removeClass('accessible');

  var url = create_url("/country?");

  d3.json(url, function(data) {


    clusterData();

    plotPrices('gradient_chart', 'Gradient', data, title='Gradient');
    plotPrices('prices_chart', 'mp_price', data, title='Prices');

    if (data != null) {
      for (var i = 0; i < data['years'].length; i++) {
        var year = data['years'][i];
        year_buttons[year].addClass('accessible');
        year_buttons[year].prop('disabled', false);
        year_array.push(year);
      }
    }
    dc.renderAll();
  });
}
