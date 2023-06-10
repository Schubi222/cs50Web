document.addEventListener("DOMContentLoaded", ()=>{

    loadDashboard()
})
/*
*   [
      ['Mushrooms', 3],
      ['Onions', 1],
      ['Olives', 1],
      ['Zucchini', 1],
      ['Pepperoni', 2]
    ]
*
* */
function loadDashboard(){
    fetch('/mydashboard/get')
        .then(response => response.json())
        .then(response => {
            const keys = Object.keys(response)
            const values = Object.values(response)

            let data_user = [[keys[0],values[0]],[keys[1],values[1]]]

            google.charts.load('current', {'packages':['corechart']}).then(() =>
                drawChart("Your Statistics", data_user,'chart_div1'))

            if(values[2] !== "No Team")
            {
                let data_team = [[keys[2],values[2]],[keys[3],values[3]]]

                google.charts.load('current', {'packages':['corechart']}).then(() =>
                    drawChart('Your team\'s statistics', data_team, 'chart_div2'))
            }

            let data_all = [[keys[4],values[4]],[keys[5],values[5]],[keys[6],values[6]]]

            google.charts.load('current', {'packages':['corechart']}).then(() =>
                drawChart('Overall statistics',data_all,'chart_div3'))

        })
}
function drawChart(titel, prepared_data,div_id) {

    // Create the data table.
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Type');
    data.addColumn('number', 'Amount');
    data.addRows(prepared_data);

    // Set chart options
    var options = {'title': titel,
                   'width':400,
                   'height':300};

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById(div_id));
    chart.draw(data, options);
}