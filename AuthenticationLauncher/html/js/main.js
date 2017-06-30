function goNFC() {
    glowNfc();
    session.raiseEvent("Authentication/GoNFC", 1);
    blowOutNfc();
}

function goQR() {
    glowQr();
    session.raiseEvent("Authentication/GoQR", 1);
    blowOutQr();
}

function goListener() {
    glowListener();
    session.raiseEvent("Authentication/GoListener", 1);
    blowOutListener();
}

function goKeyboard() {
    glowNumpad();
    session.raiseEvent("Authentication/GoKeyboard", 1);
    blowOutNumpad();
}

function glowNfc() {
    $("#nfc_item").addClass("glowing-item");
    setTimeout(blowOutNfc, 1000);
}

function glowQr() {
    $("#qr_item").addClass("glowing-item");
    setTimeout(blowOutQr, 1000);
}

function glowListener() {
    $("#listener_id").addClass("glowing-item");
    setTimeout(blowOutListener, 1000);

}

function glowNumpad() {
    $("#numpad_id").addClass("glowing-item");
    setTimeout(blowOutNumpad, 1000);

}

function blowOutNfc() {
    $("#nfc_item").removeClass("glowing-item");
}

function blowOutQr() {
    $("#qr_item").removeClass("glowing-item");
}

function blowOutListener() {
    $("#listener_id").removeClass("glowing-item");
}

function blowOutNumpad() {
    $("#numpad_id").removeClass("glowing-item");
}

function blowOutAll() {
    blowOutQr();
    blowOutListener();
    blowOutNfc();
    blowOutNumpad();
}





$(document).ready(function () {
    session.subscribeToEvent("Authentication/GlowNFC", glowNfc);
    session.subscribeToEvent("Authentication/GlowQR", glowQr);
    session.subscribeToEvent("Authentication/GlowKeyboard", glowNumpad);
    session.subscribeToEvent("Authentication/GlowListener", glowListener);
    session.raiseEvent("Authentication/StartDialog", 1);
});


var checked = 1;
var timeout = 30000;

var checkForInput = function () {
    if (checked == 1)
        session.raiseEvent("Authentication/CheckForAction", "reminder")
    else if (checked == 2)
        session.raiseEvent("Authentication/CheckForAction", "endit")
    timeout = 7000;
    checked++;
}

setInterval(checkForInput, timeout);