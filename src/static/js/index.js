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
        showRandomModeResult(dataset, result);
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
        var labels = [], datacounters = [], colors = [], points = [], i = 1;

        $('#f_measure').html(result['f_measure']);
        $('#precision').html(result['precision']);
        $('#recall').html(result['recall']);
        
        for (s of result['viterbi_states_sequence']) {
          points.push({x: i, y: s})
          i++;
        }

        for (var c in result['counter']) {
          datacounters.push(result['counter'][c]);
          labels.push(c);
          colors.push(dynamicColors());
        }

        var containerDiv = $('#preloadedPieChart').parent();
        $('#preloadedPieChart').remove();
        containerDiv.html('<canvas id="preloadedPieChart"><canvas>');
        var ctx = document.getElementById("preloadedPieChart").getContext('2d');

        new Chart(ctx,{
          type: 'doughnut',
          data: {
            datasets: [{
              data: datacounters,
              backgroundColor: colors,
              label: dataset
            }],
            labels: labels,
          },
          options: {
            responsive: true,
          }
        });

        var containerDiv = $('#preloadedRadarChart').parent();
        $('#preloadedRadarChart').remove();
        containerDiv.html('<canvas id="preloadedRadarChart"><canvas>');
        var ctx = document.getElementById("preloadedRadarChart").getContext('2d');

        new Chart(ctx, {
          type: 'radar',
          data: {
            datasets: [{
              data: result['labels_accuracy'],
              label: dataset,
              borderColor: "rgb(116, 192, 241)",
              backgroundColor: "rgba(116, 192, 241, 0.2)"
            }],
            labels: result['possible_states_array'],
          },
          options: {
            responsive: true,
            title: {
              display: true,
              text: 'States accuracy'
            }
          }
        });

        var containerLine = $('#preloadedLineChart').parent();
        $('#preloadedLineChart').remove();
        containerLine.html('<canvas id="preloadedLineChart"><canvas>');
        var ctxLine = document.getElementById("preloadedLineChart").getContext('2d');

        new Chart(ctxLine, {
          type: 'line',
          data: {
            yLabels: labels,
            datasets: [{
              data: points,
              label: dataset,
              fill: false,
              borderColor: "#3e95cd"
            }]
          },
          options: {
            elements: {
              line: {
                tension: 0,
              }
            },
            title: {
              display: true,
              text: 'Most probable states sequence'
            },
            responsive: true,
            scales: {
              yAxes: [{
                type: 'category'
              }],
              xAxes: [{
                type: 'linear',
                ticks: {
                  max: points.length,
                  min: 1,
                  stepSize: 100
                }
              }]
            }
          }
        });

      },
      dataType: "json",
      timeout: 50000
    });
  });

  function showRandomModeResult(dataset, result){
    var labels = [], datacounters = [], colors = [], points = [], i = 1;
    for (s of result['viterbi_states_sequence']) {
      $('#statesRandomList').append('<li class="list-group-item">' + s + '</li>');
      points.push({x: i, y: s})
      i++;
    }
    for (var c in result['counter']) {
      datacounters.push(result['counter'][c]);
      labels.push(c);
      colors.push(dynamicColors());
    }

    var containerPie = $('#randomPieChart').parent();
    $('#randomPieChart').remove();
    containerPie.html('<canvas id="randomPieChart"><canvas>');
    var ctxPie = document.getElementById("randomPieChart").getContext('2d');
    new Chart(ctxPie,{
      type: 'doughnut',
      data: {
        datasets: [{
          data: datacounters,
          backgroundColor: colors,
          label: dataset
        }],
        labels: labels,
      },
      options: {
        responsive: true,
      }
    });

    var containerLine = $('#randomLineChart').parent();
    $('#randomLineChart').remove();
    containerLine.html('<canvas id="randomLineChart"><canvas>');
    var ctxLine = document.getElementById("randomLineChart").getContext('2d');

    new Chart(ctxLine, {
      type: 'line',
      data: {
        yLabels: labels,
        datasets: [{
          data: points,
          label: dataset,
          fill: false,
          borderColor: "#3e95cd"
        }]
      },
      options: {
        title: {
          display: true,
          text: 'Most probable states sequence'
        },
        responsive: true,
        scales: {
          yAxes: [{
            type: 'category'
          }],
          xAxes: [{
            type: 'linear',
            ticks: {
              max: points.length,
              min: 1,
              stepSize: 1
            }
          }]
        }
      }
    });
  }
});
