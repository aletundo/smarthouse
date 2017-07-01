$(document).ready(function(){
  Matrix({
    container : '#heatMapA',
    data :
[[7865,    0,    0,    0,    0,    0,    0,    0,    0],
 [   0,   52,    0,    0,    4,    1,   73,    0,    1],
 [   0,    0,  94,    2,    0,    0,   0,    0,    0],
 [   0,    0,    1,  111,    0,    0,    0,    0,    0],
 [   0,    2,    0,    0,   93,    5,    0,    0,    0],
 [   0,   11,    0,    0,   50, 8695,    1,    0,    1],
 [   0,   36,    0,    0,    0,    0, 1628,    0,    0],
 [   0,  104,    0,    0,    0,    1,    0,  206,    4],
 [   0,    0,    0,    0,    0,    0,    0,    6,    2]]
,
    labels    : ['Sleeping', 'Toileting', 'Showering', 'Breakfast', 'Grooming', 'Spare_Time/TV', 'Leaving', 'Lunch', 'Snack'],
    start_color : '#7df1f6',
    end_color : '#ff0000',
    legend : '#heatMapLegendA'
  });

  Matrix({
    container : '#heatMapB',
    data      : [
      [ 7433,    35,    36,     0,   112,     0,   154,    57,   975,     5],
      [    5,  354,    22,     2,    10,     7,   11,     0,    17,     1],
      [   19,    21,    95,     2,    14,     0,     6,     1,    25,     0],
      [    0,    10,    46, 10314,    41,     0,     4,     0,  345,     0],
      [    0,     0,     1,     0,   208,     0,     9,    67,    24,     0],
      [    0,     6,     0,     0,     5,    64,     0,     0,     0,     0],
      [   17,     2,     1,     0,    63,     0,    77,     9,   230,     7],
      [   14,     0,     1,     0,     0,     0,    20,    32,   329,     0],
      [    0,     0,     2,     0,     9,     0,     8,   35,  5222,     0],
      [   24,     0,     0,     0,    11,     0,    16,     0,    77,     4]],
      labels    : ['Sleeping', 'Toileting', 'Showering', 'Breakfast', 'Grooming', 'Spare_Time/TV', 'Leaving', 'Lunch', 'Snack', 'Dinner'],
      start_color : '#7df1f6',
      end_color : '#ff0000',
      legend : '#heatMapLegendB'
    });


    var ctx = document.getElementById("accuracyChart").getContext('2d');

    new Chart(ctx, {
      type: 'radar',
      data: {
        datasets: [{
          data: [1.0,0.68571302575668314, 0.9732142857142857, 0.99285714285714288, 0.88401360544217678, 0.99314632019337579, 0.91819291819291826, 0.79461489887757175, 0.9285714285714286],
          label: 'OrdonezA',
          borderColor: "rgb(116, 192, 241)",
          backgroundColor: "rgba(116, 192, 241, 0.2)"
        },{
          data: [0.84556278813825947, 0.81855277382698888, 0.48507799981585142, 0.95947036380145523, 0.82063492063492072, 0.90468922611779756, 0.33616433239204224, 0.42857142857142855, 0.9871395759044681, 0.51428571428571435],
          label: 'OrdonezB',
          borderColor: "rgb(255, 0, 0)",
          backgroundColor: "rgba(255, 0, 0, 0.2)"
        }],
        labels: ['Sleeping', 'Toileting', 'Showering', 'Breakfast', 'Grooming', 'Spare_Time/TV', 'Leaving', 'Lunch', 'Snack', 'Dinner'],
      },
      options: {
        responsive: false,
        title: {
          display: true,
          text: 'States accuracy'
        }
      }
    });

    var data = [
      {
        x:['OrdonezA', 'OrdonezB'],
        y: [0.856, 0.603],
        error_y: {
          type: 'data',
          array: [0.10048, 0.1076],
          visible: true
        },
        type: 'bar',
        name: 'F-Measure'
      }
    ];

    var layout = {
      title: 'F-Measure with standard deviation',
      showlegend: true
    };
    Plotly.newPlot("fmeasureChart", data, layout, {displayModeBar: false});
  });
