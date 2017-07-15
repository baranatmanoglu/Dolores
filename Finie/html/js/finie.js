var pieChartTuples;

function visualizePieChart(input) {

    hideLoading();
    var jsonData = JSON.parse(input);
    var accountLabels = jsonData.accountLabels;
    var accountValues = jsonData.accountSpends;
    pieChartTuples = generatePieChartArray(accountLabels, accountValues);

    google.charts.load("current", {
        packages: ["corechart"]
    });
    google.charts.setOnLoadCallback(drawPieChart);
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

function drawPieChart() {


    var data = google.visualization.arrayToDataTable(pieChartTuples);

    var options = {
        title: 'Your spending history',
        pieHole: 0.4,
    };

    var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
    chart.draw(data, options);
}

var barChartTuples;


function visualizeBarChartForIncome(input) {
    hideLoading();
    var jsonData = JSON.parse(input);
    var dates = jsonData.dateList;
    var balances = jsonData.incomeList[0].data;

    barChartTuples = generateBarChartTuples(dates, balances);
    google.charts.load("current", {
        packages: ['corechart']
    });
    google.charts.setOnLoadCallback(drawBarChart, "Your Income");
    showPieChart();
}

function visualizeBarChartForBalance(input) {
    hideLoading();
    var jsonData = JSON.parse(input);
    var dates = jsonData.dateList;
    var balances = jsonData.balanceList[0].data;

    barChartTuples = generateBarChartTuples(dates, balances);
    google.charts.load("current", {
        packages: ['corechart']
    });
    google.charts.setOnLoadCallback(drawBarChart, "Your Balance");
    showPieChart();
}

function generateBarChartTuples(dates, balances) {
    var response = new Array(dates.length + 1);
    response[0] = ["Element", "Density", {
        role: "style"
    }];
    for (var i = 0; i < dates.length; i++) {
        var item = new Array(3);
        item[0] = dates[i];
        item[1] = parseFloat(balances[i]);
        item[2] = "#76A7FA";
        response[i + 1] = item;
    }
    return response;
}


function drawBarChart(title) {

    var view = new google.visualization.DataView(google.visualization.arrayToDataTable(barChartTuples));
    view.setColumns([0, 1,
        {
            calc: "stringify",
            sourceColumn: 1,
            type: "string",
            role: "annotation"
        },
                       2]);

    var options = {
        title: title,
        width: 800,
        height: 600,
        bar: {
            groupWidth: "95%"
        },
        legend: {
            position: "none"
        },
    };
    var chart = new google.visualization.ColumnChart(document.getElementById("donutchart"));
    chart.draw(view, options);
}


var lineChartTuples;

function visualizeLineChartForAdvice(input) {
    hideLoading();

    $("#offer").css("visibility","visible");
    //var jsonData = JSON.parse(input);
    //var spendingList = jsonData.historyResponse.spendingLists;
    //var spendingTicks = jsonData.historyResponse.spendingTicks;
    //var spendingLabels = jsonData.historyResponse.spendingLabels;

    //lineChartTuples = generateLineChartTuples(spendingList, spendingTicks, spendingLabels);
    //google.charts.load('current', {
    //    'packages': ['corechart']
    //});
    //google.charts.setOnLoadCallback(drawLineChart);
    //showPieChart();
}



function generateLineChartTuples(spendingList, spendingTicks, spendingLabels) {
    var response = new Array(spendingTicks.length);
    var item = new Array(spendingLabels.length + 1);
    item[0] = 'Year';
    for (var i = 1; i <= spendingLabels.length; i++) {
        item[i] = spendingLabels[i - 1];
    }
    response[0] = item;
    for (var i = 1; i < spendingTicks.length - 1; i++) {
        item = new Array(spendingLabels.length + 1);
        item[0] = spendingTicks[i - 1];
        for (var j = 1; j <= spendingLabels.length; j++) {
            item[j] = spendingList[j - 1][i - 1];
        }
        response[i] = item;
    }
    return response;
}


function drawLineChart() {
    var data = google.visualization.arrayToDataTable(lineChartTuples);

    var options = {
        title: 'Spending Advice',
        curveType: 'function',
        legend: {
            position: 'bottom'
        }
    };

    var chart = new google.visualization.LineChart(document.getElementById('donutchart'));

    chart.draw(data, options);
}

var eta = new Date();
var ticketNumber;
var intervalId;
var otherIntervalId;

function showTicketData(input) {
    
    
    hideLoading();
    $("#ticket").css("visibility", "visible");
    var data = input.split("|");

    eta.setTime(eta.getTime() + (data[1] * 60 * 1000));
    eta.setTime(eta.getTime() - (7 * 60 * 60 * 1000));

    var ampm = eta.getHours() >= 12 ? "PM" : "AM";
    
    var minutes = eta.getMinutes() < 10 ? "0" +  eta.getMinutes() : eta.getMinutes();
    alert(minutes);
    $("#waitingTime").text("You'll be served ~" + eta.getHours() + ":" + minutes + " " + ampm);
    $("#ticketNumber").text("Your number: " + data[0]);
    ticketNumber = data[0];
    intervalId = setInterval("checkForQueue()", 20000);
    otherIntervalId = setInterval("checkForOtherCustomer()", 15000);
    checkForOtherCustomer();
}

function checkForQueue() {

    var current = new Date();
    current.setTime(current.getTime() - (7 * 60 * 60 * 1000));
    var distance = eta.getTime() - current.getTime();
    var seconds = Math.floor(distance / 1000);
    if (seconds < 60) {
        var tellerId = Math.floor(Math.random() * (10 - 1) + 1);
        $("#ticketNumber").text(ticketNumber + ">" + tellerId);
        $("#ticketNumber").addClass("blink_me");
        clearInterval(intervalId);
        session.raiseEvent("Finie/GoForTransaction", tellerId);
    }

}

var baseQueueNumber = [220, 340, 880, 100, 420, 510];

function checkForOtherCustomer() {

    var index = Math.floor(Math.random() * (5));
    var tellerId = Math.floor(Math.random() * (10 - 1) + 1);
    if (baseQueueNumber[index] == ticketNumber) {
        baseQueueNumber[index]++;
    }
    $("#otherCustomer").addClass("blink_me");
    $("#otherCustomer").text(baseQueueNumber[index] + " > " + tellerId);
    baseQueueNumber[index]++;
    setTimeout("clearBlink()", 3000);

}

function clearBlink() {
    $("#otherCustomer").removeClass("blink_me");
}

function showLoading() {
    $("#loading_container").css("visibility", "visible");
    
    hidePieChart();
}

function hideLoading() {
    $("#loading_container").css("visibility", "hidden");
}

function showPieChart() {
    $("#donutchart").css("visibility", "visible");
}

function hidePieChart() {
    $("#donutchart").css("visibility", "hidden");
    $("#offer").css("visibility","hidden");
}

$(document).ready(function () {
    
    session.subscribeToEvent("Finie/ShowPieChart", visualizePieChart);
    session.subscribeToEvent("Finie/ShowBarChartForBalance", visualizeBarChartForBalance);
    session.subscribeToEvent("Finie/ShowBarChartForIncome", visualizeBarChartForIncome);
    session.subscribeToEvent("Finie/ShowLineChartForAdvice", visualizeLineChartForAdvice);
    session.subscribeToEvent("Finie/ShowTicketData", showTicketData);
    session.subscribeToEvent("Finie/ShowLoading", showLoading);
    session.subscribeToEvent("Finie/HideLoading", hideLoading);


});