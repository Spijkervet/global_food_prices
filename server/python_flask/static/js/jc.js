var dimensions = {};

var dataset = 0;

var correlationChart;

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
  // $("#" + id).append('<option value=""></option>');
  var d = {}
  for (var i = 0; i < array.length; i++) {
    d[array[i]] = false;

    var data = {
      id: array[i],
      text: array[i]
    };

    var newOption = new Option(data.text, data.id, false, false);
    $('#' + id).append(newOption);


    // $("#" + id).append('<option value="' + array[i] + '">' + array[i] + '</option>');
  }
  return d;
}

var selected_regions = '';
var selected_countries = '';
var selected_products = '';

var cluster_groups = 5;


var selected_years = new Set();
var year_buttons = {};

var year_array = Array();


$("#resetButton").on('click', function() {
  location.reload();
  //
  // deSelectAllYears();
  // setMapColor(defaultMapColor);
  //
  // resetZoom();
});


function numberFormat(number, decimals=2) {
  return "$" + number.toFixed(decimals);
}

$("#clusterGroups").change(function() {

  cluster_groups = $(this).val();
});

function create_url(endpoint) {

  var url = endpoint + "&dataset=" + dataset;
  url += "&cluster_group=" + cluster_groups;

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
  clearArcs();

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
    for (var d in destinations) {
      frequency.push([destinations[d][0], destinations[d][1]]);
      drawArc(destinations[d][1], destinations[d][2], destinations[d][3], destinations[d][4], destinations[d][5]);
    }
    totalArcs++;


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

function getPanelText() {
  var s_years = getSelectedYears(),
  countries = getFilteredDimension(selected_countries),
  html = '';

  for (var i = 0; i < countries.length; i++) {
    html += countries[i] + ', ';
  }

  html += ' between ';

  if (!s_years.length) {
    html += '1990 - 2017';
  }
  else {
    html +=  s_years[s_years.length-1] + ' - ' + s_years[0];
  }
  return html;
}


function getRefugees() {

  var html = getPanelText();

  $("#refugeesCountry").html(html);
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
  var countryTitle = '';
  for (c in selected_countries) {

    var color = selected_countries[c] ? selectedMapColor : highlightMapColor;

    if (selected_countries[c]) {
      countryTitle += c + ' | ';
    }

    setMapColor(color, c);
  }

  // for (var i = 0; i < priceCharts.length; i++) {
  //   priceCharts[i].setTitle({text: "Prices in " + countryTitle});
  // }

  get_country_data();
}

var lineCharts = Array();
var priceCharts = Array();

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


function plotCorrelation(div, data, title='') {

  console.log("CORRElATION", data);

  var x_categories = Array(),
  y_categories = Array(),
  series_data = Array(),
  x = 0;

  for (var d in data) {
    y = 0;
    for (var i in data[d]) {
      series_data.push([x, y, data[d][i]]);
      y += 1;
    }
    x_categories.push(d);
    y_categories.push(d);
    x += 1;
  }


  correlationChart = Highcharts.chart(div, {

    chart: {
      type: 'heatmap',
      marginTop: 40,
      marginBottom: 80,
      plotBorderWidth: 1,
      height: '500px'
    },


    title: {
      text: title
    },

    xAxis: {
      categories: x_categories,
      scrollbar: {
        enabled: true
      }
    },

    yAxis: {
      categories: y_categories,
      title: null,
      scrollbar: {
        enabled: true
      }
    },

    colorAxis: {
      min: 0,
      minColor: '#FFFFFF',
      maxColor: Highcharts.getOptions().colors[0]
    },

    legend: {
      align: 'right',
      layout: 'vertical',
      margin: 0,
      verticalAlign: 'top',
      y: 25,
      symbolHeight: 280
    },

    tooltip: {
      formatter: function () {
        return '<b>' + this.series.xAxis.categories[this.point.x] + '</b> sold <br><b>' +
        this.point.value + '</b> items on <br><b>' + this.series.yAxis.categories[this.point.y] + '</b>';
      }
    },

    series: [{
      name: 'Sales per employee',
      borderWidth: 1,
      data: series_data,
      dataLabels: {
        enabled: false,
        color: '#000000',
        style: {
          fontSize: '9px'
        }
      },
    }]

  });
}

$("#kmeansbutton").on('click', function() {
  clusterData();
});

function plotCurrency(div, type, data, title='') {
  var seriesOptions = [];

  var selection = selected_regions,
  selector = 'sub-region';

  if (getFilteredDimension(selected_countries).length > 0) {
    selection = selected_countries;
    selector = 'adm0_name';
  }

  console.log(data);
  for (p in selection) {

    var timeData = [];
    for (var j = 0; j < data.length; j++) {

      if (p == data[j][selector]) {
        timeData.push([data[j].datetime, data[j][type]]);
      }
    }
    if (timeData.length) {
      seriesOptions.push({
        name: p,
        data: timeData,
        point: {
          events: {
            click: function () {
              console.log(this);
            }
          }
        },
        marker: {
          enabled: false
        }
      });
    }
  }

  var chart = Highcharts.chart(div, {

    chart: {
      height: '800px',
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
      title: {
        text: 'Date'
      }
    },
    yAxis: {
      title: {
        text: 'USD'
      }
    },
    series: seriesOptions
  });

  if (chart) {
    lineCharts.push(chart);
  }
}

function plotPrices(div, type, data, title='') {
  var product_data = data['data'],
  seriesOptions = [];

  var selector = 'sub-region';

  if (getFilteredDimension(selected_countries).length > 0) {
    selector = 'adm0_name';
  }

  var placeHolder = {};
  for (var i = 0; i < product_data.length; i++) {
    var key = product_data[i].cm_name + ' ' + product_data[i][selector];

    if (!(key in placeHolder)) {
      placeHolder[key] = Array();
    }
    else {
      placeHolder[key].push([product_data[i].datetime, product_data[i][type]]);
    }
  }

  for (var p in placeHolder) {
    seriesOptions.push({
      name: p,
      data: placeHolder[p],
      point: {
        events: {
          click: function () {
            console.log(this);
          }
        }
      },
      marker: {
        enabled: false
      }
    });
  }



  var chart = Highcharts.chart(div, {

    chart: {
      height: '600px',
      events: {
        selection: function (event) {
          attachZoomChart(event);
        }
      },
      zoomType: 'x',
    },
    legend: {
      enabled: true,
      // layout: 'vertical',
      maxHeight: 100
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
      title: {
        text: 'Date'
      }
    },
    yAxis: {
      title: {
        text: 'USD'
      }
    },
    series: seriesOptions
  });

  if (chart) {
    lineCharts.push(chart);
    priceCharts.push(chart);
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
  console.log('CLUSTER', url);

  $.getJSON(url, function (data) {

    console.log('CLUSTER', data, url);

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

function getMortality() {
  var url = create_url('/mortality?');
  $.getJSON(url, function(data) {

    var html = getPanelText();
    $('#mortalityCountry').html(html);
    var data = JSON.parse(data);
    plotMortality('mortality_chart', 'Mortality Rate', data, title='Mortality');
  });
}


function plotMortality(div, type, data, title='') {


  var seriesOptions = [],
  avgMortality = 0,
  avg_i = 0;


  var selector = 'adm0_name';

  if (getFilteredDimension(selected_countries).length > 0) {
    selector = 'adm0_name';
  }

  var placeHolder = {};
  for (var i = 0; i < data.length; i++) {
    var key = data[i][selector];

    if (!(key in placeHolder)) {
      placeHolder[key] = Array();
    }
    else {
      placeHolder[key].push([data[i].datetime, data[i][type]]);
      avgMortality += data[i][type];
      avg_i += 1;
    }
  }

  for (var p in placeHolder) {
    seriesOptions.push({
      name: p,
      data: placeHolder[p],
      point: {
        events: {
          click: function () {
            console.log(this);
          }
        }
      },
      marker: {
        enabled: false
      }
    });
  }




  // for (p in selected_countries) {
  //   var timeData = [],
  //   name = p;
  //   for (var j = 0; j < data.length; j++) {
  //     if (p == data[j].adm0_name || data[j]['sub-region']) {
  //
  //       // setMortality(p, data[j][type]);
  //       var d = [data[j].datetime, data[j][type]];
  //       timeData.push(d);
  //       avgMortality += data[j][type];
  //       avg_i += 1;
  //     }
  //   }
  //
  //   if (timeData.length) {
  //     seriesOptions.push({
  //       name: name,
  //       data: timeData,
  //       point: {
  //         events: {
  //           click: function () {
  //             console.log(this);
  //           }
  //         }
  //       }
  //     });
  //   }
  // }

  var counter = new CountUp('totalMortality', 0, Number(avgMortality / avg_i / 10), 0, 1.0);
  counter.start();

  var chart = Highcharts.chart(div, {

    chart: {
      height: '500px',
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
    series: seriesOptions
  });

  if (chart) {
    lineCharts.push(chart);
  }
}

function getCorrelation() {

  console.log("CORRELATION");

  var url = create_url('/correlation?');
  console.log(url);
  $.getJSON(url, function(data) {


    var data = JSON.parse(data);
    plotCorrelation('correlation_chart', data, title='Correlation');
  });
}

function getCurrency() {

  var url = create_url('/currency_data?');
  console.log(url);
  $.getJSON(url, function(data) {

    data = JSON.parse(data);
    plotCurrency('currency_chart', 'Currency Rate', data, title='Currency Rate');
    plotCurrency('gdp_chart', 'GDP', data, title='GDP');
  });
}

function get_country_data() {


  getRefugees();
  getCorrelation();
  getMortality();

  getCurrency();

  $('.year-btn').removeClass('accessible');

  var url = create_url("/country?");

  d3.json(url, function(data) {

    console.log(url, data);

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
  });
}


$(document).ready(function() {
  $("#dataset_select").select2({ width: 'resolve'});
  $("#region_select").select2({ width: 'resolve', placeholder: "Region" });
  $("#country_select").select2({ width: 'resolve', placeholder: "Country" });
  $("#product_select").select2({ width: 'resolve', placeholder: "Product" });

  getYears();

});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();

    document.querySelector(this.getAttribute('href')).scrollIntoView({
      behavior: 'smooth'
    });
  });
});
