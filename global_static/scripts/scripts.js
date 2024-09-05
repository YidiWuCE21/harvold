function openTab(tabGroup, tab) {
    var i;
    var tabs = document.getElementsByClassName(tabGroup);
    for (i = 0; i < tabs.length; i++) {
        tabs[i].style.display = "none";
    }
    document.getElementById(tab).style.display = "block";
}

function ajaxToHtml(url, sources, target) {
    var payload = {};
    sources.forEach(element => {
        payload[element] = $("#" + element).find(":selected").val();
    });
    $.ajax(
    {
        type:"GET",
        url: url,
        data: {
            "payload": payload
        },
        success: function(response)
        {
            $("#" + target).html(response);
        }
    });

}