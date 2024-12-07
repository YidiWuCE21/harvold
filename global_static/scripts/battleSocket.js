let battleState = initialState;
let currentTurn = initialTurn;
let prevState = initialState;

// Moves
let moves = new Array(4).fill(null).map(() => ({}));
let buttonsActive = true;


// Handle socket stuff
const battleSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/battle/'
    + roomName
    + '/'
);

// Parse the incoming message; could be warning or state update
battleSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    // Display any warnings
    if (data.message != null) {
        document.querySelector('#chat-log').value += ('Warning: ' + data.message + '\n');
    }
    // Update the state
    if (data.state != null) {
        prevState = battleState;
        battleState = data.state;
        updateMoves();
        updateSwitches();
    }

    // Process outputs
    const interval = 1000;
    if (data.output != null) {
        let promise = Promise.resolve();
        data.output.push({"anim": ["enable"]});
        data.output.forEach(function (out) {
            promise = promise.then(function() {
                processOutput(out);
                return new Promise(function (resolve) {
                    setTimeout(resolve, interval);
                })
            });
        })
    }
};

battleSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

function processOutput({text = null, anim = null}) {
    if (text != null)
        document.querySelector('#chat-log').value += (text + '\n');
    if (anim != null) {
        document.querySelector('#chat-log').value += (anim + '\n');
        anim.forEach((animMove) => {
            processAnim({"animMove": animMove});
        })
    }
}

function processAnim({animMove}) {
    // Re-enable buttons after animations finished
    if (animMove == "enable") {
        toggleButtons(true);
        console.log("enabed!!!!");
    }
    // Attacks
    if ((isPlayerOne && animMove.startsWith('p1_physical')) || (!isPlayerOne && animMove.startsWith('p2_physical'))) {
        // Translate player
        attack({'x': '280', 'y': '70', 'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove.startsWith('p1_physical')) || (isPlayerOne && animMove.startsWith('p2_physical'))) {
        // Translate player
        attack({'x': '90', 'y': '120', 'div_id': 'opp_spr'});
    }
    if ((isPlayerOne && animMove.startsWith('p1_special')) || (!isPlayerOne && animMove.startsWith('p2_special'))) {
        // Translate player
        attack({'x': '185', 'y': '95', 'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove.startsWith('p1_special')) || (isPlayerOne && animMove.startsWith('p2_special'))) {
        // Translate player
        attack({'x': '185', 'y': '95', 'div_id': 'opp_spr'});
    }
    // Retreats
    if ((isPlayerOne && animMove == 'p1_retreat') || (!isPlayerOne && animMove == 'p2_retreat')) {
        disappear({'x': '20', 'y': '130', 'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove == 'p1_retreat') || (isPlayerOne && animMove == 'p2_retreat')) {
        disappear({'x': '350', 'y': '60', 'div_id': 'opp_spr'});
    }
    // Fainting
    if ((isPlayerOne && animMove == 'p1_faint') || (!isPlayerOne && animMove == 'p2_faint')) {
        disappear({'x': '70', 'y': '180', 'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove == 'p1_faint') || (isPlayerOne && animMove == 'p2_faint')) {
        disappear({'x': '300', 'y': '110', 'div_id': 'opp_spr'});
    }
    // New pokemon
    if ((isPlayerOne && animMove == 'p1_appear') || (!isPlayerOne && animMove == 'p2_appear')) {
        reappear({'x': '20', 'y': '130', 'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove == 'p1_appear') || (isPlayerOne && animMove == 'p2_appear')) {
        reappear({'x': '350', 'y': '60', 'div_id': 'opp_spr'});
    }
    // Sprite changes
    if ((isPlayerOne && animMove == 'p1_new_sprite') || (!isPlayerOne && animMove == 'p2_new_sprite')) {
        updateCanvas({'forPlayer': true});
        prevState = battleState;
    } else if ((!isPlayerOne && animMove == 'p1_new_sprite') || (isPlayerOne && animMove == 'p2_new_sprite')) {
        updateCanvas({'forPlayer': false});
        prevState = battleState;
    }
    // HP changes
    if ((isPlayerOne && animMove == 'p1_update_hp') || (!isPlayerOne && animMove == 'p2_update_hp')) {
        updateCanvas({'forPlayer': true, 'justHp': true, 'usePrev': true});
    } else if ((!isPlayerOne && animMove == 'p1_update_hp') || (isPlayerOne && animMove == 'p2_update_hp')) {
        updateCanvas({'forPlayer': false, 'justHp': true, 'usePrev': true});
    }
}

function attack({x, y, div_id}) {
    const sprite = document.getElementById(div_id);
    const splat = document.getElementById(div_id.replace('spr', 'splat'));

    const originalPosition = {
        x: sprite.offsetLeft,
        y: sprite.offsetTop
    };

    sprite.style.transition = 'all 1s ease';
    sprite.style.left = `${x}px`;
    sprite.style.top = `${y}px`;
    splat.style.transition = 'all 0.4s ease'

    setTimeout(() => {
        splat.style.opacity = 0.8;
    }, 100);

    setTimeout(() => {
        splat.style.opacity = 0;
    }, 390);

    setTimeout(() => {
        sprite.style.left = `${originalPosition.x}px`;
        sprite.style.top = `${originalPosition.y}px`;
    }, 390);
}

function toggleButtons(enable) {
    buttonsActive = enable;
    document.querySelectorAll('button.battler').forEach((button) => {
        button.disabled = !enable; // Disable if `enable` is false, enable if `true`
    });
}

function disappear({x, y, div_id}) {
    const sprite = document.getElementById(div_id);

    const originalPosition = {
        x: sprite.offsetLeft,
        y: sprite.offsetTop
    };

    sprite.style.transition = 'all 1s ease';
    sprite.transform = `translate(${x}px, ${y}px)`;
    sprite.style.opacity = 0.0

    sprite.style.left = `${originalPosition.x}px`;
    sprite.style.top = `${originalPosition.y}px`;
}

function reappear({x, y, div_id}) {
    const sprite = document.getElementById(div_id);

    const originalPosition = {
        x: sprite.offsetLeft,
        y: sprite.offsetTop
    };

    sprite.style.transition = null;
    sprite.style.left = `${x}px`;
    sprite.style.top = `${y}px`;
    sprite.style.opacity = 0.0

    sprite.style.transition = 'all 1s ease';
    sprite.style.left = `${originalPosition.x}px`;
    sprite.style.top = `${originalPosition.y}px`;
    sprite.style.opacity = 1.0
}

function sendMove({ action, move = null, item = null, target = null}) {
    if (action == null) {
        console.log("fail");
        return;
    }
    let message = {
        'action': action,
        'current_turn': currentTurn
    };
    if (action == 'attack') {
        if (move == null)
            throw new Error('Attack must choose a move!');
        message['move'] = move;
    } else if (action == 'item') {
        if (item == null)
            throw new Error('Item usage must choose an item!');
        if (target == null)
            throw new Error('Item usage must choose a target!');
        message['item'] = item;
        message['target'] = target;
    } else if (action == 'switch') {
        if (target == null)
            throw new Error('Switching must choose a target!');
        message['target'] = target;
    }
    battleSocket.send(JSON.stringify(message));
    toggleButtons(false);
}


// Functions for updating controls on state change
function updateMoves() {
    let player = null;
    if (isPlayerOne) {
        player = "player_1"
    } else {
        player = "player_2"
    }
    const pokemon = battleState[player]["current_pokemon"];
    const pokemonMoves = battleState[player]["party"][pokemon]["moves"];
    // Update each move
    pokemonMoves.forEach(function (move, i) {
        let moveButton = document.getElementById("move-" + (i + 1));
        if (move["move"] == null) {
            // No move case
            moves[i] = null;
            moveButton.disabled = true;
            moveButton.childNodes[0] = "No move learned";
            moveButton.children[1].src = "";
            moveButton.children[2].src = "";
        } else {
            // Standard case
            moves[i] = {"action": "attack", "move": move["move"]};
            if (move["pp"] < 1) {
                moveButton.disabled = true;
            } else {
                moveButton.disabled = !buttonsActive;
            }
            const moveInfo = moveData[move["move"]];
            moveButton.children[0].innerHTML = moveInfo["name"] + " - " + move["pp"] + "/" + moveInfo["pp"];
            moveButton.children[1].src = categoryPath + "/" + moveInfo["damage_class"] + ".png";
            moveButton.children[2].src = typePath + "/" + moveInfo["type"] + ".png";
        }
    });
}

function updateSwitches() {
    let player = null;
    if (isPlayerOne) {
        player = 'player_1'
    } else {
        player = 'player_2'
    }
    const party = battleState[player]['party'];
    const switchPane = document.getElementById('switch');
    switchPane.innerHTML = '';
    party.forEach(function (pkmn, i) {
        const switchButton = document.createElement('div');
        switchButton.classList.add("move-box");
        switchButton.classList.add("battler");
        switchButton.onclick = function () {
            sendMove({"action": "switch", "target": i});
            openTab('control-tab', 'select');
        };
        const pkmnIcon = document.createElement("img");
        pkmnIcon.src = iconPath + "/" + pkmn["dex_number"].toString().padStart(3, '0') + ".gif";
        switchButton.append(pkmnIcon);
        switchButton.append(pkmn["name"]);
        if (i == battleState[player]["current_pokemon"]) {
            // Pokemon is currently out
            switchButton.disabled = true;
        } else if (pkmn["current_hp"] < 1) {
            // Pokemon is knocked out
            switchButton.disabled = true;
        } else {
            // Can be switched to
            switchButton.disabled = !buttonsActive;
        }
        switchPane.append(switchButton);
    });
    const backButton = document.createElement('button');
    backButton.classList.add("button-3");
    backButton.classList.add("button-back");
    backButton.innerHTML = 'Cancel';
    backButton.onclick = function () {openTab('control-tab', 'select')};
    switchPane.append(backButton);
}

function updateCanvas({forPlayer, justHp = false, usePrev = false}) {
    // usePrev is just for previous Pokemon, current state still used
    let player = "player_2";
    let opp = "player_1";
    if (isPlayerOne) {
        player = "player_1";
        opp = "player_2"
    }
    let relevantState = battleState;
    if (usePrev)
        relevantState = prevState;
    if (forPlayer) {
        const playerPokemon = battleState[player]["party"][relevantState[player]["current_pokemon"]]
        const playerSpr = document.getElementById("player_spr");
        if (!justHp)
            playerSpr.src = backPath + "/" + playerPokemon["dex_number"].toString().padStart(3, '0') + ".png";
        const playerHp = document.getElementById("player_hp");
        playerHp.innerHTML = 'Lv. ' + playerPokemon["level"] + ' ' + playerPokemon["name"] + " " + playerPokemon["current_hp"] + "/" + playerPokemon["stats"]["hp"] + "<br/>" + playerPokemon["status"];

    } else {
        const oppPokemon = battleState[opp]["party"][relevantState[opp]["current_pokemon"]]
        const oppSpr = document.getElementById("opp_spr");
        if (!justHp)
            oppSpr.src = frontPath + "/" + oppPokemon["dex_number"].toString().padStart(3, '0') + ".png";
        const oppHp = document.getElementById("opp_hp");
        oppHp.innerHTML = 'Lv. ' + oppPokemon["level"] + ' ' + oppPokemon["name"] + " " + oppPokemon["current_hp"] + "/" + oppPokemon["stats"]["hp"] + "<br/>" + oppPokemon["status"];
    }
}

updateMoves();
updateSwitches();
updateCanvas({'forPlayer': true});
updateCanvas({'forPlayer': false});