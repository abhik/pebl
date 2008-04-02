// globals
selected_bar = null;
network_image_type = '';

// -------- Util Functions -----------------
// find max value in list
function listmax(list) {
    max = list[0];
    for (var i=0, ll=list.length; i<ll; i++) {
        max = Math.max(max, list[i]);
    }
    return max;
};

// -------------------------------------------

function network_image(rank) {
    return "data/" + rank + network_image_type + ".png";
};

function uselayout(type) {
    network_image_type = type;
    $("#network-viewer").attr('src', network_image($(selected_bar).attr('rank')));
};

function bargraph(elem, list, scores) {
    plotheight = 50;

    $(elem).empty().append("<table cellspacing='0'><tr>");
    for (var i=0, ll=list.length; i<ll; i++) {
        var td = "<td valign='bottom'><div class='bargraph-bar' score='";
        td += scores[i] + "' rank='" + i + "' ";
        td += "style='width:15px; height:" + (5 + (list[i] * plotheight));
        td += "px;'>&nbsp;</div>";
    $(elem).find("tr").append(td);
}
    $(elem).append("</tr></table>");

    // add hovering/selection color changes
    $(elem).find(".bargraph-bar").hover(
        function() { $(this).addClass('hover'); },
        function() { $(this).removeClass('hover'); }
    );

    // add bargraph selection
    $(elem).find(".bargraph-bar").click(function() {
        if (selected_bar != null) {
            $(selected_bar).removeClass('selected');
        }
        selected_bar = $(this);
        $(this).addClass('selected');
        
        // change page elements
        rank = $(selected_bar).attr('rank');
        score = $(selected_bar).attr('score');
        
        $("#network-viewer").attr('src', network_image(rank));
        $("#network-rank").text(rank);
        $("#network-score").text(score);
    });

    // select top network
    $($(elem).find(".bargraph-bar")[0]).click();
};

