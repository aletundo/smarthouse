var changeSensors = function(dataset){
  $.ajax({
    url: "/sensors_conf?dataset=" + dataset,
    type: "GET",
    success: function(sensors) {
      for (key in sensors) {
        $('.sensor' + key + ' span').html(sensors[key].replace('_', ' '));
        $('.sensor' + key + ' div').removeClass('led-green');
        $('.sensor' + key + ' div').addClass('led-red');
      }
    },
    dataType: "json",
    timeout: 2000
  });
};

// Create a list of day and monthnames.
var weekdays = [
  "Sunday", "Monday", "Tuesday",
  "Wednesday", "Thursday", "Friday",
  "Saturday"
],
months = [
  "January", "February", "March",
  "April", "May", "June", "July",
  "August", "September", "October",
  "November", "December"
];

// Create a new date from a string, return as a timestamp.
function timestamp(str){
  return new Date(str).getTime();
}

// Create a string representation of the date.
function formatDate ( date ) {
  return weekdays[date.getDay()] + ", " +
  date.getDate() + nth(date.getDate()) + " " +
  months[date.getMonth()] + " " +
  date.getFullYear();
}

// Append a suffix to dates.
// Example: 23 => 23rd, 1 => 1st.
function nth (d) {
  if(d>3 && d<21) return 'th';
  switch (d % 10) {
    case 1:  return "st";
    case 2:  return "nd";
    case 3:  return "rd";
    default: return "th";
  }
}

function updateSliderRange ( min, max, start ) {
  document.getElementById('training').noUiSlider.updateOptions({
    range: {
      'min': min,
      'max': max
    },
    start: start
  });
}

var dynamicColors = function() {
  var r = Math.floor(Math.random() * 255);
  var g = Math.floor(Math.random() * 255);
  var b = Math.floor(Math.random() * 255);
  return "rgb(" + r + "," + g + "," + b + ")";
}

$('#sensors_config').change(function(){
  dataset = $(this).val();
  changeSensors(dataset);
});

$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
  if (e.target.text === 'Random') {
    changeSensors($('#sensors_config').val());
  }else {
    changeSensors($('#dataset').val());
  }
});

$('#dataset').change(function(){
  dataset = $(this).val();
  changeSensors(dataset);
  if (dataset === 'OrdonezA') {
    start = [ timestamp('2011-11-29'), timestamp('2011-12-11') ]
    updateSliderRange(timestamp('2011-11-28 00:00:00'), timestamp('2011-12-11 00:00:00'), start)
  }else {
    start = [ timestamp('2012-11-12'), timestamp('2012-12-02') ]
    updateSliderRange(timestamp('2012-11-11 00:00:00'), timestamp('2012-12-02 00:00:00'), start)
  }
});
