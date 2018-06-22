// d3.csv({"WFPVAM_FoodPrices_version4_Retail.csv"}).then(function(experiments) {
//
// }


var dimensions = {};
var ndx = crossfilter();

var country_select = dc.selectMenu('#country_select');
// var city_select = dc.selectMenu('#city_select');
// var select1 = dc.selectMenu('#select1');

function numberFormat(number, decimals=2) {
  return "$" + number.toFixed(decimals);
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

function selectYear() {
  var year = $(this).html();
  // dimensions.yearDimension.filter(year);

  $(this).toggleClass('active');

  if ($(this).hasClass('active')) {
    selected_years.add(year);
  }
  else {
    selected_years.remove(year);
  }

  var countries = country_select.filters()
  get_country_data(countries);

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

  var url = "/country?";
  for (var i = 0; i < countries.length; i++) {
    url += "&country=" + countries[i];
  }

  for (var it = selected_years.values(), val=null; val=it.next().value; ) {
    url += "&year=" + val;
  }

  d3.json(url, function(data) {

    if (selected_years.size) {
      var chart = dc.dataTable("#test");
      var lineChart = dc.compositeChart("#test_2");
      var barChart = dc.barChart("#test_3");

      var country_data = data['data'];
      var ndx = crossfilter(country_data);
      let dimensionCategory = ndx.dimension(item => item.Iadm0_name);

      for (var i = 0; i < country_data.length; i++) {
        setMapColor(selectedMapColor, country_data[i].Iadm0_name);
      }

      console.log(country_data);

      chart.width(768)
      .height(480)
      .dimension(dimensionCategory)
      .group(function(d) { return ''; })
      .columns([
        {
          label: "Country",
          format: function (d) {
            return d.Iadm0_name;
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

      tmpProductGroup = timeCategory.group().reduceSum(function (d, g) {
        if (d.cm_name == productGroups[0]) {
          return d.mp_price;
        }
        return 0;
      });

      var subLineChart = dc.lineChart(lineChart).group(tmpProductGroup, productGroups[0]).colors(['#248221']);
      lines.push(subLineChart);

      lineChart
      .legend(dc.legend().x(60).y(10).itemHeight(13).gap(5))
      .transitionDuration(500)
      .mouseZoomable(true)
      .margins({top: 10, right: 10, bottom: 20, left: 40})
      .dimension(timeCategory)
      .compose(lines)
      .brushOn(false)
      .title('test')
      .elasticY(true)
      .x(d3.time.scale().domain(d3.extent(country_data, function(d) { return d.datetime; })))
      .xAxis();


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

      dc.renderAll();

    }
    for (var i = 0; i < data['years'].length; i++) {
      var year = data['years'][i];
      year_buttons[year].addClass('accessible');
      year_buttons[year].prop('disabled', false);
    }
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
