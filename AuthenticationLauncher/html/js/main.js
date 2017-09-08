function goNFC() {
    glowNfc();
    cutSpeech();
    session.raiseEvent("Authentication/GoNFC", 1);
    blowOutNfc();
}

function goQR() {
    glowQr();
    cutSpeech();
    session.raiseEvent("Authentication/GoQR", 1);
    blowOutQr();
}

function goListener() {
    glowListener();
    cutSpeech();
    session.raiseEvent("Authentication/GoListener", 1);
    blowOutListener();
}

function goKeyboard() {
    glowNumpad();
    cutSpeech();
    session.raiseEvent("Authentication/GoKeyboard", 1);
    blowOutNumpad();
}

function glowNfc() {
    $("#nfc_item").addClass("showcase");
    setTimeout(blowOutNfc, 1000);
}

function glowQr() {
    $("#qr_item").addClass("showcase");
    setTimeout(blowOutQr, 1000);
}

function glowListener() {
    $("#listener_id").addClass("showcase");
    setTimeout(blowOutListener, 1000);
    setTimeout(checkForInput, timeout);

}

function glowNumpad() {
    $("#numpad_id").addClass("showcase");
    setTimeout(blowOutNumpad, 1000);

}

function blowOutNfc() {
    $("#nfc_item").removeClass("showcase");
}

function blowOutQr() {
    $("#qr_item").removeClass("showcase");
}

function blowOutListener() {
    $("#listener_id").removeClass("showcase");
}

function blowOutNumpad() {
    $("#numpad_id").removeClass("showcase");
}

function blowOutAll() {
    blowOutQr();
    blowOutListener();
    blowOutNfc();
    blowOutNumpad();
}

function exit() {
    session.raiseEvent("Authentication/ExitApp", 1);
}



$(document).ready(function () {
    session.subscribeToEvent("Authentication/GlowNFC", glowNfc);
    session.subscribeToEvent("Authentication/GlowQR", glowQr);
    session.subscribeToEvent("Authentication/GlowKeyboard", glowNumpad);
    session.subscribeToEvent("Authentication/GlowListener", glowListener);
    session.raiseEvent("Authentication/StartDialog", 1);
});


var checked = 1;
var timeout = 5000;

var checkForInput = function () {
    if (checked == 1) {
        session.raiseEvent("Authentication/CheckForAction", "reminder");
        checked++;
        timeout = 10000;
        setTimeout(checkForInput, timeout);
    } else if (checked == 2) {
        session.raiseEvent("Authentication/CheckForAction", "endit");
    }

}

function cutSpeech(){
    session.service("ALTextToSpeech").then(function(tts) {
    tts.stopAll();
});
}