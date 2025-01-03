let chosenTm = null;
let chosenTarget = null;
const msgDiv = document.getElementById('msg');

function chooseTm({tm}) {
    chosenTm = tm;
    const tmData = bagData.machines[tm];
    msgDiv.innerHTML = 'Teaching move: ' + tmData.move_data.name;
    // Indicate which pokemon can learn
    for (const [dex, tmSet] of Object.entries(tmCompat)) {
        const allPokes = document.querySelectorAll('[data-dex="' + dex + '"]');
        allPokes.forEach((button) => {
            if (tmSet.includes(tmData.move)) {
                button.disabled = false;
                button.getElementsByTagName('p')[0].innerHTML = 'Can learn!'
                button.onclick = function() {choosePokemon({slot: parseInt(button.dataset.slot)})};
            } else {
                button.disabled = true;
                button.getElementsByTagName('p')[0].innerHTML = 'Cannot learn!'
                button.onclick = null;
            }
        })
    }
    openTab('teach_tab', 'target_select');
    openTab('bag_tab', 'teach_tm');
}

function choosePokemon({slot}) {
    chosenTarget = "slot_" + (slot + 1).toString();
    const slotSelect = document.getElementById('slot_select');
    slotSelect.innerHTML = '';
    const chosenPokemon = partyMoves[slot];

    for (const [moveSlot, mData] of Object.entries(chosenPokemon.moves)) {
        slotSelect.append(document.createElement('br'));
        const slotButton = document.createElement('button');
        slotButton.classList.add('move-box');
        slotButton.onclick = function () {teachTm({slot: moveSlot})};

        if (mData == null) {
            slotButton.innerHTML = 'No move';
            slotSelect.append(slotButton);
            continue;
        }
        const moveName = document.createElement('p');
        moveName.innerHTML = mData.name;
        slotButton.append(moveName);

        const categoryIcon = document.createElement('img');
        categoryIcon.src = categoryPath + '/' + mData.damage_class + '.png';
        slotButton.append(categoryIcon);

        const typeIcon = document.createElement('img');
        typeIcon.src = typePath + '/' + mData.type + '.png';
        slotButton.append(typeIcon);

        slotSelect.append(slotButton);
    }
    openTab('teach_tab', 'slot_select');
}

function teachTm({slot}) {
    $.ajax(
        {
        type: "GET",
        url: teachUrl,
        data: {
            "tm": chosenTm,
            "target": chosenTarget,
            "slot": slot
        }
    }).done(function( response ) {
        if (response.msg != null) {
            msgDiv.innerHTML = response.msg;
            setTimeout(() => {
                openTab('bag_tab', 'machines');
                chosenTm = null
                chosenTarget= null;
            }, 3000);
        } else {
            msgDiv.innerHTML = 'Successfully taught move. Reloading...';
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    }).fail(function() {
        msgDiv.innerHTML = 'Teach TM request failed to send, please contact dev.';
    });
}