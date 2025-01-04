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

function removeParty(slot, url) {
    // Get the proper slot
    slot = "slot_" + slot;
    $.ajax(
    {
        type:"GET",
        url: url,
        data: {
            "payload": slot
        },
        success: function(response)
        {
            $("#party-container").html(response);
            if (window.location.pathname === '/box') {
                window.location.reload();
            }
        }
    });
}

function moveUp(slot, url) {
    // Get the proper slot
    slot_1 = "slot_" + slot;
    slot_2 = "slot_" + (slot - 1);
    $.ajax(
    {
        type:"GET",
        url: url,
        data: {
            "slot_1": slot_1,
            "slot_2": slot_2
        },
        success: function(response)
        {
            $("#party-container").html(response);
            if (window.location.pathname === '/bag') {
                window.location.reload();
            }
        }
    });
}

function clickNthButton(element, n) {
    // Get all button elements inside the found element
    const buttons = element.getElementsByTagName("button");

    // Check if the N'th button exists (1-based index)
    if (n > 0 && n <= buttons.length) {
        buttons[n - 1].click();
    }
}

function takeItem({id, url, onSuccess = null}) {
    $.ajax({
        type: "GET",
        url: url,
        data: {
            "id": id
        }
    }).done(function( response ) {
        if (onSuccess != null)
            onSuccess(response);
    });
}