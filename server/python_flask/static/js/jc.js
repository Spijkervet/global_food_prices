// d3.csv({"WFPVAM_FoodPrices_version4_Retail.csv"}).then(function(experiments) {
//
// }


var dimensions = {};
var ndx = crossfilter();



var country_select = dc.selectMenu('#country_select');
// var city_select = dc.selectMenu('#city_select');
// var select1 = dc.selectMenu('#select1');

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

function create_url(endpoint, countries) {
  var url = endpoint;
  for (var i = 0; i < countries.length; i++) {
    url += "&country=" + countries[i];
  }

  for (var it = selected_years.values(), val=null; val=it.next().value; ) {
    url += "&year=" + val;
  }
  return url;
}

//
// $.getJSON("/all_products", function(data) {
//
//   var ndx = crossfilter(data);
//   productDimension = ndx.dimension(function (d) {
//     return d.product;
//   });
//
//   product_select.dimension(productDimension)
//   .group(productDimension.group())
//   .multiple(true)
//   .numberVisible(10)
//   .controlsUseVisibility(true);
//
//   product_select.render();
// });

var country_ndx = crossfilter();
var selected_years = new Set();
var year_buttons = {};

var year_array = Array();

function deSelectAllYears() {

  for (var i = 0; i < year_array.length; i++) {
    selected_years.delete(year_array[i]);
    year_buttons[year_array[i]].removeClass('active');
  }

  var countries = country_select.filters();
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
  get_country_data(countries);

  // cluster_countries(countries);

}

$.getJSON("/years", function(data) {
  country_ndx.add(data);

  dimensions.yearDimension = country_ndx.dimension(function (d) {
    return d.year;
  });

  var year_el = $("#years");

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
});



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

$("#product_select").change(function() {
  var product = $(this).find(':selected').val();
  setMapColor(defaultMapColor);
  average_product(product);
})

$("#country_select").change(function() {
  var countries = country_select.filters();
  setMapColor(defaultMapColor);
  select_countries(countries);

  // if (selected_years.size) {
  //   cluster_countries(countries);
  // }
})

function select_countries(countries) {

  get_country_data(countries);
  for (var i = 0; i < countries.length; i++) {
    setMapColor(highlightMapColor, countries[i]);
  }
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


function get_country_data(countries) {


  $('.year-btn').removeClass('accessible');

  var url = create_url("/country?", countries);

  d3.json(url, function(data) {

    if (selected_years.size) {

      console.log("GETTING COUNTRY DATA", url, data);

      var chart = dc.dataTable("#test");
      var lineChart = dc.compositeChart("#test_2");
      var barChart = dc.barChart("#test_3");

      var country_data = data['data'];

      var unique_products = [];
      country_data.filter(function(item){
        var i = unique_products.indexOf(item.cm_name);
        if(i <= -1) {
          unique_products.push(item.cm_name);
        }
        return null;
      });

      var ndx = crossfilter(country_data);
      let dimensionCategory = ndx.dimension(item => item.adm0_name);

      for (var i = 0; i < country_data.length; i++) {
        setMapColor(selectedMapColor, country_data[i].adm0_name);
      }

      chart.width(768)
      .height(480)
      .dimension(dimensionCategory)
      .group(function(d) { return ''; })
      .columns([
        {
          label: "Country",
          format: function (d) {
            return d.adm0_name;
          }
        },
        {
          label: "Product",
          format: function (d) {
            return d.cm_name;
          }
        },
        {
          label: "USD",
          format: function (d) {
            return numberFormat(d.mp_price);
          }
        },
        {
          label: "Date",
          format: function (d) {
            return new Date(d.datetime).toISOString().split('T')[0];
          }
        },
      ]);

      let timeCategory = ndx.dimension(item => item.datetime);

      var productGroups = new Set;
      for (var i = 0; i < country_data.length; i++) {
        productGroups.add(country_data[i]['cm_name']);
      }

      var lines = []
      productGroups = Array.from(productGroups);

      var productGroup = timeCategory.group().reduceSum(dc.pluck('cm_name'));


      var names = country_data.map(function(row) { return row.cm_name; });
      names = names.filter(function(item, pos, self) {
        return self.indexOf(item) == pos;
      })


      var g_colors = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6", "#dd4477", "#66aa00", "#b82e2e", "#316395", "#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707", "#651067", "#329262", "#5574a6", "#3b3eac"];
      var positions = timeCategory.group().reduce(
        function(p, v) { // add
          p[v["cm_name"]] = (p[v["mp_price"]] || 0) + v["mp_price"];
          return p;
        },
        function(p, v) { // remove
          p[v["cm_name"]] -= v["mp_price"];
          return p;
        },
        function() { // initial
          return {};
        });


        console.log("COMPOSING FOR", url);
        lineChart.height(400)
        .legend(dc.legend().x(60).y(10).itemHeight(13).gap(2))
        .transitionDuration(500)
        .mouseZoomable(true)
        .margins({top: 10, right: 10, bottom: 20, left: 40})
        // .dimension(timeCategory)
        // .group(productGroup)
        .compose(

          names.map(function(name, idx) {
            return dc.lineChart(lineChart)
            // .renderArea(true)
            .mouseZoomable(true)
            .dimension(timeCategory)
            // .colors()
            .colors(function() {
              return g_colors[idx];
            })
            .group(positions, name)
            .round(d3.time.month.round)
            .xUnits(d3.time.months)
            .renderHorizontalGridLines(true)
            .valueAccessor(function(kv) {
              return kv.value[name];
            });
          })
        )
        .brushOn(true)
        // .elasticY(true)
        .x(d3.time.scale().domain(d3.extent(country_data, function(d) { return d.datetime; })))
        .xAxis();

        lineChart.on('pretransition.hideshow', function(chart) {
          chart.selectAll('g.dc-legend .dc-legend-item')
          .on('click.hideshow', function(d, i) {
            var subchart = chart.select('g.sub._' + i);
            var visible = subchart.style('visibility') !== 'hidden';
            subchart.style('visibility', function() {
              return visible ? 'hidden' : 'visible';
            });
            d3.select(this).style('opacity', visible ? 0.2 : 1);
          });
        });

        var productDimension = ndx.dimension(function(d) {return d.cm_name;}),
        productSum = productDimension.group().reduceSum(function(d) {return d.mp_price;});
        barChart
        .x(d3.scale.linear().domain([]))
        .xUnits(dc.units.ordinal)
        .brushOn(false)
        .xAxisLabel('Product')
        .yAxisLabel('USD')
        .dimension(productDimension)
        .barPadding(0.1)
        .outerPadding(0.05)
        .group(productSum);
      }
      for (var i = 0; i < data['years'].length; i++) {
        var year = data['years'][i];
        year_buttons[year].addClass('accessible');
        year_buttons[year].prop('disabled', false);
        year_array.push(year);
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
