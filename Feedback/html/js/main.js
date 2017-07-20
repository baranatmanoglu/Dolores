function surveyClicked(value) {
    if(value != "G")
        $("#recorder").css("visibility","visible");
    session.raiseEvent("Feedback/SurveyClicked", value);
    
}

$(document).ready(function () {

    session.subscribeToEvent("Feedback/SetRecordDuration",setDuration);
});

var micState = 'off'
var timeOutId;
var recordDuration;
function setDuration(val)
{
    recordDuration = parseInt(val) * 1000;
}

function micClicked() {
    if (micState == 'off') {
        micState = 'on'; 
        $("#record").addClass("microphone-glow");
        $("#warning").css("visibility","visible");
        timeOutId = setTimeout("micClicked()",recordDuration);
        session.raiseEvent("Feedback/ProcessRecording","S");
    }
    
    else{
        clearTimeout(timeOutId);
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