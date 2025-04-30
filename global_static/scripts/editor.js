

class NPC {
    constructor(position) {
        this.name = 'NPC'; // Name of the NPC
        this.dialogue = 'Battle start dialogue'; // Dialogue text of the NPC
        this.loss = 'Battle loss dialogue';
        this.trainer_sprite = 'picnicker_m'; // The sprite of the NPC
        this.pokemon_sprite = '001';
        this.isPokemon = false; // Boolean indicating if the NPC is a Pokemon
        this.wanderPoints = [{"x": position.x, "y": position.y, "dir": "down"}]; // List of wander points (array of {x, y, direction})
        this.team = []; // List of team members (Pokémon or NPC objects)
        this.mapSprite = []; // pointer to sprite
        this.bg = null;

        this.fast = false;
        this.flying = false;
        this.alwaysMoving = false;
    }

    fromJson(data) {
        this.name = data["map"]["name"]
        this.dialogue = data["map"]["dialogue"]
        if ("type" in data["map"]) {
            this.isPokemon = true;
            this.pokemon_sprite = data["map"]["sprite"];
        } else {
            this.trainer_sprite = data["map"]["sprite"];
        }

        if ("alwaysMoving" in data["map"]) this.alwaysMoving = true;
        if ("fast" in data["map"]) this.fast = true;
        if ("flying" in data["map"]) this.flying = true;
        let new_points = [];
        data["map"]["wander_points"].forEach((point) => {
            new_points.push({'x': point.x + 1, 'y': point.y + 1, 'dir': point.dir})
        })
        this.wanderPoints = new_points;

        // Check if there is a gen
        if ("gen" in data) {
            this.team = data["gen"]["team"]
            this.loss = data["gen"]["lose"]
            this.bg = data["gen"]["bg"]
        }
    }

    exportJson() {
        if (!this.isValidWanderPoints()) {
            throw new Error(`Wander points are not valid on ${this.name}`)
        }
        const whichSprite = (this.isPokemon) ? this.pokemon_sprite : this.trainer_sprite;
        // Only generate battle if team is not empty
        let res = {
            "map": {
                "name": this.name,
                "sprite": whichSprite,
                "dialogue": this.dialogue,
                "wander_points": this.wanderPoints
            }
        }
        let new_points = [];
        this.wanderPoints.forEach((point) => {
            new_points.push({'x': point.x - 1, 'y': point.y - 1, 'dir': point.dir})
        })
        res["map"]["wander_points"] = new_points;
        if (this.isPokemon) {
            res["map"]["type"] = "pokemon";
        }
        if (this.flying) {
            res["map"]["flying"] = true;
        }
        if (this.alwaysMoving) {
            res["map"]["alwaysMoving"] = true;
        }
        if (this.fast) {
            res["map"]["fast"] = true;
        }
        if (this.team.length > 0) {
            let battle_name = `${mapName}_${this.name.replace(/\s+/g, '-').toLowerCase()}`
            let battle_info = {
                "name": this.name,
                "file": battle_name,
                "team": this.team,
                "sprite": whichSprite,
                "lose": this.loss
            }
            if (this.bg) {
                battle_info["bg"] = this.bg;
            }
            res["gen"] = battle_info
            res["map"]["battle"] = battle_name
        }
        return res

    }

    // Method to add a wander point
    addWanderPoint(x, y, direction) {
        this.wanderPoints.push({ x, y, direction });
    }

    render(parent) {
        // Get the path
        const spritePath = (this.isPokemon) ? pkmnPath : trainerPath;
        const whichSprite = (this.isPokemon) ? this.pokemon_sprite : this.trainer_sprite
        const fullPath = spritePath + whichSprite + '.png';
        this.mapSprite = [];
        // Create the image
        this.wanderPoints.forEach((point) => {
            const mapSprite = document.createElement('img');
            mapSprite.src = fullPath;
            mapSprite.style.position = 'absolute';
            mapSprite.style.opacity = '0.6';
            mapSprite.style.objectFit = "none";  // Prevent scaling
            mapSprite.style.objectPosition = "0% 0%";
            let yOffset = 0;
            switch (point.dir) {
                case 'left':
                    mapSprite.style.clipPath = "inset(25% 75% 50% 0)";
                    yOffset = 32 * 1;
                    break;
                case 'right':
                    mapSprite.style.clipPath = "inset(50% 75% 25% 0)";
                    yOffset = 32 * 2;
                    break;
                case 'up':
                    mapSprite.style.clipPath = "inset(75% 75% 0 0)";
                    yOffset = 32 * 3;
                    break;
                case 'down':
                    mapSprite.style.clipPath = "inset(0 75% 75% 0)";
                    break;
            }
            mapSprite.style.left = `${point.x * 16 - 8}px`;
            mapSprite.style.top = `${point.y * 16 - 12 - yOffset}px`;
            this.mapSprite.push(mapSprite);
            parent.append(mapSprite)
        })


        // Add it to the map
    }

    // Method to check if the wander points are valid
    isValidWanderPoints() {
        if (this.wanderPoints.length == 1) return true;
        for (let i = 0; i < this.wanderPoints.length; i++) {
            const current = this.wanderPoints[i];
            const next = this.wanderPoints[(i + 1) % this.wanderPoints.length]; // Wrap around to the first point

            if (!this.isValidDirection(current, next)) {
                return false; // Invalid direction or mismatch between points
            }
        }
        return true; // All wander points are valid
    }

    // Helper function to validate direction
    isValidDirection(current, next) {
        const xDiff = next.x - current.x;
        const yDiff = next.y - current.y;

        switch (current.dir) {
            case 'left':
                console.log(xDiff);
                return yDiff === 0 && xDiff < 0; // Moving left should decrease x
            case 'right':
                console.log(xDiff);
                return yDiff === 0 && xDiff > 0; // Moving right should increase x
            case 'up':
                console.log(yDiff);
                return xDiff === 0 && yDiff < 0; // Moving up should decrease y
            case 'down':
                console.log(yDiff);
                return xDiff === 0 && yDiff > 0; // Moving down should increase y
            default:
                console.log("edge case");
                console.log(current.dir);
                return false;
        }
    }
}

// Get various elements
const map = document.getElementById("map");
const highlight = document.getElementById("highlight");
const addCharacterBtn = document.getElementById("add_npc");
const npcList = document.getElementById("npcs");

// Constants
const trainerPath = '/static/assets/npc/overworld/';
const pkmnPath = '/static/assets/pokemon/overworld/';

// State vars
let npcs = [];
let addMode = false;
let addingPoint = false;
let charIdx = null;

prevData.forEach((npc) => {
    const npc_obj = new NPC({"x": 0, "y": 0});
    npc_obj.fromJson(npc);
    npcs.push(npc_obj);
})
renderMap();
renderSidebar();

addCharacterBtn.addEventListener("click", () => {
    addMode = true;
});

map.addEventListener("mousemove", (e) => {
    if (!addMode) return;

    const rect = map.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left + map.scrollLeft) / 16);
    const y = Math.floor((e.clientY - rect.top + map.scrollTop) / 16);

    highlight.style.left = `${x * 16 - 8}px`;
    highlight.style.top = `${y * 16 - 12}px`;
    highlight.style.objectFit = "none";  // Prevent scaling
    highlight.style.objectPosition = "0% 0%"; // Show top-left
    highlight.style.clipPath = "inset(0 75% 75% 0)";
    highlight.style.display = "block";
});

map.addEventListener("mouseleave", () => {
    highlight.style.display = "none";
});

map.addEventListener("click", (e) => {
    if (!addMode) return;

    const rect = map.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left + map.scrollLeft) / 16);
    const y = Math.floor((e.clientY - rect.top + map.scrollTop) / 16);

    //const character = { x, y };
    if (addingPoint && charIdx != null) {
        // TODO sanity check; only allow push on same axis
        npcs[charIdx].wanderPoints.push({x: x, y: y, dir: "down"})
        addingPoint = false;
        charIdx = null;
    } else {
        const character = new NPC({"x": x, "y": y})
        npcs.push(character);
    }
    renderMap();
    renderSidebar();
    addMode = false;
    highlight.style.display = "none";
});

// Functions for binding fields to classes
function bindInput(inputId, instance, property) {
    const input = document.getElementById(inputId);
    if (!input) return;

    if (input.type == 'checkbox') {
        input.addEventListener("input", () => {
            instance[property] = input.checked;
        });
        input.checked = instance[property];

    } else {
        input.addEventListener("input", () => {
            instance[property] = input.value;
        });
        input.value = instance[property];
    }
}

function createSelect(optionsList, selectId, selected = null) {
    const select = document.createElement("select");
    if (selectId) select.id = selectId; // Optional ID
    let to_select = null;
    optionsList.forEach((optionValue) => {
        const option = document.createElement("option");
        option.value = optionValue[0];
        option.textContent = optionValue[1];
        if (option.value == selected) {
            to_select = option.value;
        }
        select.appendChild(option);
    });
    if (to_select) select.value = to_select;

    return select;
}

function renderMap() {
    const keepIds = ['highlight', 'mapImg'];
    Array.from(map.children).forEach(child => {
        if (!keepIds.includes(child.id)) {
            map.removeChild(child);
        }
    });
    npcs.forEach(function (character) {
        character.render(map);
    })
}

function renderSidebar() {
    npcList.innerHTML = '';
    npcs.forEach(function (character, i) {
        const charTab = document.createElement('div');
        charTab.id = `${i}_npc`;
        charTab.style.border = '1px solid black';
        charTab.style.padding = '5px';
        charTab.classList.add('char_class');

        // Field to edit name
        const nameInput = document.createElement('input');
        nameInput.value = character.name;
        nameInput.id = `${i}_name`;
        nameInput.addEventListener("mouseenter", () => highlightCharacter(i));
        nameInput.addEventListener("mouseleave", () => removeHighlight());
        charTab.append(nameInput);

        // Fields to edit dialogue
        const dialogueInput = document.createElement('input');
        dialogueInput.value = character.dialogue;
        dialogueInput.id = `${i}_dialogue`;
        charTab.append(dialogueInput);

        const lossInput = document.createElement('input');
        lossInput.value = character.loss;
        lossInput.id = `${i}_loss`;
        charTab.append(lossInput);

        // Field to check pokemon box; onchange, switch lists
        const isPokemonInput = document.createElement('input')
        isPokemonInput.type = "checkbox";
        isPokemonInput.value = character.isPokemon;
        isPokemonInput.id = `${i}_pkmn`;
        isPokemonInput.addEventListener("change", renderMap);
        charTab.append(document.createTextNode("Pokemon?"));
        charTab.append(isPokemonInput);

        const isFast = document.createElement('input')
        isFast.type = "checkbox";
        isFast.value = character.fast;
        isFast.id = `${i}_fast`;
        isFast.addEventListener("change", renderMap);
        charTab.append(document.createTextNode("Fast?"));
        charTab.append(isFast);

        const isMoving = document.createElement('input');
        isMoving.type = "checkbox";
        isMoving.value = character.alwaysMoving;
        isMoving.id = `${i}_moving`;
        isMoving.addEventListener("change", renderMap);
        charTab.append(document.createTextNode("Moving?"));
        charTab.append(isMoving);

        const isFlying = document.createElement('input');
        isFlying.type = "checkbox";
        isFlying.value = character.flying;
        isFlying.id = `${i}_flying`;
        isFlying.addEventListener("change", renderMap);
        charTab.append(document.createTextNode("Flying?"));
        charTab.append(isFlying);

        const amFast = document.createElement('input');
        amFast.type = "checkbox";
        amFast.value = character.fast;
        amFast.id = `${i}_faster`;
        amFast.addEventListener("change", renderMap);
        charTab.append(document.createTextNode("Fasttt?"));
        charTab.append(amFast);

        // Field to select sprite
        const trainerSprites = createSelect(trainers, `${i}_trainersprites`)
        const pokemonSprites = createSelect(pokemon, `${i}_pokesprites`)
        trainerSprites.addEventListener("change", renderMap);
        pokemonSprites.addEventListener("change", renderMap);
        charTab.append(trainerSprites);
        charTab.append(pokemonSprites);
        // BG select
        const bgs = [
            ["beach", "beach"], ["brown_cave", "brown_cave"], ["mountain", "mountain"],
            ["default", "default"], ["desert", "desert"],
            ["grass", "grass"], ["gray_cave", "gray_cave"],
            ["pond", "pond"], ["snow", "snow"],
            ["volcano", "volcano"], ["water", "water"]];
        const bgSelect = createSelect(bgs, `${i}_bgselect`, "grass");
        isMoving.value = "grass"
        charTab.append(bgSelect);

        // Field to add wander points
        const wanderSection = document.createElement('div');
        character.wanderPoints.forEach((point, idx) => {
            const wanderPointTab = document.createElement('div');
            const xInput = document.createElement('input');
            xInput.value = point.x;
            xInput.id = `${i}_wander_${idx}_x`;
            xInput.addEventListener("change", () => {
                point.x = parseInt(xInput.value);
                renderMap();
            });

            const yInput = document.createElement('input');
            yInput.value = point.y;
            yInput.id = `${i}_wander_${idx}_y`;
            yInput.addEventListener("change", () => {
                point.y = parseInt(yInput.value);
                renderMap();
            });

            const directionInput = createSelect([["right", "right"], ["left", "left"], ["up", "up"], ["down", "down"]], `${i}_wander_${idx}_dir`, point.dir);
            //document.createElement('input');
            //directionInput.value = point.dir;
            //directionInput.id = `${i}_wander_${idx}_dir`;
            directionInput.addEventListener("change", () => {
                point.dir = directionInput.value;
                renderMap();
            });

            wanderPointTab.append(xInput);
            wanderPointTab.append(yInput);
            wanderPointTab.append(directionInput);

            // Delete Button for Wander Point
            const deleteWanderButton = document.createElement('button');
            deleteWanderButton.textContent = 'Delete';
            deleteWanderButton.addEventListener('click', () => {
                character.wanderPoints.splice(idx, 1);  // Remove wander point
                renderSidebar();  // Re-render the sidebar to reflect the update
                renderMap();
            });
            wanderPointTab.append(deleteWanderButton);
            wanderPointTab.addEventListener("mouseenter", () => highlightPoint(i, idx));
            wanderPointTab.addEventListener("mouseleave", () => removeHighlight());

            wanderSection.appendChild(wanderPointTab);
        })
        // Add New Wander Point
        const addWanderButton = document.createElement('button');
        addWanderButton.textContent = 'Add Wander Point';
        addWanderButton.addEventListener("click", () => {
            addMode = true;
            addingPoint = true;
            charIdx = i;
        });
        // Add Sanity Check
        const addWanderCheck = document.createElement('button');
        addWanderCheck.textContent = 'Check Wander Points';
        addWanderCheck.addEventListener("click", () => {
            if (character.isValidWanderPoints()) {
                console.log("Valid")
            } else {
                console.log("Not valid")
            }
        });
        charTab.appendChild(document.createElement('br'))
        charTab.appendChild(document.createTextNode("wander"));
        wanderSection.appendChild(addWanderButton);
        wanderSection.appendChild(addWanderCheck);
        charTab.appendChild(wanderSection);


        // Field to create team
        const teamSection = document.createElement('div');
        character.team.forEach((member, idx) => {
            const teamMemberTab = document.createElement('div');

            const dexInput = createSelect(pokemon, `${i}_team_${idx}_dex`, member.dex);
            dexInput.addEventListener("change", () => {
                member.dex = dexInput.value;
            });

            const levelInput = document.createElement('input');
            levelInput.type = "number";
            levelInput.value = member.level;
            levelInput.id = `${i}_team_${idx}_level`;
            levelInput.addEventListener("change", () => {
                member.level = parseInt(levelInput.value);
            });

            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', () => {
                character.team.splice(idx, 1);
                renderSidebar();
            })

            teamMemberTab.append(dexInput);
            teamMemberTab.append(levelInput);
            teamMemberTab.append(deleteButton);
            teamSection.append(teamMemberTab);
        })
        const addTeamButton = document.createElement('button');
        addTeamButton.textContent = 'Add Team Member';
        addTeamButton.addEventListener('click', () => {
            character.team.push({ dex: '001', level: 5 });  // Add new member with default values
            renderSidebar();  // Re-render the sidebar to reflect the update
        });
        charTab.appendChild(document.createElement('br'))
        charTab.appendChild(document.createTextNode("team"));
        teamSection.appendChild(addTeamButton);
        charTab.appendChild(teamSection);

        // Del button
        const removeBtn = document.createElement("span");
        removeBtn.textContent = "x";
        removeBtn.classList.add("remove-btn");
        removeBtn.addEventListener("click", (e) => {
            npcs.splice(i, 1);
            renderSidebar();
            renderMap();
            e.stopPropagation();
        });
        charTab.append(removeBtn);

        // Bind all inputs
        npcList.append(charTab)
        bindInput(nameInput.id, character, 'name');
        bindInput(dialogueInput.id, character, 'dialogue');
        bindInput(lossInput.id, character, 'loss');
        bindInput(isPokemonInput.id, character, 'isPokemon');
        //bindInput(isFast.id, character, 'fast');
        bindInput(isMoving.id, character, 'alwaysMoving');
        bindInput(amFast.id, character, 'fast');
        bindInput(isFlying.id, character, 'flying');
        bindInput(trainerSprites.id, character, 'trainer_sprite');
        bindInput(pokemonSprites.id, character, 'pokemon_sprite');
        bindInput(bgSelect.id, character, 'bg');
    })
}

// Highlights
function highlightCharacter(index) {
    npcs[index].mapSprite.forEach((spr) => {
        spr.style.filter = "brightness(1.3)";
    })
}
function highlightPoint(index, pt) {
    npcs[index].mapSprite[pt].style.filter = "brightness(1.3)";
}

function removeHighlight() {
    npcs.forEach((char) => {
        char.mapSprite.forEach((spr) => {
            spr.style.filter = "brightness(1)";
        })
    });
}

function hasDuplicateNames(instances) {
    const seenNames = new Set();
    for (const instance of instances) {
        if (seenNames.has(instance.name)) {
            return true; // Duplicate found
        }
        seenNames.add(instance.name);
    }
    return false; // No duplicates
}

function exportJsons() {


    let res = JSON.stringify(npcs.map((x) => x.exportJson()));
    document.getElementById("npc_data").value = res;
    document.getElementById("preview").innerHTML = res;
}