
var arcs = Array();

var defaultMapColor = 'rgb(66, 66, 66)';
var highlightMapColor = 'rgb(180, 180, 180)';
var selectedMapColor = 'rgb(221, 167, 67)';

var arcColors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5'];
var totalArcs = 0;

function test(name) {
  console.log(name);
}

function show_info(geography, e) {
  return;
  $(".country-info").html('<h6>' + geography.properties.name + '</h6>');
  $(".country-info").css({'top': e[1],'left': e[0]}).fadeIn();
}

var map = new Datamap({
  element: document.getElementById('map-container'),
  scope: 'world',

  fills: {
    defaultFill: defaultMapColor
  },
  geographyConfig: {
    highlightFillColor: highlightMapColor,
    borderColor: 'black',
    borderOpacity: 0.1,
    highlightBorderColor: 'rgba(10, 10, 10, 0.2)',
    highlightBorderWidth: 2,
    highlightBorderOpacity: 0.1,
    popupTemplate:  function(geography, data){
      test(geography.properties.name);
      return '<div class=hoverinfo><strong>' + geography.properties.name + '</strong></div>';
    },
  },



  done: function(datamap) {
    datamap.svg.selectAll('.datamaps-subunit').on('click', function(geography) {
      var country_name = geography.properties.name;

      // var defaultData = [{id: country_name, text: country_name}];
      // $('#country_select').data().select2.updateSelection(defaultData);

      show_info(geography, d3.mouse(this));
    });

    // ZOOM BEHAVIOR
    // datamap.svg.call(d3.behavior.zoom().on("zoom", redraw));
    // function redraw() {
    //   datamap.svg.selectAll("g").attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    // }

  }
});

function getCountryCode(country) {
  var countries = Datamap.prototype.worldTopo.objects.world.geometries;
  for (var j = 0; j < countries.length - 1; j++) {
    if (countries[j].properties.name.indexOf(country) >= 0) {
      return countries[j].id;
    }
  }
}

function setMapColor(color, country = '') {
  var countries = Datamap.prototype.worldTopo.objects.world.geometries;
  if (country) {
    for (var j = 0; j < countries.length - 1; j++) {
      if (countries[j].properties.name.indexOf(country) >= 0) {
        try {
          var obj = {};
          obj[countries[j].id] = color;
          map.updateChoropleth(obj);
        }
        catch (e) {
        }
        break;
      }
    }
  }
  else {
    for (var j = 0; j < countries.length - 1; j++) {
      try {
        var obj = {};
        obj[countries[j].id] = color;
        map.updateChoropleth(obj);
      }
      catch (e) {}
    }
  }
}

function clearArcs() {
  arcs = Array();
}

var colors = d3.scale.category10();


function drawArc(frequency, origin_lat, origin_lon, dest_lat, dest_lon) {

  var new_arc = {
    origin: {
      latitude: origin_lat,
      longitude: origin_lon
    },
    destination: {
      latitude: dest_lat,
      longitude: dest_lon
    },
    options: {
      strokeWidth: frequency / 10000,
      strokeColor: arcColors[totalArcs], //'rgba(100, 200, 200, 0.8)',
      greatArc: true
    }
  };

  arcs.push(new_arc);
  map.arc(arcs, {strokeWidth: 2});
}



function perc2color(perc) {
  var r, g, b = 0;
  if(perc < 50) {
    r = 255;
    g = Math.round(5.1 * perc);
  }
  else {
    g = 255;
    r = Math.round(510 - 5.10 * perc);
  }
  var h = r * 0x10000 + g * 0x100 + b * 0x1;
  return '#' + ('000000' + h.toString(16)).slice(-6);
}

function setMortality(country, mortality_rate) {

  // mortality_rate is per 1000, rescale to 100%.
  console.log(country, mortality_rate);
  var code = getCountryCode(country);
  var obj = {};
  obj[code] = perc2color(mortality_rate / 10);
  map.updateChoropleth(obj);
}
