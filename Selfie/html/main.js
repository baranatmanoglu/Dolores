/**
 * Created by berkeyanilmaz on 2017-07-14.
 */

function showSocialMedia() {
    $("#socialPanel").css("visibility", "visible");
}

function showMaximumLogo() {
    $("#maximum").css("visibility", "visible");
}

function hideMaximumLogo() {
    $("#maximum").css("visibility", "hidden");
}

function hideSocialMedia() {
    $("#socialPanel").css("visibility", "hidden");
}

function hideSelfie() {
    $("#baran").css("visibility", "hidden");
}


session.subscribeToEvent("Selfie/HideScreen", function () {
    hideSocialMedia();
    hideMaximumLogo();
})

session.subscribeToEvent("Selfie/Animation", function () {
    hideSocialMedia();
    showMaximumLogo();
    hideSelfie();
})

session.subscribeToEvent("Selfie/EndAnimation", function () {
    hideMaximumLogo();
    showSocialMedia();
})