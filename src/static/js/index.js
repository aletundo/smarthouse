$(document).ready(function(){
  var observations = [];

  $('#samplingButton').click(function(){
    // Get parameters
    var samples = ($('#samples').val() !== '') ? parseInt($('#samples').val()) : 10;
    var rate = ($('#rate').val() !== '') ? parseInt($('#rate').val())*1000 : 5000;
    var dataset = $('#sensors_config').val();

    // Clean all
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
        complete: (i < (samples) ) ? setTimeout(function() {poll();}, rate) : document.getElementById("viterbiRandomButton").disabled = false,
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

});
