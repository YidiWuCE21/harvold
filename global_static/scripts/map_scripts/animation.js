// Constant to help with player movement during animation
let animatePlayer = {
    "w": {
        "row": 2,
        "offset": {x: 0, y: movespeed},
        "ledge": 99,
        "direction": "north"
    },
    "a": {
        "row": 1,
        "offset": {x: movespeed, y: 0},
        "ledge": 3,
        "direction": "west"
    },
    "s": {
        "row": 0,
        "offset": {x: 0, y: -movespeed},
        "ledge": 2,
        "direction": "south"
    },
    "d": {
        "row": 3,
        "offset": {x: -movespeed, y: 0},
        "ledge": 4,
        "direction": "east"
    }
};


function applyFilter() {
    switch (timeOfDay) {
        case "night":
            c.fillStyle = 'rgba(5, 0, 40, 0.5)';
            break;
        case "morning":
            c.fillStyle = 'rgba(50, 50, 10, 0.3)';
            break;
        case "evening":
            c.fillStyle = 'rgba(70, 30, 0, 0.2)';
            break;
        default:
            c.fillStyle = 'rgba(0, 0, 0, 0)';
    }
    c.fillRect(0, 0, canvas.width, canvas.height);
}

let start, now, then, elapsed;
const fpsInterval = 20;
then = Date.now();
start = then;

function animate(looped = true) {
    // Check for loop
    if (looped) {
        //setTimeout(() => {requestAnimationFrame(animate);}, 1000 / 60);
        window.requestAnimationFrame(animate);
    }

    // Cap FPS
    now = Date.now();
    elapsed = now - then;
    if (elapsed > fpsInterval) {
        // Increment game tick
        gameTick += 1;
        trainerTick();
        if (gameTick == 100) {
            gameTick = 0;
        }
        // Check sprint
        if (keys.shift.pressed) {
            movespeed = 4;
        } else {
            movespeed = 2;
        }
        // Get camera
        let cappedCamera = {
            x: Math.min(Math.max(camera.position.x, 0), mapWidth * tileWidth - canvas.width),
            y: Math.min(Math.max(camera.position.y, 0), mapHeight * tileWidth - canvas.height)
        }
        // Order game sprites
        let orderedSprites = [...mapTrainersSprites];
        if (surfing) {
            orderedSprites.push(surf);
            orderedSprites.push(surfer);
        } else {
            orderedSprites.push(player);
        }
        let zCompare = (a, b) => {
            if (a.flying && !b.flying) {
                return 1;
            }
            if (!a.flying && b.flying) {
                return -1;
            }
            if (a.position.y < b.position.y) {
                return -1;
            }
            if (a.position.y < b.position.y) {
                return 1;
            }
            return 0;
        };
        orderedSprites.sort(zCompare);
        // Split flying and non flying
        let [flyingSprites, nonFlyingSprites] = orderedSprites.reduce(
            (acc, creature) => {
                acc[creature.flying ? 0 : 1].push(creature);
                return acc;
            },
            [[], []] // Initialize with two empty arrays
        );
        orderedSprites = nonFlyingSprites;


        // Flip surf and surfer
        let surfIdx = orderedSprites.indexOf(surf);
        let surferIdx = orderedSprites.indexOf(surfer);
        orderedSprites[surferIdx] = surf;
        orderedSprites[surfIdx] = surfer;
        // Check for map transition
        if (mapLoad) {
            player.moving = true;
            if (background)
                background.draw(cappedCamera);

            // Draw trainers in order
            for (let i = 0; i < orderedSprites.length; i++) {
                const currentSprite = orderedSprites[i];
                currentSprite.draw(cappedCamera);
            }
            switch(travelDir) {
                case "in":
                    statics.forEach(movable => {movable.rows.val = 2});
                    break;
                case "out":
                    statics.forEach(movable => {movable.rows.val = 0});
                    break;
                case "north":
                    statics.forEach(movable => {movable.position.y -= movespeed});
                    nonCameraStatics.forEach(movable => {movable.rows.val = 2});
                    break;
                case "south":
                    statics.forEach(movable => {movable.position.y += movespeed});
                    nonCameraStatics.forEach(movable => {movable.rows.val = 0});
                    break;
                case "east":
                    statics.forEach(movable => {movable.position.x += movespeed});
                    nonCameraStatics.forEach(movable => {movable.rows.val = 3});
                    break;
                case "west":
                    statics.forEach(movable => {movable.position.x -= movespeed});
                    nonCameraStatics.forEach(movable => {movable.rows.val = 1});
                    break;
            }
            foreground.draw(cappedCamera);

            // Draw flying sprites in order
            for (let i = 0; i < flyingSprites.length; i++) {
                const currentSprite = flyingSprites[i];
                currentSprite.draw(cappedCamera);
            }
            // applyFilter();
            return;
        }
        if (ledgeActive != null) {
            player.moving = true;
            if (background)
                background.draw(cappedCamera);

            // Draw trainers in order
            for (let i = 0; i < orderedSprites.length; i++) {
                const currentSprite = orderedSprites[i];
                currentSprite.draw(cappedCamera);
            }
            // Jump animation
            if (ledgeFrames > 9) {
                nonCameraStatics.forEach(movable => {movable.position.y -= 2});
            } else if (ledgeFrames < 7) {
                nonCameraStatics.forEach(movable => {movable.position.y += 2});
            }
            switch(ledgeActive) {
                case "in":
                    nonCameraStatics.forEach(movable => {movable.rows.val = 1});
                    break;
                case "north":
                    nonCameraStatics.forEach(movable => {movable.rows.val = 1});
                    break;
                case "south":
                    statics.forEach(movable => {movable.position.y += 2});
                    nonCameraStatics.forEach(movable => {movable.rows.val = 0});
                    break;
                case "east":
                    statics.forEach(movable => {movable.position.x += 2});
                    nonCameraStatics.forEach(movable => {movable.rows.val = 3});
                    break;
                case "west":
                    statics.forEach(movable => {movable.position.x -= 2});
                    nonCameraStatics.forEach(movable => {movable.rows.val = 2});
                    break;
            }
            foreground.draw(cappedCamera);


            // Draw flying sprites in order
            for (let i = 0; i < flyingSprites.length; i++) {
                const currentSprite = flyingSprites[i];
                currentSprite.draw(cappedCamera);
            }
            // applyFilter();
            ledgeFrames -= 1;
            if (ledgeFrames == 0) {
                ledgeFrames = defaultLedgeFrames;
                ledgeActive = null;
            }

            return;
        }
        c.fillStyle = 'black';
        c.fillRect(0, 0, canvas.width, canvas.height);
        background.draw(cappedCamera);
        // Detect maplink nearby
        for (let i = 0; i < maplinkUnpartitioned.length; i++) {
            const maplinkTile = maplinkUnpartitioned[i];
            if (
                inRadius({point1: player.position, point2: maplinkTile.position, radius: 50, offset: 0})
            ) {
                // Set opacity based on distance to player
                const distance = Math.sqrt((player.position.x - maplinkTile.position.x) ** 2 + (player.position.y - maplinkTile.position.y) ** 2)
                const opacity = -1/50 * distance + 1
                c.globalAlpha = opacity;
                maplinkTile.draw(cappedCamera, gameTick);
                c.globalAlpha = 1;
            }
        }

        // Detect if on water
        surfing = false;
        if (!onBridge) {
            let waterTile = detectCollision({
                collidables: waterTiles,
                collisionFunc: pointCollision
            })
            if (waterTile != null) {
                surfing = true;
            }
        }
        // Detect if on battle
        currentArea = null;
        grass = false;
        if (!onBridge) {
            let battleTile = detectCollision({
                collidables: battleTiles,
                collisionFunc: pointCollision
            })
            if (battleTile != null) {
                grass = true;
                currentArea = battleTile.value;
            }
        }
        // Detect if on bridge
        const currentOnBridge = onBridge;
        onBridge = false;
        let bridgeTile = detectCollision({
            collidables: bridgeTiles,
            collisionFunc: pointCollision
        })
        if (bridgeTile != null) {
            if (bridgeTile.value == 2) {
                onBridge = true;
            } else if (bridgeTile.value == 1 && currentOnBridge) {
                onBridge = true;
            } else {
                onBridge = false;
            }
        }
        // Draw trainers in order
        for (let i = 0; i < orderedSprites.length; i++) {
            const currentSprite = orderedSprites[i];
            currentSprite.draw(cappedCamera);
        }
        foreground.draw(cappedCamera);

        // Draw flying sprites in order
        for (let i = 0; i < flyingSprites.length; i++) {
            const currentSprite = flyingSprites[i];
            currentSprite.draw(cappedCamera);
        }
        if (!onBridge && bridgeExists)
            bridgeRender.draw(cappedCamera);
        // Draw speech bubbles after

        for (let i = 0; i < mapTrainersSprites.length; i++) {
            const currentTrainer = mapTrainersSprites[i];
            currentTrainer.exclaim(cappedCamera);
        }

        // Manage enter events
        if (keys.enter.pressed) {
            // Map travel
            if (!stopTravel) {
                let traveling = detectCollision({
                    collidables: maplinkTiles,
                    collisionFunc: pointCollision
                })
                if (traveling != null) {
                    const newMap = maplinkKey[traveling.value];
                    // Play the map travel animation
                    updatePos();
                    player.moving = true;
                    travelDir = traveling.direction;
                    // Use current position to overwrite positional offset
                    if ("posOffset" in newMap) {
                        newMap["playerOffset"] = {};
                        if ("x" in newMap["posOffset"]) {
                            newMap["playerOffset"]["x"] = player.position.x + newMap["posOffset"]["x"] * tileWidth;
                        }
                        if ("y" in newMap["posOffset"]) {
                            newMap["playerOffset"]["y"] = player.position.y + newMap["posOffset"]["y"] * tileWidth;
                        }
                    }
                    mapInit(newMap);
                    stopTravel = true;
                    document.getElementById("wild").style.display = "none";
                    wildHide = null;
                    wildShow = null;
                    wildArea = null;
                }
            }
            if (wildHide != null && !stopTravel) {
                document.wildBattleForm.submit();
            }
        }
        // Also manages enter events but we need to loop this regardless so keep it outside of block
        mapTrainersSprites.forEach((trainer) => {
            if (trainer.solid && !stopTravel) {
                // Trainer battle/dialogue activation
                if (trainer.battle != null && !dialogueActive && keys.enter.pressed) {
                    updatePos();
                    // Play dialogue first
                    document.getElementById("wild").style.display = "none";
                    wildHide = null;
                    dialogueActive = true;
                    // Prepare speaker name and image
                    document.getElementById("speaker_name").innerHTML = trainer.name;
                    document.getElementById("speaker_sprite").src = trainer.image.src;
                    // View dialogue and start writing
                    toggleDialogueWindow({'open': true});
                    writeDialogue(trainer.dialogue);
                    // Go to battle
                    setTimeout(() => {
                        const url = trainerUrl;
                        const form = $('<form action="' + url + '" method="post" style="display:none;">' +
                          '<input type="text" name="trainer" value="' + trainer.battle + '" />' +
                          '<input type="text" name="map" value="' + currentMap + '" />' +
                          '</form>');
                        $('body').append(form);
                        const csrfElem = document.createElement('input');
                        csrfElem.type = 'hidden';
                        csrfElem.name = 'csrfmiddlewaretoken';
                        csrfElem.value = csrf_val;
                        form.append(csrfElem);
                        form.submit();
                    }, Math.max(trainer.dialogue.length * delayPerCharacter - 300, 0));

                } else if(trainer.dialogue != null && !dialogueActive && keys.enter.pressed) {
                    // Remove wild Pokemon
                    document.getElementById("wild").style.display = "none";
                    wildHide = null;
                    dialogueActive = true;
                    // Prepare speaker name and image
                    document.getElementById("speaker_name").innerHTML = trainer.name;
                    document.getElementById("speaker_sprite").src = trainer.image.src;
                    // View dialogue and start writing
                    toggleDialogueWindow({'open': true});
                    writeDialogue(trainer.dialogue);
                }
            } else if(dialogueActive && trainer.battle == null && !stopTravel) {
                if (document.getElementById("speaker_name").innerHTML == trainer.name) {
                    toggleDialogueWindow({'open': false});
                    dialogueActive = false;
                }
            }
        })

        let moving = true;
        player.moving = false;
        surf.moving = true;
        surfer.moving = true;
        ledgeActive = null;


        // Movement logic
        const relevantBoundaries = (onBridge) ? bridgeBounds : boundaries;
        for (const dir of ["w", "a", "s", "d"]) {
            if (keys[dir].pressed && (lastKey === dir || !keys[lastKey].pressed)) {
                player.moving = true;
                nonCameraStatics.forEach(movable => {movable.rows.val = animatePlayer[dir]["row"]});

                // Collisions
                let collided = detectCollision({
                    collidables: relevantBoundaries,
                    collisionFunc: rectangularCollision,
                    offset: animatePlayer[dir]["offset"]
                })
                if (collided != null) {
                    moving = false;
                } else {
                    // Check ledges second
                    let collided = detectCollision({
                        collidables: ledges,
                        collisionFunc: rectangularCollision,
                        offset: animatePlayer[dir]["offset"]
                    })
                    if (collided != null) {
                        if (collided.value == animatePlayer[dir]["ledge"]) {
                            ledgeActive = animatePlayer[dir]["direction"];
                        } else {
                            moving = false;
                        }
                    }
                }

                // Trainer collision
                for (let i = 0; i < mapTrainersSprites.length; i++) {
                    const stationaryTrainer = mapTrainersSprites[i];
                    // Do not collide with non-solid trainers
                    if (!stationaryTrainer.solid)
                        continue;
                    // The extra 6 is to adjust for the larger trainer spritesheet compared to player
                    if (
                        rectangularCollision({
                            rectangle1: player,
                            rectangle2: {...stationaryTrainer, position: {
                                x: stationaryTrainer.position.x + 6 + animatePlayer[dir]["offset"]["x"],
                                y: stationaryTrainer.position.y + 6 + animatePlayer[dir]["offset"]["y"]
                            }}
                        })
                    ) {
                        moving = false;
                        break;
                    }
                }
                if (moving) {
                    statics.forEach(movable => {
                        movable.position.x -= animatePlayer[dir]["offset"]["x"];
                        movable.position.y -= animatePlayer[dir]["offset"]["y"];
                    });
                }
            }
        }
        if (keys.w.pressed || keys.a.pressed || keys.s.pressed || keys.d.pressed) {
            if (moving && !dialogueActive) {
                let areaStr = null;
                // Decrement steps
                if (grass) {
                    if (wildShow == null && wildHide == null)
                        steps -= 1;
                    areaStr = "grass" + currentArea;
                }
                if (surfing) {
                    if (wildShow == null && wildHide == null)
                        steps -= 1;
                    areaStr = "water";
                }
                // Pokemon queueed
                if (wildShow != null) {
                    if ((wildArea == 'grass' && grass) || (wildArea == 'water' && surfing)) {
                        wildShow -= 1;
                    } else {
                        wildArea = null;
                    }
                    if (wildArea == null) {
                        wildShow = null;
                    }
                }
                if (wildHide != null) {
                    wildHide -= 1;
                }
                if (steps < 0) {
                    steps = 20;
                    if (Math.random() < 0.4) {
                        wildArea = (grass) ? 'grass' : 'water';
                        $.ajax(
                        {
                            type: "GET",
                            url: wildUrl,
                            data: {
                                "payload": {"map": currentMap, "area": areaStr}
                            },

                        }).done(function( response ) {
                            let sex = ' ';
                            if (response.sex == "m") {
                                sex = ' <span style="color:blue">&#9794;</span>'
                            } else if (response.sex == "f") {
                                sex = ' <span style="color:magenta">&#9792;</span>'
                            }
                            document.getElementById("wild-name").innerHTML = response.name + sex;
                            document.getElementById("wild-level").innerHTML = "Level " + response.level;
                            document.getElementById("wild-img").src = pokePath + "/" + response.dex_number + ".png";
                            wildShow = 10;
                            wildPokemon = response;
                        });
                    }


                }
                // Logic for showing and hiding wild encounters
                if (wildShow == 0) {
                    document.getElementById("wild").style.display = "block";
                    wildHide = 50;
                    wildShow = null;
                    wildArea = null;
                }
                if (wildHide == 0) {
                    document.getElementById("wild").style.display = "none";
                    wildHide = null;
                }
            }
        } else {
            player.frames.val = 0;
        }
    }

}

function writeDialogue(text) {
    // Get the div where the text will appear
    const dialogueBox = document.getElementById('dialogue');
    dialogueBox.textContent = '';  // Clear any previous content

    let index = 0;

    // Function to append one character at a time
    function addLetter() {
        if (index < text.length) {
            dialogueBox.textContent += text[index];  // Add the next letter
            if (text[index] == ' ') {
                index++;
                dialogueBox.textContent += text[index];
            }
            index++;
            // For spaces, skip
            const delay = (keys.enter.pressed) ? delayPerCharacter / 2 : delayPerCharacter;
            if (dialogueActive)
                setTimeout(addLetter, delay);  // Call this function again after the delay
        }
    }

    // Start the letter-by-letter animation
    addLetter();
}

function toggleDialogueWindow({open}) {
    const dialogueBox = document.getElementById('dialogue');
    const textBox = document.getElementById('speaker');
    const closeBtn = document.getElementById('close');
    if (open) {
        dialogueBox.style.display = 'block';
        textBox.style.display = 'block';
        closeBtn.style.display = 'block';
    } else {
        dialogueBox.style.display = 'none';
        textBox.style.display = 'none';
        closeBtn.style.display = 'none';
    }
}


// Function to handle trainer movements
function trainerTick() {
    mapTrainersSprites.forEach((trainer) => {
        // If there is more than one wander point and has idled for more than 5 ticks, chance to walk
        if (gameTick == trainer.delay && trainer.currentState == 'idle') {
            // If fast, do not idle
            if (trainer.fast) {
                trainer.currentState = 'walking';
                trainer.idleTicks = 0;
            }
            trainer.idleTicks += 1;
            if (Math.random() < 0.5 && trainer.rows.max > 1) {
                // Turn chance
                trainer.rows.val = Math.floor(Math.random() * 4);
            } else if (trainer.wanderPoints.length > 1 && trainer.idleTicks > 1) {
                if (Math.random() < 0.9 * (trainer.idleTicks - 4)) {
                    trainer.currentState = 'walking';
                    trainer.idleTicks = 0;
                }
            }
        }
        // Near trainer case
        if (inRadius({point1: trainer.position, point2: player.position, radius: trainer.radius, offset: 6})) {
            if (!trainer.alwaysMoving) {
                trainer.frames.val = 0;
                trainer.rows.val = 0;
                if (trainer.wasIndependent)
                    trainer.solid = true;
            }
        } else {
            trainer.solid = false;
            trainer.wasIndependent = true;
            // Idle case
            if (trainer.currentState == 'idle') {
                trainer.moving = false;
                if (!trainer.alwaysMoving)
                    trainer.frames.val = 0;
            }
            // Walk case
            if (trainer.currentState == 'walking') {
                trainer.moving = true;
                // SADW
                const destinationIndex = (trainer.currentPoint == trainer.wanderPoints.length - 1) ? 0 : trainer.currentPoint + 1;
                const destination = trainer.wanderPoints[destinationIndex];
                switch(trainer.wanderPoints[trainer.currentPoint].dir) {
                    case 'left':
                        trainer.rows.val = 1;
                        trainer.position.x -= trainer.speed;
                        break;
                    case 'right':
                        trainer.rows.val = 2;
                        trainer.position.x += trainer.speed;
                        break;
                    case 'down':
                        trainer.rows.val = 0;
                        trainer.position.y += trainer.speed;
                        break;
                    case 'up':
                        trainer.rows.val = 3;
                        trainer.position.y -= trainer.speed;
                        break;
                }
                if (trainer.position.x - 8 == destination.x * tileWidth && trainer.position.y == destination.y * tileWidth) {
                    trainer.currentState = "idle";
                    trainer.currentPoint = destinationIndex;
                }
            }
        }


    })
}