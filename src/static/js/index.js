$(document).ready(function(){
  $('#playButton').click(function(){
    var samples = ($('#samples').val() !== '') ? $('#samples').val() : 10;
    var rate = ($('#rate').val() !== '') ? $('#rate').val()*1000 : 5000;
    var dataset = $('#dataset').val();
    i = 0;
      (function poll() {
        $.ajax({
            url: "/sampling?dataset=" + dataset,
            type: "GET",
            success: function(sample) {
              for (var j = 0; j < sample.length; j++) {
                if (sample[j] === '0') {
                  $('#sensor' + j + ' div').removeClass('led-green');
                  $('#sensor' + j + ' div').addClass('led-red');
                }else {
                  $('#sensor' + j + ' div').removeClass('led-red');
                  $('#sensor' + j + ' div').addClass('led-green');
                }
              }
              ++i;
            },
            dataType: "json",
            complete: (i < samples - 1) ? setTimeout(function() {poll()}, rate) : '',
            timeout: 2000
        });
      })();
  });
});
