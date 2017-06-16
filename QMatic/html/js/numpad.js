function keyClicked(value) {
    switch (value) {
        case "0":
        case "1":
        case "2":
        case "3":
        case "4":
        case "5":
        case "6":
        case "7":
        case "8":
        case "9":
            var current = $('#numpadOut').text();
            if (current.length == 16)
                return;
            current = current + value;
            $('#numpadOut').text(current);
            break;
        case "D":
            var current = $('#numpadOut').text();
            if (current.length == 0)
                return;
            current = current.substr(0,current.length-1);
            $('#numpadOut').text(current);
            break;
        default:
            break;
    }
}

