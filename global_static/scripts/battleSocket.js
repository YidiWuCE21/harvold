let battleState = initialState;
let currentTurn = initialTurn;
let prevState = initialState;
let interval = 1000;
let selectedItem = null;
let prompt = null;

// Moves
let moves = new Array(4).fill(null).map(() => ({}));
let buttonsActive = true;


// Handle socket stuff
let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
const battleSocket = new WebSocket(
    ws_scheme
    + '://'
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
        document.querySelector('#chat-log').scrollTop = document.querySelector('#chat-log').scrollHeight;
        toggleButtons(true);
    }
    // Update the state
    if (data.state != null) {
        prevState = battleState;
        battleState = data.state;
        updateMoves();
        updateSwitches();
        updateInventory();
    }

    if (data.prompt != null) {
        prompt = data.prompt;
    }

    // Process outputs
    if (data.output != null) {
        let promise = Promise.resolve();
        data.output.push({"anim": ["turnEnd"]});
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

function endBattle() {
    const endPane = document.getElementById('end');
    if (prompt == null)
        return;
    for (const [displayText, nextUrl] of Object.entries(prompt)) {
        const endButton = document.createElement('a');
        endButton.href = nextUrl;
        endButton.innerHTML = displayText;
        endButton.classList.add('move-box');
        endPane.append(endButton);
    }
    openTab('control-tab', 'end');
}

function processOutput({text = null, anim = null}) {
    if (text != null)
        document.querySelector('#chat-log').value += (text + '\n');
        document.querySelector('#chat-log').scrollTop = document.querySelector('#chat-log').scrollHeight;
    if (anim != null) {
        anim.forEach((animMove) => {
            processAnim({"animMove": animMove});
        })
    }
}

function processAnim({animMove}) {
    // Re-enable buttons after animations finished
    if (animMove == "turnEnd") {
        if (battleState.outcome == null) {
            toggleButtons(true);
        } else {
            endBattle();
        }
    }
    if (animMove == 'player_info') {
        const playerInfo = document.getElementById('player_info').children;
        for (let i = 0; i < playerInfo.length; i++) {
            playerInfo[i].style.transition = 'opacity 1s';
            playerInfo[i].style.opacity = '1';
        }
    }
    if (animMove == 'opp_info') {
        const oppInfo = document.getElementById('opp_info').children;
        for (let i = 0; i < oppInfo.length; i++) {
            oppInfo[i].style.transition = 'opacity 1s';
            oppInfo[i].style.opacity = '1';
        }
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
    if ((isPlayerOne && animMove.startsWith('p1_status')) || (!isPlayerOne && animMove.startsWith('p2_status'))) {
        // Translate player
        wiggle({'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove.startsWith('p1_status')) || (isPlayerOne && animMove.startsWith('p2_status'))) {
        // Translate player
        wiggle({'div_id': 'opp_spr'});
    }
    // Retreats
    if ((isPlayerOne && animMove == 'p1_retreat') || (!isPlayerOne && animMove == 'p2_retreat')) {
        disappear({'x': '20', 'y': '130', 'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove == 'p1_retreat') || (isPlayerOne && animMove == 'p2_retreat')) {
        disappear({'x': '350', 'y': '60', 'div_id': 'opp_spr'});
    }
    if (animMove == 'trainer_retreat') {
        disappear({'x': '20', 'y': '142', 'div_id': 'player_spr'});
    }
    // Fainting
    if ((isPlayerOne && animMove == 'p1_faint') || (!isPlayerOne && animMove == 'p2_faint')) {
        disappear({'x': '70', 'y': '180', 'div_id': 'player_spr'});
        updateBalls();
        openTab('control-tab', 'switch');
    } else if ((!isPlayerOne && animMove == 'p1_faint') || (isPlayerOne && animMove == 'p2_faint')) {
        disappear({'x': '300', 'y': '110', 'div_id': 'opp_spr'});
        updateBalls();
    }
    // New pokemon
    if ((isPlayerOne && animMove == 'p1_appear') || (!isPlayerOne && animMove == 'p2_appear')) {
        reappear({'x': '20', 'y': '130', 'div_id': 'player_spr'});
    } else if ((!isPlayerOne && animMove == 'p1_appear') || (isPlayerOne && animMove == 'p2_appear')) {
        reappear({'x': '350', 'y': '60', 'div_id': 'opp_spr'});
    }
    // Sprite changes
    if ((isPlayerOne && animMove == 'p1_new_sprite') || (!isPlayerOne && animMove == 'p2_new_sprite')) {
        updateCanvas({'forPlayer': true, 'usePrevState': true});
        prevState = battleState;
    } else if ((!isPlayerOne && animMove == 'p1_new_sprite') || (isPlayerOne && animMove == 'p2_new_sprite')) {
        updateCanvas({'forPlayer': false, 'usePrevState': true});
        prevState = battleState;
    }
    // HP changes
    if ((isPlayerOne && animMove.startsWith('p1_update_hp_')) || (!isPlayerOne && animMove.startsWith('p2_update_hp_'))) {
        let newHp = animMove.split("_update_hp_")[1];
        updateCanvas({'forPlayer': true, 'justHp': true, 'usePrevPokemon': true, 'newHp': newHp});
    } else if ((!isPlayerOne && animMove.startsWith('p1_update_hp_')) || (isPlayerOne && animMove.startsWith('p2_update_hp_'))) {
        let newHp = animMove.split("_update_hp_")[1];
        updateCanvas({'forPlayer': false, 'justHp': true, 'usePrevPokemon': true, 'newHp': newHp});
    }
}

function attack({x, y, div_id}) {
    const sprite = document.getElementById(div_id);
    const splat = document.getElementById(div_id.replace('spr', 'splat'));

    const originalPosition = {
        x: sprite.getAttribute('data-ox'),
        y: sprite.getAttribute('data-oy')
    };

    sprite.style.transition = `all ${interval / 1000 * 0.4}s ease-in`;
    sprite.style.left = `${x}px`;
    sprite.style.top = `${y}px`;
    splat.style.transition = `all ${interval / 1000 * 0.2}s linear`;

    setTimeout(() => {
        splat.style.opacity = 1;
    }, 0.15 * interval);

    setTimeout(() => {
        splat.style.opacity = 0;
    }, 0.3 * interval);

    setTimeout(() => {
        sprite.style.transition = `all ${interval / 1000 * 0.4}s ease-out`;
        sprite.style.left = `${originalPosition.x}px`;
        sprite.style.top = `${originalPosition.y}px`;
    }, 0.4 * interval);
}

function wiggle({div_id}) {
    const sprite = document.getElementById(div_id);

    const originalPosition = {
        x: sprite.getAttribute('data-ox'),
        y: sprite.getAttribute('data-oy')
    };

    sprite.style.transition = `all ${interval / 1000 * 0.3}s ease`;
    sprite.style.left = `${Number(originalPosition.x) - 20}px`;

    setTimeout(() => {
        sprite.style.left = `${Number(originalPosition.x) + 20}px`;
    }, 0.1 * interval);

    setTimeout(() => {
        sprite.style.left = `${Number(originalPosition.x) - 20}px`;
    }, 0.3 * interval);

    setTimeout(() => {
        sprite.style.left = `${originalPosition.x}px`;
    }, 0.5 * interval);
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
        x: sprite.getAttribute('data-ox'),
        y: sprite.getAttribute('data-oy')
    };

    sprite.style.transition = `all ${interval / 1000 * 0.8}s ease`;
    sprite.style.left = `${x}px`;
    sprite.style.top = `${y}px`;
    sprite.style.opacity = 0.0

    setTimeout(() => {
        sprite.style.left = `${originalPosition.x}px`;
        sprite.style.top = `${originalPosition.y}px`;
    }, interval * 0.8);
}

function reappear({x, y, div_id}) {
    const sprite = document.getElementById(div_id);

    const originalPosition = {
        x: sprite.getAttribute('data-ox'),
        y: sprite.getAttribute('data-oy')
    };

    sprite.style.transition = null;
    sprite.style.left = `${x}px`;
    sprite.style.top = `${y}px`;
    sprite.style.opacity = 0.0


    setTimeout(() => {
        sprite.style.transition = `all ${interval / 1000 * 0.8}s ease`;
        sprite.style.left = `${originalPosition.x}px`;
        sprite.style.top = `${originalPosition.y}px`;
        sprite.style.opacity = 1.0
    }, 0.1 * interval);
}

function sendMove({ action, move = null, item = null, target = null}) {
    if (action == null) {
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
            moveButton.children[0].innerHTML = "No move learned";
            moveButton.children[2].src = "";
            moveButton.children[3].src = "";
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
            moveButton.children[2].src = categoryPath + "/" + moveInfo["damage_class"] + ".png";
            moveButton.children[3].src = typePath + "/" + moveInfo["type"] + ".png";
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
    switchPane.innerHTML = '<p>Choose a Pokémon:</p>';
    party.forEach(function (pkmn, i) {
        const switchButton = document.createElement('button');
        switchButton.classList.add("button-3");
        switchButton.classList.add("battler");
        switchButton.style.height = '40px';
        switchButton.style.width = '40px';
        switchButton.style.margin = '4px';
        const pkmnIcon = document.createElement("img");
        pkmnIcon.src = iconPath + "/" + pkmn["dex_number"].toString().padStart(3, '0') + ".gif";
        pkmnIcon.style.filter = (pkmn.current_hp < 1) ? 'grayscale(90%)' : 'none';
        switchButton.append(pkmnIcon);
        if (i == battleState[player]["current_pokemon"]) {
            // Pokemon is currently out
            switchButton.disabled = true;
        } else if (pkmn["current_hp"] < 1) {
            // Pokemon is knocked out
            switchButton.disabled = true;
        } else {
            // Can be switched to
            switchButton.disabled = !buttonsActive;
            switchButton.onclick = function () {
                sendMove({"action": "switch", "target": i});
                openTab('control-tab', 'select');
            };
        }
        switchPane.append(switchButton);
    });
    const backButton = document.createElement('button');
    backButton.classList.add("button-3");
    backButton.classList.add("button-back");
    backButton.innerHTML = 'Back';
    backButton.onclick = function () {openTab('control-tab', 'select')};
    switchPane.append(document.createElement('br'));
    switchPane.append(document.createElement('br'));
    switchPane.append(backButton);
}

function updateSelector() {
    // Function to update the item tab and target selector pane
    const player = (isPlayerOne) ? 'player_1' : 'player_2';
    const party = battleState[player]['party'];
    // Update target select
    const targetSelector = document.getElementById('item_target_select');
    targetSelector.innerHTML = '<span>Use item on</span>';
    // Show the image of item being used
    const selectedItemImg = document.createElement('img');
    selectedItemImg.src = itemPath + "/" + selectedItem + ".png";
    targetSelector.append(selectedItemImg);
    targetSelector.append(document.createElement('br'));
    // Show the party buttons
    party.forEach(function (pkmn, i) {
        const targetButton = document.createElement('div');
        targetButton.classList.add("button-3");
        targetButton.classList.add("battler");
        targetButton.style.height = '40px';
        targetButton.style.width = '40px';
        targetButton.style.margin = '4px';
        targetButton.onclick = function () {
            if (selectedItem != null) {
                sendMove({"action": "item", "item": selectedItem, "target": i});
            } else {
                document.querySelector('#chat-log').value += ('Select an item first!\n');
                document.querySelector('#chat-log').scrollTop = document.querySelector('#chat-log').scrollHeight;
            }
            targetSelector.style.display = 'none';
            openTab('control-tab', 'select');
        };
        const pkmnIcon = document.createElement("img");
        pkmnIcon.src = iconPath + "/" + pkmn["dex_number"].toString().padStart(3, '0') + ".gif";
        // Grayscale if Pokemon is fainted
        pkmnIcon.style.filter = (pkmn.current_hp < 1) ? 'grayscale(90%)' : 'none';
        targetButton.append(pkmnIcon);
        targetSelector.append(targetButton);
    });
    // Add back button to target selector
    const backButton = document.createElement('button');
    backButton.classList.add("button-3");
    backButton.classList.add("button-back");
    backButton.innerHTML = 'Back';
    backButton.onclick = function () {openTab('control-tab', 'items')};
    targetSelector.append(document.createElement('br'));
    targetSelector.append(backButton);
}

function updateInventory() {
    // Function to update the item tab and target selector pane
    const player = (isPlayerOne) ? 'player_1' : 'player_2';
    const inventory = battleState[player]['inventory'];
    // Update item select portion
    const invControls = document.getElementById('switch');
    let validItems = [];
    // Get the valid items
    if (ballsAllowed)
        validItems.push('ball');
    if (medicinesAllowed)
        validItems.push('medicine');
    // Update each item group
    validItems.forEach((itemClass) => {
        const itemGroup = document.getElementById(itemClass);
        itemGroup.innerHTML = '';
        for (const [item, quantity] of Object.entries(inventory[itemClass])) {
            if (quantity > 0) {
                // Add item when quantity exists
                const itemButton = document.createElement('button');
                itemButton.classList.add("button-3");
                itemButton.classList.add("battler");
                if (itemClass == 'ball') {
                    itemButton.onclick = function () {
                        sendMove({"action": "item", "item": item});
                        openTab('control-tab', 'select');
                    };
                } else {
                    itemButton.onclick = function () {
                        selectedItem = item;
                        updateSelector();
                        openTab('control-tab', 'item_target_select');
                    };
                }
                itemButton.style.height = '35px';
                itemButton.style.width = '80px';
                const itemImg = document.createElement('img')
                itemImg.src = itemPath + "/" + item + ".png";
                itemButton.append(itemImg);
                itemButton.append(` x${quantity}`);
                itemGroup.append(itemButton);
            }
        }
    })
}

function updateCanvas({forPlayer, justHp = false, usePrevPokemon = false, usePrevState = false, newHp = null}) {
    // usePrev is just for previous Pokemon, current state still used
    let player = "player_2";
    let opp = "player_1";
    if (isPlayerOne) {
        player = "player_1";
        opp = "player_2"
    }
    let partyState = battleState;
    let statusState = battleState
    if (usePrevPokemon)
        partyState = prevState;
    if (usePrevState)
        statusState = prevState;
    if (forPlayer) {
        // Update icon
        const playerPokemon = statusState[player]["party"][partyState[player]["current_pokemon"]]
        const playerSpr = document.getElementById("player_spr");
        if (!justHp)
            playerSpr.src = backPath + "/" + playerPokemon["dex_number"].toString().padStart(3, '0') + ".png";
        // Update status
        const playerStatus = document.getElementById("player_status");
        if (playerPokemon["status"] != "") {
            playerStatus.src = statusPath + "/" + playerPokemon["status"] + ".png";
        } else {
            playerStatus.src = "";
        }
        // Update info bar
        const playerInfo = document.getElementById("player_name");
        let playerHpVal = (newHp == null)? playerPokemon["current_hp"] : newHp;
        playerInfo.innerHTML = 'Lv. ' + playerPokemon["level"] + ' ' + playerPokemon["name"] + " " + playerHpVal + "/" + playerPokemon["stats"]["hp"];
        // Update HP bar
        const playerHp = document.getElementById("player_hp");
        playerHp.style.transition = `all ${interval / 1000}s ease-out`;
        const hpPercentage = playerHpVal / playerPokemon["stats"]["hp"] * 100;
        playerHp.style.width = `${hpPercentage}%`;

    } else {
        // Update icon
        const oppPokemon = statusState[opp]["party"][partyState[opp]["current_pokemon"]]
        const oppSpr = document.getElementById("opp_spr");
        if (!justHp)
            oppSpr.src = frontPath + "/" + oppPokemon["dex_number"].toString().padStart(3, '0') + ".png";
        // Update status
        const oppStatus = document.getElementById("opp_status");
        if (oppPokemon["status"] != "") {
            oppStatus.src = statusPath + "/" + oppPokemon["status"] + ".png";
        } else {
            oppStatus.src = "";
        }
        // Update info bar
        const oppInfo = document.getElementById("opp_name");
        let oppHpVal = (newHp == null)? oppPokemon["current_hp"] : newHp;
        oppInfo.innerHTML = 'Lv. ' + oppPokemon["level"] + ' ' + oppPokemon["name"] + " " + oppHpVal + "/" + oppPokemon["stats"]["hp"];
        // Update HP bar
        const oppHp = document.getElementById("opp_hp");
        oppHp.style.transition = `all ${interval / 1000}s ease-out`;
        const hpPercentage = oppHpVal / oppPokemon["stats"]["hp"] * 100;
        oppHp.style.width = `${hpPercentage}%`;

    }
}

function updateBalls() {
    const player = (isPlayerOne) ? 'player_1' : 'player_2';
    const opp = (isPlayerOne) ? 'player_2' : 'player_1';
    const playerBalls = document.getElementById('player_balls');
    const oppBalls = document.getElementById('opp_balls');
    playerBalls.innerHTML = '';
    oppBalls.innerHTML = '';
    // fill player party
    for (let i = 0; i < battleState[player]['party'].length; i++) {
        const pokeBall = document.createElement('img');
        const pkmn = battleState[player]['party'][i]
        pokeBall.style.filter = (pkmn.current_hp < 1) ? 'grayscale(100%)' : 'none';
        pokeBall.src = miscPath + "/ballicon.png";
        playerBalls.append(pokeBall);
    }
    // fill opp party
    for (let i = 0; i < battleState[opp]['party'].length; i++) {
        const pokeBall = document.createElement('img');
        const pkmn = battleState[opp]['party'][i]
        pokeBall.style.filter = (pkmn.current_hp < 1) ? 'grayscale(100%)' : 'none';
        pokeBall.src = miscPath + "/ballicon.png";
        oppBalls.append(pokeBall);
    }
}

function battleStart() {
    let loadAnim = [{}];

    let player = (isPlayerOne) ? "player_1" : "player_2";
    let opp = (isPlayerOne) ? "player_2" : "player_1";

    const playerName = document.getElementById("player_name");
    playerName.innerHTML = battleState[player]['name'];

    const oppPokemon = battleState[opp]["party"][battleState[opp]["current_pokemon"]]
    const playerPokemon = battleState[player]["party"][battleState[player]["current_pokemon"]]

    const playerSpr = document.getElementById("player_spr");
    playerSpr.src = playerTrainer;
    playerSpr.style.top = '142px';

    if (battleType == 'wild') {
        loadAnim.push({'text': 'A ' + battleState['player_2']['name'] + ' appeared!'});
    } else {
        const oppName = document.getElementById("opp_name");
        oppName.innerHTML = battleState[opp]['name'];
        const oppSpr = document.getElementById("opp_spr");
        oppSpr.src = oppTrainer;
        loadAnim.push({'text': battleState[opp]['name'] + ' wants to battle!'});
        loadAnim.push({'anim': ['p2_retreat']});
        loadAnim.push({'text': battleState[opp]['name'] + ' sent out ' + oppPokemon['name'] +'!', 'anim': ['p2_new_sprite', 'p2_appear']});
    }
    loadAnim.push({'text': 'Go, ' + playerPokemon['name'] + '!', "anim": ["trainer_retreat"]});
    loadAnim.push({'anim': ['p1_new_sprite', 'p1_appear']})
    loadAnim.push({"anim": ["turnEnd"]});
    let promise = Promise.resolve();
    loadAnim.forEach(function (out) {
        promise = promise.then(function() {
            processOutput(out);
            return new Promise(function (resolve) {
                setTimeout(resolve, interval);
            })
        });
    })
}

updateMoves();
updateSwitches();
updateInventory();
updateCanvas({'forPlayer': true});
updateCanvas({'forPlayer': false});
updateBalls();
toggleButtons(false);
if (initialTurn == 1) {
    battleStart();
} else {
    toggleButtons(true);
}