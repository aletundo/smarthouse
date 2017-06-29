$(document).ready(function(){

  var dateValues = [
    document.getElementById('event-start'),
    document.getElementById('event-end')
  ];


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

  dateSlider.noUiSlider.on('update', function( values, handle ) {
    dateValues[handle].innerHTML = formatDate(new Date(+values[handle]));
  });

});
