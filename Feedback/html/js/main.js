function surveyClicked(value) {
    if(value != "G")
        $("#recorder").css("visibility","visible");
    session.raiseEvent("Feedback/SurveyClicked", value);
    
}

$(document).ready(function () {


});

var micState = 'off'
var timeOut;
function micClicked() {
    if (micState == 'off') {
        micState = 'on'; 
        $("#record").addClass("microphone-glow");
        $("#warning").css("visibility","visible");
        timeOut = setTimeout("micClicked()",5000);
        session.raiseEvent("Feedback/ProcessRecording","S");
    }
    
    else{
        clearTimeout(timeOut);
        micState = 'off';
        
        $("#record").removeClass("microphone-glow");
        $("#warning").css("visibility","hidden");
        session.raiseEvent("Feedback/ProcessRecording","E");
    }
    
}

function exit()
{
    session.raiseEvent("Feedback/ExitApp",1);
}

var checked = 1;
var timeout = 30000;

var checkForInput = function () {
    if (checked == 1)
        session.raiseEvent("Feedback/CheckForAction", "reminder")
    else if (checked == 2)
        session.raiseEvent("Feedback/CheckForAction", "endit")
    timeout = 7000;
    checked++;
}

setInterval(checkForInput, timeout);