
var defaultMapColor = 'rgb(66, 66, 66)';
var highlightMapColor = 'rgb(180, 180, 180)';
var selectedMapColor = 'rgb(221, 167, 67)';

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
      country_select.filter(country_name)
      select_countries(country_select.filters());
      country_select.render();
      show_info(geography, d3.mouse(this));
    });

    datamap.svg.call(d3.behavior.zoom().on("zoom", redraw));
    function redraw() {
      datamap.svg.selectAll("g").attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }

  }
});

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
