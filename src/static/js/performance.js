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
      labels    : ['Spare_Time/TV', 'Grooming', 'Toileting', 'Sleeping', 'Breakfast', 'Showering', 'Snack', 'Lunch', 'Leaving', 'Dinner'],
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
          data: [0.95947036380145523, 0.48507799981585142, 0.90468922611779756, 0.82063492063492072, 0.81855277382698888, 0.84556278813825947, 0.9871395759044681, 0.42857142857142855, 0.33616433239204224, 0.51428571428571435],
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


    var ctxLine = document.getElementById("learningCurveChartA").getContext('2d');

    new Chart(ctxLine, {
      type: 'line',
      data: {
        datasets: [{
          data: [0.77964216588095503, 0.72055856715188071, 0.66604938271604941, 0.57786922294296372, 0.6651785714285714, 0.85042851408016906, 0.81912462190526325, 0.62550875050875043, 0.69880952380952377, 0.8738047949722727, 0.62830951455052175, 0.82607551807632917, 0.77730573710965867],
          label: 'OrdonezA',
          fill: false,
          borderColor: "#3e95cd"
        }],
        labels : ['1 day', '2 days', '3 days','4 days', '5 days', '6 days', '7 days', '8 days', '9 days', '10 days', '11 days', '12 days', '13 days']
      },
      options: {
        title: {
          display: true,
          text: 'Learning curve Ordonez A'
        },
        responsive: false
      }
    });

    ctxLine = document.getElementById("learningCurveChartB").getContext('2d');

    new Chart(ctxLine, {
      type: 'line',
      data: {
        datasets: [{
          data: [0.52257532061536915, 0.44031349485894078, 0.48602399845155692, 0.38666519446453645, 0.44126874655908943, 0.54074247198039482, 0.48875435228028796, 0.4989369261053036, 0.64185905572746094, 0.64907918593651526, 0.49416265116440522, 0.48499937598141601, 0.50203785854438654, 0.62291075962784559, 0.55022151878550452, 0.60627448156725783, 0.61537871050827031, 0.57881662254636312, 0.28468859157413928, 0.53053682981604533],
          label: 'OrdonezB',
          fill: false,
          borderColor: "#ff0000"
        }],
        labels : ['1 day', '2 days', '3 days','4 days', '5 days', '6 days', '7 days', '8 days', '9 days', '10 days', '11 days', '12 days', '13 days', '14 days',  '15 days', '16 days','17 days','18 days','19 days','20 days']
      },
      options: {
        title: {
          display: true,
          text: 'Learning curve Ordonez B'
        },
        responsive: false
      }
    });
  });
