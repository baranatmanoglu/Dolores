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






function enterPressed() {
    var current = $('#numpadOut').text()
    session.raiseEvent("Keyboard/NumberEntered", current);
}

function exit(){
    session.raiseEvent("Keyboard/ExitApp", 1);
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

function clearScreen() {
   $('#numpadOut').text(""); 
}


$(document).ready(function () {



    session.raiseEvent("Keyboard/ReadyToGo", 1);
    session.subscribeToEvent("Keyboard/NumpadInput", pressKey);
    session.subscribeToEvent("Keyboard/ShowLoading", showLoading);
    session.subscribeToEvent("Keyboard/HideLoading", hideLoading);
    session.subscribeToEvent("Keyboard/CleanScreen", clearScreen);



});
var checked = 1;

var checkForInput = function () {
    var current = $('#numpadOut').text();

    if (current.length == 0) {
        if (checked == 1)
            session.raiseEvent("Keyboard/CheckForAction", "reminder")
        else if (checked == 2)
            session.raiseEvent("Keyboard/CheckForAction", "endit")
    }
    if (checked == 3) {
        session.raiseEvent("Keyboard/CheckForAction", "endit")
    }
    checked++;
}

setInterval(checkForInput, 15000);