/**
 * Created by berkeyanilmaz on 2017-06-27.
 */

function exit() {
    session.raiseEvent("GuideApp/ExitApp", 1);
}

//Subscribe to Chat Events
session.subscribeToEvent("GuideApp/ShowFeet", function () {
    console.log("Raised Event: GuideApp/Feet");
    $("#gif-green").css("visibility", "hidden");
    $("#gif-blue").css("visibility", "hidden");
    $("#gif-red").css("visibility", "hidden");
    $("#gif-feet").css("visibility", "visible");
});

session.subscribeToEvent("GuideApp/ShowRedEyes", function () {
    console.log("Raised Event: GuideApp/RedEyes");
    $("#gif-green").css("visibility", "hidden");
    $("#gif-blue").css("visibility", "hidden");
    $("#gif-feet").css("visibility", "hidden");
    $("#gif-red").css("visibility", "visible");
});

session.subscribeToEvent("GuideApp/ShowBlueEyes", function () {
    console.log("Raised Event: GuideApp/BlueEyes");
    $("#gif-green").css("visibility", "hidden");
    $("#gif-red").css("visibility", "hidden");
    $("#gif-feet").css("visibility", "hidden");
    $("#gif-blue").css("visibility", "visible");

});

session.subscribeToEvent("GuideApp/ShowGreenEyes", function () {
    console.log("Raised Event: GuideApp/GreenEyes");
    $("#gif-blue").css("visibility", "hidden");
    $("#gif-red").css("visibility", "hidden");
    $("#gif-feet").css("visibility", "hidden");
    $("#gif-green").css("visibility", "visible");

});

