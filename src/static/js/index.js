$(document).ready(function(){
  var dynamicColors = function() {
    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
}

  var observations = [];

  $('#samplingButton').click(function(){
    var samples = ($('#samples').val() !== '') ? parseInt($('#samples').val()) : 10;
    var rate = ($('#rate').val() !== '') ? parseInt($('#rate').val())*1000 : 5000;
    var dataset = $('#sensors_config').val();

    observations = [];
    $('#observationsRandomList').html('');
    $('#statesRandomList').html('');
    i = 1;
    (function poll() {
      $.ajax({
        url: "/sampling?dataset=" + dataset,
        type: "GET",
        success: function(result) {
          ++i;
          configuration = result['configuration'];
          observations.push(configuration);
          splitted = result['splitted'];
          for (var j = 0; j < splitted.length; j++) {
            if (splitted[j] === '0') {
              $('.sensor' + j + ' div').removeClass('led-green');
              $('.sensor' + j + ' div').addClass('led-red');
            }else {
              $('.sensor' + j + ' div').removeClass('led-red');
              $('.sensor' + j + ' div').addClass('led-green');
            }
          }
          $('.configuration').html(configuration);
          $('#observationsRandomList').append('<li class="list-group-item">' + configuration + '</li>');
        },
        dataType: "json",
        complete: (i < (samples) ) ? setTimeout(function() {poll();}, rate) : '',
        timeout: 2000
      });
    })();
  });

  $('#viterbiRandomButton').click(function(){
    var dataset = $('#sensors_config').val();
    var mode = 'Random';
    $.ajax({
      url: "/viterbi",
      type: "POST",
      data: {dataset:dataset, observations: observations, mode: mode},
      success: function(result) {
        for (s of result['viterbi_states_sequence']) {
          $('#statesRandomList').append('<li class="list-group-item">' + s + '</li>');
        }

        var labels = [], datacounters = [], colors = [];

        for (var c in result['counter']) {
          datacounters.push(result['counter'][c]);
          labels.push(c);
          colors.push(dynamicColors());
        }

        var data = {
          datasets: [{
            data: datacounters,
            backgroundColor: colors
          }],
          labels: labels,
        };


        var options = {
          responsive: true,
        };

        var containerDiv = $('#randomPieChart').parent();
        $('#randomPieChart').remove();
        containerDiv.html('<canvas id="randomPieChart"><canvas>');
        var ctx = document.getElementById("randomPieChart").getContext('2d');
        var myLineChart = new Chart(ctx,{
          type: 'doughnut',
          data: data,
          options: options
        });
      },
      dataType: "json",
      timeout: 2000
    });
  });

  $('#viterbiPreloadedButton').click(function(){
    var dataset = $('#dataset').val();
    var mode = 'Preloaded';
    var train_days = document.getElementById('training').noUiSlider.get();
    train_days = train_days.map(function(e) {
      var date = new Date(parseInt(e));
      date.setUTCHours(00,00,00);
      return date.toISOString().replace('T',' ').split('.')[0];
    });
    $.ajax({
      url: "/viterbi",
      type: "POST",
      data: {dataset:dataset, mode: mode, start_day: train_days[0], end_day: train_days[1]},
      success: function(result) {
        var labels = [], datacounters = [], colors = [];

        for (var c in result['counter']) {
          datacounters.push(result['counter'][c]);
          labels.push(c);
          colors.push(dynamicColors());
        }

        var data = {
          datasets: [{
            data: datacounters,
            backgroundColor: colors
          }],
          labels: labels,
        };


        var options = {
          responsive: true,
        };

        var containerDiv = $('#randomPieChart').parent();
        $('#randomPieChart').remove();
        containerDiv.html('<canvas id="randomPieChart"><canvas>');
        var ctx = document.getElementById("randomPieChart").getContext('2d');
        var myLineChart = new Chart(ctx,{
          type: 'doughnut',
          data: data,
          options: options
        });
      },
      dataType: "json",
      timeout: 50000
    });
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

  var dateSlider = document.getElementById('training');

  noUiSlider.create(dateSlider, {
    // Create two timestamps to define a range.
    range: {
      min: timestamp('2011-11-28 00:00:00'),
      max: timestamp('2011-12-11 00:00:00')
    },
    behaviour: 'drag-tap',
    connect: [false, true, false],
    // Steps of one day
    step: 24 * 60 * 60 * 1000,

    // Two more timestamps indicate the handle starting positions.
    start: [ timestamp('2011-11-29 00:00:00'), timestamp('2011-12-11 00:00:00') ]
  });


  var dateValues = [
    document.getElementById('event-start'),
    document.getElementById('event-end')
  ];

  dateSlider.noUiSlider.on('update', function( values, handle ) {
    dateValues[handle].innerHTML = formatDate(new Date(+values[handle]));
  });

});
