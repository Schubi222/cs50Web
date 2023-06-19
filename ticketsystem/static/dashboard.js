import {displayMessage} from "./util.js";

document.addEventListener("DOMContentLoaded", ()=>{

    loadDashboard()
})

function loadDashboard(){
    fetch('/mydashboard/get')
        .then(response => response.json())
        .then(response => {
            if (response.error){
                displayMessage(response.message,response.error)
                return
            }
            const keys = Object.keys(response)
            const values = Object.values(response)
            let no_ticket = ""

            if (values[0]+values[1] === 0) {
                no_ticket = `<h3>You do not have any tickets!</h3>`
                // document.getElementById('chart_div1').innerHTML = `<h3>You do not have any tickets!</h3>`
            }
            else{
                let data_user = [[keys[0],values[0]],[keys[1],values[1]]]
                google.charts.load('current', {'packages':['corechart']}).then(() =>
                drawChart("Your Statistics", data_user,'chart_div1'))
            }


            if(values[2] !== "No Team")
            {
                if (values[2]+values[3] === 0){
                    no_ticket = `<h3>Your team does not have any tickets!</h3>`
                }
                else{
                    let data_team = [[keys[2],values[2]],[keys[3],values[3]]]
                    google.charts.load('current', {'packages':['corechart']}).then(() =>
                        drawChart('Your team\'s statistics', data_team, 'chart_div2'))
                }

            }
            if (values[4] + values[5] + values[6] === 0){
                no_ticket = `<h3>There are no tickets!</h3>`
            }
            else{
                let data_all = [[keys[4],values[4]],[keys[5],values[5]],[keys[6],values[6]]]
                google.charts.load('current', {'packages':['corechart']}).then(() =>
                    drawChart('Overall statistics',data_all,'chart_div3'))
            }
            if (no_ticket !== ''){
                document.getElementById('no_tickets_heading').innerHTML = no_ticket
            }

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
                   'width':320,
                   'height':300};

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById(div_id));
    chart.draw(data, options);
}