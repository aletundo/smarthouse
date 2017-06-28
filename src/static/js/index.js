$(document).ready(function(){
  $('#playButton').click(function(){
    var samples = ($('#samples').val() !== '') ? $('#samples').val() : 10;
    var rate = ($('#rate').val() !== '') ? $('#rate').val()*1000 : 5000;
    var dataset = $('.dataset').val();
    i = 0;
      (function poll() {
        $.ajax({
            url: "/sampling?dataset=" + dataset,
            type: "GET",
            success: function(result) {
              configuration = result['configuration'];
              splitted = result['splitted']
              for (var j = 0; j < splitted.length; j++) {
                if (splitted[j] === '0') {
                  $('.sensor' + j + ' div').removeClass('led-green');
                  $('.sensor' + j + ' div').addClass('led-red');
                }else {
                  $('.sensor' + j + ' div').removeClass('led-red');
                  $('.sensor' + j + ' div').addClass('led-green');
                }
              }
              $('.configuration').html(configuration)
              ++i;
            },
            dataType: "json",
            complete: (i < samples - 1) ? setTimeout(function() {poll()}, rate) : '',
            timeout: 2000
        });
      })();
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
