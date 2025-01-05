function openMessage(key) {
    $.ajax({
        url: openUrl,
        type: "GET",
        data: {
            "msg": key
        },
        success: function(data) {
            $("#message").html(data);
            openTab('inbox_tab', 'message');
        }
    });
}