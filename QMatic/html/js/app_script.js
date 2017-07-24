function pressKey(number) {
    switch (number) {
        case "one":
            keyClicked(1);
            break;
        case "two":
            keyClicked(2);
            break;
        case "three":
            keyClicked(3);
            break;
        case "four":
            keyClicked(4);
            break;
        case "five":
            keyClicked(5);
            break;
        case "six":
            keyClicked(6);
            break;
        case "seven":
            keyClicked(7);
            break;
        case "eight":
            keyClicked(8);
            break;
        case "nine":
            keyClicked(9);
            break;
        case "zero":
        default:
            keyClicked(0);
            break;
    }
}

function showTicket(value) {
    $("#candidate_container").css("visibility", "hidden");
    $("#ticket_container").css("visibility", "visible");
    $("#ticket").text(value);
}






function exitPressed() {
    session.raiseEvent("QueueMatic/ExitApp", 1);
}



function tellerPressed() {
    //var current = $('#numpadOut').text() + ",T";
    session.raiseEvent("QueueMatic/OptionSelected", "T");
}


function custRepPressed() {
    //var current = $('#numpadOut').text() + ",C";
    session.raiseEvent("QueueMatic/OptionSelected", "C");
}


function showLoading() {
    $("#loading_container").css("visibility", "visible");
}

function hideLoading() {
    $("#loading_container").css("visibility", "hidden");
}

function showNumPad() {
    $("#numpad_container").css("visibility", "visible");
}


function exit() {
    session.raiseEvent("QueueMatic/ExitApp", 1);
}

$(document).ready(function () {


    $("#numpad_container").css("visibility", "hidden");
    session.raiseEvent("QueueMatic/ReadyToGo", 1);
    session.subscribeToEvent("QueueMatic/NumpadInput", pressKey);
    session.subscribeToEvent("QueueMatic/NumpadInputTeller", tellerPressed);
    session.subscribeToEvent("QueueMatic/NumpadInputCust", custRepPressed);
    session.subscribeToEvent("QueueMatic/ShowTicketNumber", showTicket);
    session.subscribeToEvent("QueueMatic/ShowLoading", showLoading);
    session.subscribeToEvent("QueueMatic/HideLoading", hideLoading);
    session.subscribeToEvent("QueueMatic/StartTimer", startTimer);




});

var checked = 1;

var checkForInput = function () {


    if (checked == 1) {
        session.raiseEvent("QueueMatic/CheckForAction", "10");
        checked++;
    } else if (checked == 2)
        session.raiseEvent("QueueMatic/CheckForAction", "20");



}

function startTimer() {
    setTimeout(checkForInput, 5000);
}