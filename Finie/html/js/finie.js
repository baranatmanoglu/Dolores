var input = '{\"visuals\": {\"formattedResponse\": \"You have $4000.00 in your creditcard account. Here\'s what your balance looked like in the prior 2 dates.\",\"accountLabels\": [\"Fresca 2\",\"Mediterranean Wraps\",\"Anatolian Kitchen\",\"Douce France\",\"La Bicyclette\",\"Squ*sq *Sightglass Cof\",\"The Counter Palo Alto\",\"Others\"],\"speakableResponse\": \"You have 4000 dollars in your creditcard account. Here\'s what your balance looked like in the prior 2 dates.\",\"accountSpends\": [\"311.20\",\"234.35\",\"223.50\",\"207.09\",\"199.59\",\"174.31\",\"167.50\",\"1572.55\"]},\"intent\": \"balance\"}';


var pieChartTuples;
function visualizePieChart(input) {
    hideLoading();
    var jsonData = JSON.parse(input);
    var accountLabels = jsonData.visuals.accountLabels;
    var accountValues = jsonData.visuals.accountSpends;
    pieChartTuples = generatePieChartArray(accountLabels, accountValues);

    google.charts.load("current", {
        packages: ["corechart"]
    });
    google.charts.setOnLoadCallback(drawChart);
    showPieChart();
}


function generatePieChartArray(accountLabels, accountValues) {
    var response = new Array(accountLabels.length + 1);
    response[0] = ['Shop', 'Amount per shop'];
    for (var i = 0; i < accountLabels.length; i++) {
        var item = new Array(2);
        item[0] = accountLabels[i];
        item[1] = parseFloat(accountValues[i]);
        response[i + 1] = item;
    }
    return response;
}

function drawChart() {


    var data = google.visualization.arrayToDataTable(pieChartTuples);

    var options = {
        title: 'You spent $3090.09 from your accounts on Food and Drink, which is 6.24% of your total spending during May 2017.',
        pieHole: 0.4,
    };

    var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
    chart.draw(data, options);
}

function showLoading() {
    $("#loading_container").css("visibility", "visible");
}

function hideLoading() {
    $("#loading_container").css("visibility", "hidden");
}

function showPieChart(){
    $("#donutchart").css("visibility","visible");
}

function hidePieChart(){
     $("#donutchart").css("visibility","hidden");
}

$(document).ready(function () {
    visualizePieChart(input);
    session.subscribeToEvent("Finie/ShowPieChart", visualizePieChart);
    session.subscribeToEvent("Finie/ShowLoading", showLoading);
    session.subscribeToEvent("Finie/HideLoading", hideLoading);

});