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
    var current = $('#numpadOut').val()
    session.raiseEvent("Numpad/NumberEntered", current);
}

function exit(){
    session.raiseEvent("Numpad/ExitApp", 1);
}



function showLoading() {
    return;
    //$("#loading_container").css("visibility", "visible");
}

function hideLoading() {
    return;
    //$("#loading_container").css("visibility", "hidden");
}

function showNumPad() {
    $("#numpad_container").css("visibility", "visible");
}

function clearScreen() {
   $('#numpadOut').val(""); 
}


$(document).ready(function () {



    session.raiseEvent("Numpad/ReadyToGo", 1);
    session.subscribeToEvent("Numpad/ShowLoading", showLoading);
    session.subscribeToEvent("Numpad/HideLoading", hideLoading);
    session.subscribeToEvent("Numpad/CleanScreen", clearScreen);
    session.subscribeToEvent("Numpad/Timer", startTimer);
    session.subscribeToEvent("Numpad/Reminder", startTimer);



});
var checked = 1;

function startTimer()
{
    setTimeout(checkForInput, 5000);
}

var checkForInput = function () {
    var current = $('#numpadOut').val();

    if (current.length == 0) {
        if (checked == 1)
            session.raiseEvent("Numpad/CheckForAction", "reminder")
        else if (checked == 2)
            session.raiseEvent("Numpad/CheckForAction", "endit")
    }
    else{
        setTimeout(checkForInput, 5000);
    }
    if (checked == 10) {
        session.raiseEvent("Numpad/CheckForAction", "endit")
    }
    checked++;
}

