// d3.csv({"WFPVAM_FoodPrices_version4_Retail.csv"}).then(function(experiments) {
//
// }


var dimensions = {};
var ndx = crossfilter();

var dataset = 0;
var country_ndx = crossfilter();
var product_ndx = crossfilter();
var selected_years = new Set();
var year_buttons = {};

var year_array = Array();
var country_select = dc.selectMenu('#country_select');
var product_select = dc.selectMenu('#product_select');
// var city_select = dc.selectMenu('#city_select');
// var select1 = dc.selectMenu('#select1');


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


function cluster_countries(countries) {
  console.log(countries);

  var url = create_url("/cluster?", countries);

  d3.json(url, function(data) {

    console.log("GOT DATA", data);

    var clusterTable = dc.dataTable("#cluster_table");

    var ndx = crossfilter(data);
    let dimensionCategory = ndx.dimension(item => item.cluster_group);

    // for (var i = 0; i < country_data.length; i++) {
    //   setMapColor(selectedMapColor, country_data[i].Iadm0_name);
    // }

    clusterTable.width(768)
    .height(480)
    .dimension(dimensionCategory)
    .group(function(d) { return ''; })
    .columns([
      {
        label: "Cluster",
        format: function (d) {
          return d.cluster_group;
        }
      }
    ]);

    clusterTable.render();
  });
}

function numberFormat(number, decimals=2) {
  return "$" + number.toFixed(decimals);
}

function create_url(endpoint, countries = [], products=[]) {

  var url = endpoint + "&dataset=" + dataset;
  for (var i = 0; i < countries.length; i++) {
    url += "&country=" + countries[i];
  }

  for (var i = 0; i < products.length; i++) {
    url += "&product=" + products[i];
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

  var countries = country_select.filters();
  get_country_data(countries);
  // cluster_countries(countries);
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

  var countries = country_select.filters();
  var products = product_select.filters();
  get_country_data(countries, products);

  // cluster_countries(countries);
}

function getYears() {

  $.getJSON(create_url("/years?"), function(data) {

    console.log("TEST", data);

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
$.getJSON("/all_countries", function(data) {

  country_ndx.add(data);
  dimensions.countryDimension = country_ndx.dimension(function (d) {
    return d.country;
  });

  country_select.dimension(dimensions.countryDimension)
  .group(dimensions.countryDimension.group())
  .multiple(true)
  .numberVisible(3)
  .controlsUseVisibility(true);

  country_select.render();
});

$("#dataset_select").change(function() {
  dataset = $(this).val()[0];
  var countries = country_select.filters();
  var products = product_select.filters();
  select_countries(countries, products);
});

$("#product_select").change(function() {
  var countries = country_select.filters();
  var products = product_select.filters();
  select_countries(countries, products);
})

$("#country_select").change(function(e) {
  var countries = country_select.filters();

  setMapColor(defaultMapColor);

  select_products(countries);

  getRefugees(countries);

  // if (selected_years.size) {
  //   cluster_countries(countries);
  // }
})


function getRefugeeDestinations(countries) {
  var url = create_url("refugees_destinations?", countries);
  $.getJSON(url, function (data) {

    var destinations = JSON.parse(data['destinations']);
    // categories = [],
    // values = [];
    // for (var i = 0; i < destinations.length; i++) {
    //   categories.push(destinations[i][0]);
    //   values.push(destinations[i][1]);
    // }

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
        data: destinations

      }]
    });

    console.log(data);
  });
}

function getRefugees(countries) {

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

  getRefugeeDestinations(countries);

  var seriesOptions = [],
  seriesCounter = 0,
  totalRefugees = 0;

  $.each(countries, function (i, name) {

    var url = create_url("refugees?country=" + name);
    $.getJSON(url, function (data) {

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
          rangeSelector: {
            floating: true,
            y: -65,
            verticalAlign: 'bottom'
          },

          navigator: {
            margin: 60
          },
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

function select_products(countries) {

  var url = create_url("/country_products?", countries);

  $.getJSON(url, function(data) {

    product_ndx.remove();
    product_ndx.add(data);
    dimensions.productDimension = product_ndx.dimension(function (d) {
      return d.product;
    });

    product_select.dimension(dimensions.productDimension)
    .group(dimensions.productDimension.group())
    .multiple(true)
    .numberVisible(5)
    .controlsUseVisibility(true);

    product_select.render();
    console.log("PRODUCTS", data);
  });
}

function select_countries(countries, products='') {

  for (var i = 0; i < countries.length; i++) {
    setMapColor(highlightMapColor, countries[i]);
  }
  get_country_data(countries, products);
}


$("#select1").change(function() {
  var country = $(this).find(':selected').val();

  var countries = Datamap.prototype.worldTopo.objects.world.geometries;
  for (var i = 0, j = countries.length; i < j; i++) {
    if (country == countries[i].properties.name) {
      try {
        var obj = {};
        obj[countries[i].id] = highlightMapColor;
        map.updateChoropleth(obj);
      }
      catch (e) {}
      break;
    }
  }
})

var lineCharts = Array();

function resetZoom() {
  for (var i = 0; i < lineCharts.length; i++) {
    if (lineCharts[i].xAxis) {
      lineCharts[i].xAxis[0].setExtremes(null,null);
      console.log("RESET NULL)");
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

function plotPrices(div, type, products, data, title='') {


  var product_data = data['data'],
  seriesOptions = [];

  var timeData = data['time'];
  totalRefugees += data.total;

  for (var i = 0; i < products.length; i++) {
    var timeData = [];
    for (var j = 0; j < product_data.length; j++) {
      if (products[i] == product_data[j].cm_name) {
        timeData.push([product_data[j].datetime, product_data[j][type]]);
      }
    }

    console.log(products[i], timeData);
    seriesOptions[i] = {
      name: products[i],
      data: timeData,
      point: {
        events: {
          click: function () {
            console.log(this);
          }
        }
      }
    }
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
    rangeSelector: {
      floating: true,
      y: -65,
      verticalAlign: 'bottom'
    },

    navigator: {
      margin: 60,
      enabled: true
    },
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


  console.log(data, formatted_series);

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


function clusterData(countries, products) {

  var url = create_url("/cluster?", countries, products);

  console.log("K", url);

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
    console.log(table);

    $("#cluster_table").dataTable();

    var tsne = data['tsne'];
    createTSNEPlot(tsne);
  });
}

function get_country_data(countries, products) {

  clusterData(countries, products);
  getRefugees(countries);
  $('.year-btn').removeClass('accessible');

  var url = create_url("/country?", countries, products);

  d3.json(url, function(data) {

    console.log(data);

    if (selected_years.size) {

      plotPrices('gradient_chart', 'Gradient', products, data, title='Gradient');
      plotPrices('prices_chart', 'mp_price', products, data, title='Prices');

      // console.log("GETTING COUNTRY DATA", url, data);
      //
      // var chart = dc.dataTable("#test");
      // var lineChart = dc.compositeChart("#test_2");
      // var gradientChart = dc.compositeChart("#gradient_chart");
      // var barChart = dc.barChart("#test_3");
      //
      // var country_data = data['data'];
      //
      // var unique_products = [];
      // country_data.filter(function(item){
      //   var i = unique_products.indexOf(item.cm_name);
      //   if(i <= -1) {
      //     unique_products.push(item.cm_name);
      //   }
      //   return null;
      // });
      //
      // var ndx = crossfilter(country_data);
      // let dimensionCategory = ndx.dimension(item => item.adm0_name);
      //
      // for (var i = 0; i < country_data.length; i++) {
      //   setMapColor(selectedMapColor, country_data[i].adm0_name);
      // }
      //
      // chart.width(768)
      // .height(480)
      // .dimension(dimensionCategory)
      // .group(function(d) { return ''; })
      // .columns([
      //   {
      //     label: "Country",
      //     format: function (d) {
      //       return d.adm0_name;
      //     }
      //   },
      //   {
      //     label: "Product",
      //     format: function (d) {
      //       return d.cm_name;
      //     }
      //   },
      //   {
      //     label: "USD",
      //     format: function (d) {
      //       return numberFormat(d.mp_price);
      //     }
      //   },
      //   {
      //     label: "Date",
      //     format: function (d) {
      //       return new Date(d.datetime).toISOString().split('T')[0];
      //     }
      //   },
      // ]);
      //
      // let timeCategory = ndx.dimension(item => item.datetime);
      //
      // var productGroups = new Set;
      // for (var i = 0; i < country_data.length; i++) {
      //   productGroups.add(country_data[i]['cm_name']);
      // }
      //
      // var lines = []
      // productGroups = Array.from(productGroups);
      //
      // var productGroup = timeCategory.group().reduceSum(dc.pluck('cm_name'));
      //
      //
      // var names = country_data.map(function(row) { return row.cm_name; });
      // names = names.filter(function(item, pos, self) {
      //   return self.indexOf(item) == pos;
      // })
      //
      //
      // var g_colors = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6", "#dd4477", "#66aa00", "#b82e2e", "#316395", "#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707", "#651067", "#329262", "#5574a6", "#3b3eac"];
      // var positions = timeCategory.group().reduce(
      //   function(p, v) { // add
      //     p[v["cm_name"]] = (p[v["mp_price"]] || 0) + v["mp_price"];
      //     return p;
      //   },
      //   function(p, v) { // remove
      //     p[v["cm_name"]] -= v["mp_price"];
      //     return p;
      //   },
      //   function() { // initial
      //     return {};
      //   });
      //
      //   var gradientPositions = timeCategory.group().reduce(
      //     function(p, v) { // add
      //       p[v["cm_name"]] = (p[v["Gradient"]] || 0) + v["Gradient"];
      //       return p;
      //     },
      //     function(p, v) { // remove
      //       p[v["cm_name"]] -= v["Gradient"];
      //       return p;
      //     },
      //     function() { // initial
      //       return {};
      //     });
      //
      //     lineChart.height(400)
      //     .legend(dc.legend().x(60).y(10).itemHeight(13).gap(2))
      //     .transitionDuration(500)
      //     .mouseZoomable(true)
      //     .margins({top: 10, right: 10, bottom: 20, left: 40})
      //     // .dimension(timeCategory)
      //     // .group(productGroup)
      //     .compose(
      //
      //       names.map(function(name, idx) {
      //         return dc.lineChart(lineChart)
      //         // .renderArea(true)
      //         .mouseZoomable(true)
      //         .dimension(timeCategory)
      //         // .colors()
      //         .colors(function() {
      //           return g_colors[idx];
      //         })
      //         .group(positions, name)
      //         .round(d3.time.month.round)
      //         .xUnits(d3.time.months)
      //         .renderHorizontalGridLines(true)
      //         .valueAccessor(function(kv) {
      //           return kv.value[name];
      //         });
      //       })
      //     )
      //     .brushOn(true)
      //     .xAxisLabel('Date')
      //     .yAxisLabel('USD')
      //     // .elasticY(true)
      //     .x(d3.time.scale().domain(d3.extent(country_data, function(d) { return d.datetime; })))
      //     .xAxis();
      //
      //     lineChart.on('pretransition.hideshow', function(chart) {
      //       chart.selectAll('g.dc-legend .dc-legend-item')
      //       .on('click.hideshow', function(d, i) {
      //         var subchart = chart.select('g.sub._' + i);
      //         var visible = subchart.style('visibility') !== 'hidden';
      //         subchart.style('visibility', function() {
      //           return visible ? 'hidden' : 'visible';
      //         });
      //         d3.select(this).style('opacity', visible ? 0.2 : 1);
      //       });
      //     });
      //
      //     gradientChart.height(400)
      //     .legend(dc.legend().x(60).y(10).itemHeight(13).gap(2))
      //     .transitionDuration(500)
      //     .mouseZoomable(true)
      //     .margins({top: 10, right: 10, bottom: 20, left: 40})
      //     // .dimension(timeCategory)
      //     // .group(productGroup)
      //     .compose(
      //
      //       names.map(function(name, idx) {
      //         return dc.lineChart(gradientChart)
      //         // .renderArea(true)
      //         .mouseZoomable(true)
      //         .dimension(timeCategory)
      //         // .colors()
      //         .colors(function() {
      //           return g_colors[idx];
      //         })
      //         .group(gradientPositions, name)
      //         .round(d3.time.month.round)
      //         .xUnits(d3.time.months)
      //         .renderHorizontalGridLines(true)
      //         .valueAccessor(function(kv) {
      //           return kv.value[name];
      //         });
      //       })
      //     )
      //     .brushOn(true)
      //     .xAxisLabel('Date')
      //     .yAxisLabel('Gradient')
      //     // .elasticY(true)
      //     .x(d3.time.scale().domain(d3.extent(country_data, function(d) { return d.datetime; })))
      //     .xAxis();
      //
      //     gradientChart.on('pretransition.hideshow', function(chart) {
      //       chart.selectAll('g.dc-legend .dc-legend-item')
      //       .on('click.hideshow', function(d, i) {
      //         var subchart = chart.select('g.sub._' + i);
      //         var visible = subchart.style('visibility') !== 'hidden';
      //         subchart.style('visibility', function() {
      //           return visible ? 'hidden' : 'visible';
      //         });
      //         d3.select(this).style('opacity', visible ? 0.2 : 1);
      //       });
      //     });
      //
      //     var productDimension = ndx.dimension(function(d) {return d.cm_name;}),
      //     productSum = productDimension.group().reduceSum(function(d) {return d.mp_price;});
      //     barChart
      //     // .x(d3.scale.linear().domain([]))
      //     .xUnits(dc.units.ordinal)
      //     .brushOn(false)
      //     .xAxisLabel('Product')
      //     .yAxisLabel('USD')
      //     .dimension(productDimension)
      //     .barPadding(0.1)
      //     .outerPadding(0.05)
      //     .group(productSum);
    }

    if (data != null) {
      console.log(data['years'])
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


//
// function average_product(prod_id) {
//
//   var pieChart = dc.pieChart("#pieChart");
//   var chart = dc.dataTable("#test");
//
//   d3.json("/avg_prod/" + prod_id, function(data) {
//     // $.getJSON("/avg_prod/" + prod_id, function(data) {
//
//     var ndx = crossfilter(data);
//
// var countries = Datamap.prototype.worldTopo.objects.world.geometries;
// for (var i = 0; i < data.length; i++) {
//   setMapColor(highlightMapColor, data[i].country);
// }
//
//
//     dimensions.cityDimension = ndx.dimension(function (d) {
//       return d.country;
//     }),
//     cityGroup = dimensions.cityDimension.group().reduceSum(function (d) {
//       return d.average;
//     });
//
//
//     // select1.dimension(dimensions.cityDimension)
//     // .group(dimensions.cityDimension.group())
//     // .multiple(true)
//     // .numberVisible(10)
//     // .controlsUseVisibility(true);
//
//
//     pieChart.width(200)
//     .height(200)
//     .slicesCap(4)
//     .dimension(dimensions.cityDimension)
//     .group(cityGroup);
//
//     chart.width(768)
//     .height(480)
//     .dimension(dimensions.cityDimension)
//     .group(function(d) { return d.country; })
//     .columns([
//       'average',
//       'lat',
//       'lon',
//     ]);
//
//
//     // dimensions.cityDimension.filter('Afghanistan');
//
//     dc.renderAll();
//
//   });
// }
//
//
// function render_plots() {
//
//
// }
//
// render_plots();


function test_graph(url) {
  // basic SVG setup
  var margin = { top: 20, right: 100, bottom: 40, left: 100 };
  var height = 500 - margin.top - margin.bottom;
  var width = 960 - margin.left - margin.right;

  var svg = d3.select("body").append("svg")
  .attr("width",width + margin.left + margin.right)
  .attr("height",height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // setup scales - the domain is specified inside of the function called when we load the data
  var xScale = d3.time.scale().range([0, width]);
  var yScale = d3.scale.linear().range([height, 0]);
  var color = d3.scale.category10();

  // setup the axes
  var xAxis = d3.svg.axis().scale(xScale).orient("bottom");
  var yAxis = d3.svg.axis().scale(yScale).orient("left");

  // create function to parse dates into date objects
  var parseDate = d3.time.format("%Y-%m-%d").parse;
  var formatDate = d3.time.format("%Y-%m-%d");
  var bisectDate = d3.bisector(function(d) { return d.date; }).left;

  // set the line attributes
  var line = d3.svg.line()
  .interpolate("basis")
  .x(function(d) { return xScale(d.date); })
  .y(function(d) { return yScale(d.close); });

  var focus = svg.append("g").style("display","none");


  // import data and create chart
  d3.json(url, function(d) {

    console.log(d);

    return {
      date: parseDate(d.data.datetime),
      Amazon: +d.Amazon,
      Apple: +d.Apple,
      Facebook: +d.Facebook,
      Google: +d.Google,
      IBM: +d.IBM,
      Microsoft: +d.Microsoft
    };
  },
  function(error,data) {

    // sort data ascending - needed to get correct bisector results
    // data.sort(function(a,b) {
    // 	return a.date - b.date;
    // });
    //
    // // color domain
    // color.domain(d3.keys(data[0]).filter(function(key) { return key !== "date"; }));
    //
    // // create stocks array with object for each company containing all data
    // var stocks = color.domain().map(function(name) {
    // 	return {
    // 		name: name,
    // 		values: data.map(function(d){
    // 			return {date: d.date, close: d[name]};
    // 		})
    // 	};
    // });
    //
    // // add domain ranges to the x and y scales
    // xScale.domain([
    // 	d3.min(stocks, function(c) { return d3.min(c.values, function(v) { return v.date; }); }),
    // 	d3.max(stocks, function(c) { return d3.max(c.values, function(v) { return v.date; }); })
    // ]);
    // yScale.domain([
    // 	0,
    // 	// d3.min(stocks, function(c) { return d3.min(c.values, function(v) { return v.close; }); }),
    // 	d3.max(stocks, function(c) { return d3.max(c.values, function(v) { return v.close; }); })
    // ]);
    //
    // // add the x axis
    // svg.append("g")
    // 	.attr("class", "x axis")
    // 	.attr("transform", "translate(0," + height + ")")
    // 	.call(xAxis);
    //
    // // add the y axis
    // svg.append("g")
    // 		.attr("class", "y axis")
    // 		.call(yAxis)
    // 	.append("text")
    // 		.attr("transform","rotate(-90)")
    // 		.attr("y",-60)
    // 		.attr("dy",".71em")
    // 		.style("text-anchor","end")
    // 		.text("Price ($)");
    //
    // // add circle at intersection
    // focus.append("circle")
    // 	.attr("class","y")
    // 	.attr("fill","none")
    // 	.attr("stroke","black")
    // 	.style("opacity",0.5)
    // 	.attr("r",8);
    //
    // // add horizontal line at intersection
    // focus.append("line")
    // 	.attr("class","x")
    // 	.attr("stroke","black")
    // 	.attr("stroke-dasharray","3,3")
    // 	.style("opacity",0.5)
    // 	.attr("x1", 0)
    // 	.attr("x2", width);
    //
    // // add vertical line at intersection
    // focus.append("line")
    // 	.attr("class","y")
    // 	.attr("stroke","black")
    // 	.attr("stroke-dasharray","3,3")
    // 	.style("opacity",0.5)
    // 	.attr("y1", 0)
    // 	.attr("y2", height);
    //
    // // append rectangle for capturing if mouse moves within area
    // svg.append("rect")
    // 	.attr("width",width)
    // 	.attr("height",height)
    // 	.style("fill","none")
    // 	.style("pointer-events","all")
    // 	.on("mouseover", function() { focus.style("display", null); })
    // 	.on("mouseout", function() { focus.style("display", "none"); })
    // 	.on("mousemove", mousemove);
    //
    // // add the line groups
    // var stock = svg.selectAll(".stockXYZ")
    // 		.data(stocks)
    // 	.enter().append("g")
    // 		.attr("class","stockXYZ");
    //
    // // add the stock price paths
    // stock.append("path")
    // 	.attr("class","line")
    // 	.attr("id",function(d,i){ return "id" + i; })
    // 	.attr("d", function(d) {
    // 		return line(d.values);
    // 	})
    // 	.style("stroke", function(d) { return color(d.name); });
    //
    //
    // // add the stock labels at the right edge of chart
    // var maxLen = data.length;
    // stock.append("text")
    // 	.datum(function(d) {
    // 		return {name: d.name, value: d.values[maxLen - 1]};
    // 	})
    // 	.attr("transform", function(d) {
    // 		return "translate(" + xScale(d.value.date) + "," + yScale(d.value.close) + ")";
    // 	})
    // 	.attr("id",function(d,i){ return "text_id" + i; })
    //   .attr("x", 3)
    //   .attr("dy", ".35em")
    //   .text(function(d) { return d.name; })
    //   .on("mouseover",function(d,i) {
    //   	for (j=0; j < 6; j++) {
    // 			if (i !== j) {
    // 				d3.select("#id"+j).style("opacity",0.1);
    // 				d3.select("#text_id"+j).style("opacity",0.2);
    // 			}
    // 		};
    //   })
    //   .on("mouseout", function(d,i) {
    //   	for (j=0; j < 6; j++) {
    // 			d3.select("#id"+j).style("opacity",1);
    // 			d3.select("#text_id"+j).style("opacity",1);
    // 		};
    //   });

    // mousemove function
    function mousemove() {

      var x0 = xScale.invert(d3.mouse(this)[0]);
      var i = bisectDate(data, x0, 1); // gives index of element which has date higher than x0
      var d0 = data[i - 1], d1 = data[i];
      var d = x0 - d0.date > d1.date - x0 ? d1 : d0;
      var close = d3.max([+d.Amazon,+d.Apple,+d.Facebook,+d.Google,+d.IBM,+d.Microsoft]);

      focus.select("circle.y")
      .attr("transform", "translate(" + xScale(d.date) + "," + yScale(close) + ")");

      focus.select("line.y")
      .attr("y2",height - yScale(close))
      .attr("transform", "translate(" + xScale(d.date) + ","
      + yScale(close) + ")");

      focus.select("line.x")
      .attr("x2",xScale(d.date))
      .attr("transform", "translate(0,"
      + (yScale(close)) + ")");

    };

  });
}
