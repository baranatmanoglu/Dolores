/**
 * Created by berkeyanilmaz on 2017-06-27.
 */
// Camera
session.subscribeToEvent("QRReader/StartTimer", function() {
    session.service("ALVideoDevice").then(function(vid) {
        var theVideoDevice = vid;
        VideoUtils.unsubscribeAllHandlers(theVideoDevice, "pepper"+"_camera").then(function() {
            VideoUtils.startVideo(theVideoDevice, "videoBuffer",2, 30, 0)
            $('#loading_video').hide();
        });
    });
})



var c=document.getElementById("borders");
var ctx=c.getContext("2d");
ctx.fillStyle="#00FF00";
ctx.fillRect(100,50,40,8);
ctx.fillRect(100,50,8,40);

ctx.fillRect(100,150,8,40);
ctx.fillRect(100,182,40,8);

ctx.fillRect(200,50,40,8);
ctx.fillRect(232,50,8,40);

ctx.fillRect(232,150,8,40);
ctx.fillRect(200,182,40,8);

$(document).ready(function(){
    session.service("ALVideoDevice").then(function(vid) {
        var theVideoDevice = vid;
        VideoUtils.unsubscribeAllHandlers(theVideoDevice, "pepper"+"_camera").then(function() {
            VideoUtils.startVideo(theVideoDevice, "videoBuffer",1, 40, 0)
            $('#loading_video').hide();
        });
    });
    
});