var tiles = new Array(),
    flips = new Array('tb', 'bt', 'lr', 'rl'),
    iFlippedTile = null,
    iTileBeingFlippedId = null,
    tileAllocation = null,
    iTimer = 0,
    iInterval = 100,
    iPeekTime = 3000;

var totalTiles = 16;
var attempts = 0;
var tilesFound = 0;
var animalNames = new Array('bear', 'elephant', 'giraffe', 'kangroo', 'lion', 'penguin', 'racoon', 'zebra');
var lastTouched = null;
var checked =1;
function getRandomImageForTile() {

    var iRandomImage = Math.floor((Math.random() * tileAllocation.length)),
        iMaxImageUse = 2;

    while (tileAllocation[iRandomImage] >= iMaxImageUse) {

        iRandomImage = iRandomImage + 1;

        if (iRandomImage >= tileAllocation.length) {

            iRandomImage = 0;
        }
    }

    return iRandomImage;
}

function createTile(iCounter) {

    var curTile = new tile("tile" + iCounter),
        iRandomImage = getRandomImageForTile();

    tileAllocation[iRandomImage] = tileAllocation[iRandomImage] + 1;

    curTile.setFrontColor("tileColor");
    curTile.setStartAt(500 * Math.floor((Math.random() * 5) + 1));
    curTile.setFlipMethod(flips[Math.floor((Math.random() * 3) + 1)]);
    curTile.setBackContentImage("images/" + animalNames[iRandomImage] + ".png");
    curTile.setFileName(animalNames[iRandomImage]);

    return curTile;
}

function initState() {

    /* Reset the tile allocation count array.  This
    	is used to ensure each image is only 
    	allocated twice.
    */
    tileAllocation = new Array(0, 0, 0, 0, 0, 0, 0, 0);

    while (tiles.length > 0) {
        tiles.pop();
    }

    $('#board').empty();
    iTimer = 0;

}

function initTiles() {

    var iCounter = 0,
        curTile = null;

    initState();

    // Randomly create twenty tiles and render to board
    for (iCounter = 0; iCounter < totalTiles; iCounter++) {

        curTile = createTile(iCounter);

        $('#board').append(curTile.getHTML());

        tiles.push(curTile);
    }
}

function hideTiles(callback) {

    var iCounter = 0;

    for (iCounter = 0; iCounter < tiles.length; iCounter++) {

        tiles[iCounter].revertFlip();

    }

    callback();
}

function revealTiles(callback) {

    var iCounter = 0,
        bTileNotFlipped = false;

    for (iCounter = 0; iCounter < tiles.length; iCounter++) {

        if (tiles[iCounter].getFlipped() === false) {

            if (iTimer > tiles[iCounter].getStartAt()) {
                tiles[iCounter].flip();
            } else {
                bTileNotFlipped = true;
            }
        }
    }

    iTimer = iTimer + iInterval;

    if (bTileNotFlipped === true) {
        setTimeout("revealTiles(" + callback + ")", iInterval);
    } else {
        callback();
    }
}

function showMatched(tile) {

    $("#bigpictureanimal").attr("src", "images/" + tile.getFileName() + "B.png");
    $("#bigpicture").css("visibility", "visible");


}

function hideMatched() {

    checkFinalState();
    $("#bigpictureanimal").attr("src", "");
    $("#bigpicture").css("visibility", "hidden");
}

function checkMatch() {

    lastTouched = new Date().getTime();
    if (iFlippedTile === null) {

        iFlippedTile = iTileBeingFlippedId;

    } else {
        attempts++;
        if (tiles[iFlippedTile].getBackContentImage() !== tiles[iTileBeingFlippedId].getBackContentImage()) {
            //This is fail
            setTimeout("tiles[" + iFlippedTile + "].revertFlip()", 2000);
            setTimeout("tiles[" + iTileBeingFlippedId + "].revertFlip()", 2000);
            session.raiseEvent("PairGame/PairNotFound", 1);

        } else {
            tilesFound += 2;
            var eventVal = "N";
            var tf2 = tilesFound / 2;
            if (tf2 != 1) {
                if (tf2 / attempts <= 1.2) {
                    eventVal = "G"
                }
            }
            eventVal = eventVal + ";" + tiles[iTileBeingFlippedId].getFileName();
            setTimeout("showMatched(tiles[" + iFlippedTile + "])", 1500);

            session.raiseEvent("PairGame/PairFound", eventVal);

        }

        iFlippedTile = null;
        iTileBeingFlippedId = null;
    }

}

function checkFinalState() {
    if (totalTiles == tilesFound) {
        console.log("Mission accomplished: " + attempts);
        session.raiseEvent("PairGame/GameFinished", attempts);
    }
}

function onPeekComplete() {

    $('div.tile').click(function () {

        iTileBeingFlippedId = this.id.substring("tile".length);

        if (tiles[iTileBeingFlippedId].getFlipped() === false) {
            tiles[iTileBeingFlippedId].addFlipCompleteCallback(function () {
                checkMatch();
            });
            tiles[iTileBeingFlippedId].flip();
        }

    });
}

function onPeekStart() {
    setTimeout("hideTiles( function() { onPeekComplete(); })", iPeekTime);
}

function startGame() {
    initTiles();
    setTimeout("revealTiles(function() { onPeekStart(); })", iInterval);
    lastTouched = new Date().getTime();
    setInterval("checkTimer()", 1000);
}

function checkTimer() {

    console.log("checking");
    // Get todays date and time
    var now = new Date().getTime();

    // Find the distance between now an the count down date
    var distance = now - lastTouched;


    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    if (seconds > 30) {
        lastTouched = new Date().getTime();
        
        if (checked == 1)
            session.raiseEvent("PairGame/CheckForAction", "reminder");
        else if (checked == 2)
            session.raiseEvent("PairGame/CheckForAction", "endit");
        checked++;
    }
}

function showPrize() {
    $("#prize").css("visibility", "visible");
}


$(document).ready(function () {

    
    session.subscribeToEvent("PairGame/ShuffleCards", startGame);
    session.subscribeToEvent("PairGame/ShowPrize", showPrize);
    session.subscribeToEvent("PairGame/HideTriviaScreen", hideMatched);


});