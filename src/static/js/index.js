$(document).ready(function(){
  var observations = [];

  $('#playButton').click(function(){
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
    $.ajax({
        url: "/viterbi",
        type: "POST",
        data: {dataset:dataset, observations: observations},
        success: function(states) {
          for (s of states) {
            $('#statesRandomList').append('<li class="list-group-item">' + s + '</li>');
          }
        },
        dataType: "json",
        timeout: 2000
    });
  });


  $('#dataset').change(function(){
    dataset = $(this).val();
    changeSensors(dataset);
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

});
