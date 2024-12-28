// Basic setup

const canvas = document.querySelector('canvas');
const c = canvas.getContext('2d');

canvas.width = 576;
canvas.height = 400;

// Consts to plug in
const movespeed = 2;
const tile_width = 16;
const maxSteps = 500;
const minSteps = 150;
const defaultLedgeFrames = 16;
let gameTick = 0;
const delayPerCharacter = 50;

// Variables loaded from JSON
let mapWidth = 0;
let mapHeight = 0;
let maplinkKey = {};
let default_offset = {x: 0, y: 0};
let collisions = [];
let collisionsMap = [];
let water = [];
let battles = []
let maplink = []
let currentMap = mapName;
let currentData = null;
let wildPokemon = null;
let timeOfDay = 'night';

let mapTrainers = [];
let mapTrainersSprites = [];

// Variables declared for collision logic
let offset = {};
let boundaries = [];
let ledges = [];
let waterMap = [];
let waterTiles = [];
let maplinkMap = [];
let maplinkTiles = [];
let battleMap = [];
let battleTiles = [];
let bridgeTiles = [];
let bridgeMap = [];
let bridgeBounds = [];
// Bounding boxes
let northBound = null;
let southBound = null;
let westBound = null;
let eastBound = null;

// Camera boxes
let northCamBound = null;
let southCamBound = null;
let westCamBound = null;
let eastCamBound = null;

// Render variables
let mapImage = new Image();
let mapForeground = new Image();
let background = null;
let foreground = null;
let bridgeImage = new Image();
let bridgeRender = null;

let movables = [];
let statics = [];
let nonCameraStatics = [];
let stopTravel = false;

let mapLoad = true;
let travelDir = null;
// move surfing out for early access
let surfing = false;
let grass = false;
let currentArea = null;

let steps = 10;

let wildShow = null;
let wildHide = null;
let wildArea = null;
let ledgeActive = null;
let ledgeFrames = defaultLedgeFrames;

let dialogueActive = false;

let onBridge = false;


// Player sprite constants
const playerImage = new Image();
playerImage.src = '/static/assets/player/overworld/' + playerNum + '.png';
const surfImage = new Image();
surfImage.src = '/static/assets/player/overworld/surf.png';
const surferImage = new Image();
surferImage.src = '/static/assets/player/overworld/' + playerNum + 's.png';

const player = new Sprite({
    position: {
        x: 0,
        y: 0,
    },
    frames: {max: 4},
    rows: {max: 4},
    image: playerImage,
    crop: {x: 0, y: 0},
    hitbox: {width: 12, height: 12},
    offset: {x: 3, y: 12}
})

const camera = new Boundary({
    position: {
        x: 0,
        y: 0,
    },
    width: 0,
    height: 0
})

const surf = new Sprite({
    position: {
        x: 0,
        y: 0,
    },
    frames: {max: 4},
    rows: {max: 4},
    image: surfImage
})

const surfer = new Sprite({
    position: {
        x: 0,
        y: 0,
    },
    frames: {max: 4},
    rows: {max: 4},
    image: surferImage
})

statics = [player, surf, surfer];


function mapSetup({map, mapData, forcedOffset = {}, playerOffset = {}, startingPos = null}) {
    if (!(Object.keys(mapData).length === 0))
        currentData = mapData
    // Changes outside canvas
    document.getElementById("map-name").innerHTML = currentData.map_name;
    // Reset relevant vars
    boundaries = [];
    ledges = [];


    waterMap = [];
    waterTiles = [];
    maplinkMap = [];
    maplinkTiles = [];
    movables = [];
    battleMap = [];
    battleTiles = [];
    mapTrainers = [];
    bridgeTiles = []
    bridgeBounds = [];
    bridgeMap = []

    collisions = currentData.collisions;
    mapTrainers = currentData.trainers;
    water = currentData.water;
    battles = currentData.battles;
    bridge = currentData.bridge || [];
    // Set to zero where water is not None
    if (battles == "all")
        battles = water.map(num => num === 0 ? 1 : 0);
        //battles = new Array(mapWidth * mapHeight).fill(1)
    maplink = currentData.maplink;

    mapHeight = currentData.mapHeight;
    mapWidth = currentData.mapWidth;
    default_offset = currentData.default_offset;
    if (Object.keys(forcedOffset).length === 0) {
        offset = default_offset;
    } else {
        offset = forcedOffset;
    }
    offset.x = offset.x * tile_width;
    offset.y = offset.y * tile_width;
    // Override offset with playerOffset
    if ("x" in playerOffset) {
        offset.x = playerOffset.x;
    }
    if ("y" in playerOffset) {
        offset.y = playerOffset.y;
    }
    // Override with known offset if available
    if (startingPos != null) {
        offset.x = startingPos.x;
        offset.y = startingPos.y;
    }
    maplinkKey = currentData.maplinkKey;

    // Set the statics new positions
    statics = [player, surfer, surf, camera];
    nonCameraStatics = [player, surfer, surf];
    statics.forEach((static) => {
        static.position.x = offset.x;
        static.position.y = offset.y;
    })

    // Move the surf object right
    surf.position.x -= 6
    surf.position.y -= 6
    // Move the surfer object up
    surfer.position.y -= 9

    // Move the camera further up by 1/2 the screen
    camera.position.x -= canvas.width / 2;
    camera.position.y -= canvas.height / 2;

    // Create trainer objects
    mapTrainersSprites = [];
    mapTrainers.forEach((trainer) => {
        const trainerImage = new Image();
        let trainerOffset = {x: 3, y: 12}
        if ((trainer.type || "trainer") == "pokemon") {
            trainerImage.src = '/static/assets/pokemon/overworld/' + trainer.sprite + '.png';
            trainerOffset = {x: 3, y: 12}
        } else {
            trainerImage.src = '/static/assets/npc/overworld/' + trainer.sprite + '.png';
            trainerOffset = {x: 3, y: 12}
        }
        let trainerRows = trainer.rows || 4;
        mapTrainersSprites.push(new Trainer({
            position: {
                x: Math.floor(trainer.wander_points[0].x * tile_width + 8),
                y: Math.floor(trainer.wander_points[0].y * tile_width),
            },
            frames: {max: 4},
            rows: {max: trainerRows},
            image: trainerImage,
            crop: {x: 0, y: 0},
            offset: trainerOffset,
            wanderPoints: trainer.wander_points,
            delay:  Math.floor(Math.random() * 4) * 25 + 1,
            battle: trainer.battle,
            dialogue: trainer.dialogue,
            name: trainer.name,
            alwaysMoving: trainer.alwaysMoving || false,
            fast: trainer.fast || false,
            frameTick: trainer.frameTick || 10
        }));

    })

    // Create collision objects
    collisionsMap = [];
    for (let i = 0; i < collisions.length; i += mapWidth) {
        collisionsMap.push(collisions.slice(i, i + mapWidth));
    }

    collisionsMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col > 1 && col < 5) {
                // 2 is down ledge, 3 is left ledge, 4 is right ledge
                ledges.push(new Boundary({
                    position: {
                        x: j * tile_width,
                        y: i * tile_width
                    },
                    value: col
                }))
            } else if (col != 0) {
                boundaries.push(new Boundary({position: {
                    x: j * tile_width,
                    y: i * tile_width
                }}))
            }

        })
    })

    // Create bounding box
    northBound = new Boundary({
        position: {
            x: -16,
            y: -16
        },
        width: (mapWidth + 2) * tile_width
    });
    boundaries.push(northBound);
    southBound = new Boundary({
        position: {
            x: -16,
            y: mapHeight * tile_width
        },
        width: (mapWidth + 2) * tile_width
    });
    boundaries.push(southBound);
    westBound = new Boundary({
        position: {
            x: -16,
            y: -16
        },
        height: (mapWidth + 2) * tile_width
    });
    boundaries.push(westBound);
    eastBound = new Boundary({
        position: {
            x: mapWidth * tile_width,
            y: -16
        },
        height: (mapWidth + 2) * tile_width
    });
    boundaries.push(eastBound);

    // Create water objects
    for (let i = 0; i < water.length; i += mapWidth) {
        waterMap.push(water.slice(i, i + mapWidth));
    }

    waterMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col != 0)
                waterTiles.push(new Boundary({position: {
                    x: j * tile_width,
                    y: i * tile_width
                }}))
        })
    })

    // Create bridge objects
    for (let i = 0; i < bridge.length; i += mapWidth) {
        bridgeMap.push(bridge.slice(i, i + mapWidth));
    }

    bridgeMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col != 0)
                bridgeTiles.push(new Boundary({
                    position:{
                        x: j * tile_width,
                        y: i * tile_width
                    },
                    value: col
                }))
        })
    })
    bridgeBounds = bridgeTiles.filter(obj => obj.value === 3);


    // Create maplink objects
    for (let i = 0; i < maplink.length; i += mapWidth) {
        maplinkMap.push(maplink.slice(i, i + mapWidth));
    }

    maplinkMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col != 0)
                maplinkTiles.push(new Boundary({
                    position: {
                        x: j * tile_width,
                        y: i * tile_width
                    },
                    value: col,
                    direction: maplinkKey[col]["direction"]
                }))
        })
    })

    // Create battle objects
    for (let i = 0; i < battles.length; i += mapWidth) {
        battleMap.push(battles.slice(i, i + mapWidth));
    }

    battleMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col != 0)
                battleTiles.push(new Boundary({
                    position: {
                        x: j * tile_width,
                        y: i * tile_width
                    },
                    value: col
                }))
        })
    })

    // Rendered map
    mapImage = new Image();
    mapImage.src = '/static/assets/maps/' + map + '/background.png';
    mapForeground = new Image();
    mapForeground.src = '/static/assets/maps/' + map + '/foreground.png';


    background = new Sprite({
        position: {x: 0, y: 0},
        image: mapImage
    });

    foreground = new Sprite({
        position: {x: 0, y: 0},
        image: mapForeground
    });
    if (currentData.bridge != null) {
        bridgeImage = new Image();
        bridgeImage.src = '/static/assets/maps/' + map + '/bridge.png';
        bridgeRender = new Sprite({
            position: {x: 0, y: 0},
            image: bridgeImage
        })
    }
    // Create movables
    movables = [background, foreground, ...boundaries, ...ledges, ...waterTiles, ...maplinkTiles, ...mapTrainersSprites];
    mapLoad = false;
}


function mapInit({map, forcedOffset = {}, preload = null, playerOffset = {}, startingPos = null}) {
    mapLoad = true;
    currentMap = map;
    // Reset statics

    // Retrieve relevant info from JSON
    if (preload == null) {
        $.ajax(
        {
            type: "GET",
            url: jsonUrl,
            data: {
                "payload": {"map": map}
            }
        }).done(function( response ) {
            mapSetup({map: map, mapData: response, forcedOffset: forcedOffset, playerOffset: playerOffset, startingPos: startingPos});
        }).fail(function() {
            alert("This map is not valid! Returning to world map...");
            window.location.href = worldMapUrl;
        });
    } else {
        mapSetup({map: map, mapData: preload, forcedOffset: forcedOffset, playerOffset: playerOffset, startingPos: startingPos});
    }



}

mapInit({map: currentMap, preload: initialMap, startingPos: initialPos});

const keys = {
    w: {
        pressed: false
    },
    a: {
        pressed: false
    },
    s: {
        pressed: false
    },
    d: {
        pressed: false
    },
    enter: {
        pressed: false
    }
};


function rectangularCollision({rectangle1, rectangle2}) {
    return (
        rectangle1.position.x + rectangle1.offset.x + rectangle1.width >= rectangle2.position.x + rectangle2.offset.x &&
        rectangle1.position.x + rectangle1.offset.x <= rectangle2.position.x + rectangle2.offset.x + rectangle2.width &&
        rectangle1.position.y + rectangle1.offset.y + rectangle1.height >= rectangle2.position.y + rectangle2.offset.y &&
        rectangle1.position.y + rectangle1.offset.y <= rectangle2.position.y + rectangle2.offset.y + rectangle2.height
    )
}
function pointCollision({rectangle1, rectangle2}) {
    return (
        rectangle1.position.x + rectangle1.width / 2 + rectangle1.offset.x >= rectangle2.position.x + rectangle2.offset.x &&
        rectangle1.position.x + rectangle1.width / 2 + rectangle1.offset.x <= rectangle2.position.x + rectangle2.offset.x + rectangle2.width &&
        rectangle1.position.y + rectangle1.height / 2 + rectangle1.offset.y >= rectangle2.position.y + rectangle2.offset.y &&
        rectangle1.position.y + rectangle1.height / 2 + rectangle1.offset.y <= rectangle2.position.y + rectangle2.offset.y + rectangle2.height
    )
}

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

function animate(looped = true) {
    // Increment game tick
    gameTick += 1;
    trainerTick();
    if (gameTick == 100) {
        gameTick = 0;
    }
    // Get camera
    let cappedCamera = {
        x: Math.min(Math.max(camera.position.x, 0), mapWidth * tile_width - canvas.width),
        y: Math.min(Math.max(camera.position.y, 0), mapHeight * tile_width - canvas.height)
    }
    // Check for loop
    if (looped)
        window.requestAnimationFrame(animate);
    // Order game sprites
    let orderedSprites = [...mapTrainersSprites];
    if (surfing) {
        orderedSprites.push(surf);
        orderedSprites.push(surfer);
    } else {
        orderedSprites.push(player);
    }
    let zCompare = (a, b) => {
        if (a.position.y < b.position.y) {
            return -1;
        }
        if (a.position.y < b.position.y) {
            return 1;
        }
        return 0;
    };
    orderedSprites.sort(zCompare);
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
                player.rows.val = 2;
                surf.rows.val = 3;
                surfer.rows.val = 2;
                break;
            case "out":
                player.rows.val = 0;
                surf.rows.val = 0;
                surfer.rows.val = 0;
                break;
            case "north":
                statics.forEach(movable => {movable.position.y -= movespeed});
                player.rows.val = 2;
                surf.rows.val = 3;
                surfer.rows.val = 2;
                break;
            case "south":
                statics.forEach(movable => {movable.position.y += movespeed});
                player.rows.val = 0;
                surf.rows.val = 0;
                surfer.rows.val = 0;
                break;
            case "east":
                statics.forEach(movable => {movable.position.x += movespeed});
                player.rows.val = 3;
                surf.rows.val = 2;
                surfer.rows.val = 3;
                break;
            case "west":
                statics.forEach(movable => {movable.position.x -= movespeed});
                player.rows.val = 1;
                surf.rows.val = 1;
                surfer.rows.val = 1;
                break;
        }
        foreground.draw(cappedCamera);
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
        if (ledgeFrames > 10) {
            nonCameraStatics.forEach(movable => {movable.position.y -= 2});
        } else if (ledgeFrames < 7) {
            nonCameraStatics.forEach(movable => {movable.position.y += 2});
        }
        switch(ledgeActive) {
            case "in":
                player.rows.val = 2;
                surf.rows.val = 3;
                surfer.rows.val = 2;
                break;
            case "north":

                player.rows.val = 2;
                surf.rows.val = 3;
                surfer.rows.val = 2;
                break;
            case "south":
                statics.forEach(movable => {movable.position.y += movespeed});
                player.rows.val = 0;
                surf.rows.val = 0;
                surfer.rows.val = 0;
                break;
            case "east":
                statics.forEach(movable => {movable.position.x += movespeed});
                player.rows.val = 3;
                surf.rows.val = 2;
                surfer.rows.val = 3;
                break;
            case "west":
                statics.forEach(movable => {movable.position.x -= movespeed});
                player.rows.val = 1;
                surf.rows.val = 1;
                surfer.rows.val = 1;
                break;
        }
        foreground.draw(cappedCamera);
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
    for (let i = 0; i < maplinkTiles.length; i++) {
        const maplinkTile = maplinkTiles[i];
        if (
            inRadius({point1: player.position, point2: maplinkTile.position, radius: 50, offset: 0})
        ) {
            // Set opacity based on distance to player
            const distance = Math.sqrt((player.position.x - maplinkTile.position.x) ** 2 + (player.position.y - maplinkTile.position.y) ** 2)
            const opacity = -3/250 * distance + 1
            c.globalAlpha = opacity;
            maplinkTile.draw(cappedCamera, gameTick);
            c.globalAlpha = 1;
        }
    }

    // Detect if on water
    surfing = false;
    if (!onBridge) {
        for (let i = 0; i < waterTiles.length; i++) {
            const waterTile = waterTiles[i];
            if (
                pointCollision({
                    rectangle1: player,
                    rectangle2: {...waterTile, position: {
                        x: waterTile.position.x,
                        y: waterTile.position.y
                    }}
                })
            ) {
                surfing = true;
                break;
            }
        }
    }
    // Detect if on battle
    currentArea = null;
    grass = false;
    if (!onBridge) {
        for (let i = 0; i < battleTiles.length; i++) {
            const battleTile = battleTiles[i];
            if (
                pointCollision({
                    rectangle1: player,
                    rectangle2: {...battleTile, position: {
                        x: battleTile.position.x,
                        y: battleTile.position.y
                    }}
                })
            ) {
                grass = true;
                currentArea = battleTile.value;
                break;
            }
        }
    }
    // Detect if on bridge
    const currentOnBridge = onBridge;
    onBridge = false;
    for (let i = 0; i < bridgeTiles.length; i++) {
        const bridgeTile = bridgeTiles[i];
        if (bridgeTile.value == 3)
            continue;
        if (
            pointCollision({
                rectangle1: player,
                rectangle2: {...bridgeTile, position: {
                    x: bridgeTile.position.x,
                    y: bridgeTile.position.y
                }}
            })
        ) {
            if (bridgeTile.value == 2) {
                onBridge = true;
            } else if (bridgeTile.value == 1 && currentOnBridge) {
                onBridge = true;
            } else {
                onBridge = false;
            }
        }
    }
    /*// Draw ledges
    for (let i = 0; i < ledges.length; i++) {
        const ledge = ledges[i];
        ledge.drawBox(cappedCamera, 'rgba(255, 0, 0, 0.3)');
    }
    // Draw collision
    for (let i = 0; i < boundaries.length; i++) {
        const boundary = boundaries[i];
        boundary.drawBox(cappedCamera, 'rgba(0, 255, 0, 0.3)');

    }*/
    // Draw trainers in order
    for (let i = 0; i < orderedSprites.length; i++) {
        const currentSprite = orderedSprites[i];
        currentSprite.draw(cappedCamera);
    }
    foreground.draw(cappedCamera);
    if (!onBridge)
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
            for (let i = 0; i < maplinkTiles.length; i++) {
                const maplinkTile = maplinkTiles[i];
                if (
                    pointCollision({
                        rectangle1: player,
                        rectangle2: {...maplinkTile, position: {
                            x: maplinkTile.position.x,
                            y: maplinkTile.position.y
                        }}
                    })
                ) {
                    const newMap = maplinkKey[maplinkTile.value];
                    // Play the map travel animation
                    player.moving = true;
                    travelDir = maplinkTile.direction;
                    // Use current position to overwrite positional offset
                    if ("posOffset" in newMap) {
                        newMap["playerOffset"] = {};
                        if ("x" in newMap["posOffset"]) {
                            newMap["playerOffset"]["x"] = player.position.x + newMap["posOffset"]["x"] * tile_width;
                        }
                        if ("y" in newMap["posOffset"]) {
                            newMap["playerOffset"]["y"] = player.position.y + newMap["posOffset"]["y"] * tile_width;
                        }
                    }
                    mapInit(newMap);
                    stopTravel = true;
                }
            }
        }
    }
    // Also manages enter events but we need to loop this regardless so keep it outside of block
    mapTrainersSprites.forEach((trainer) => {
        if (trainer.solid) {
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
                      '</form>');
                    $('body').append(form);
                    const csrfElem = document.createElement('input');
                    csrfElem.type = 'hidden';
                    csrfElem.name = 'csrfmiddlewaretoken';
                    csrfElem.value = csrf_val;
                    form.append(csrfElem);
                    form.submit();
                }, Math.max(trainer.dialogue.length * delayPerCharacter - 500, 0));

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
        } else if(dialogueActive && trainer.battle == null) {
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
    // Draw bounds
    /*for (let i = 0; i < relevantBoundaries.length; i++) {
        const ledge = relevantBoundaries[i];
        ledge.drawBox(cappedCamera, 'rgba(255, 0, 0, 0.3)');
    }*/
    if (keys.w.pressed && (lastKey === 'w' || !keys[lastKey].pressed)) {
        player.moving = true;
        player.rows.val = 2;
        surf.rows.val = 3;
        surfer.rows.val = 2;

        // Collisions
        for (let i = 0; i < relevantBoundaries.length; i++) {
            const boundary = relevantBoundaries[i];
            if (
                rectangularCollision({
                    rectangle1: player,
                    rectangle2: {...boundary, position: {
                        x: boundary.position.x,
                        y: boundary.position.y + movespeed
                    }}
                })
            ) {
                moving = false;
                break;
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
                        x: stationaryTrainer.position.x + 6,
                        y: stationaryTrainer.position.y + 6 + movespeed
                    }}
                })
            ) {
                moving = false;
                break;
            }
        }
        if (moving) {
            statics.forEach(movable => {movable.position.y -= movespeed});
        }
    } else if (keys.a.pressed && (lastKey === 'a' || !keys[lastKey].pressed)) {
        player.moving = true
        player.rows.val = 1;
        surf.rows.val = 1;
        surfer.rows.val = 1;
        for (let i = 0; i < relevantBoundaries.length; i++) {
            const boundary = relevantBoundaries[i];
            if (
                rectangularCollision({
                    rectangle1: player,
                    rectangle2: {...boundary, position: {
                        x: boundary.position.x + movespeed,
                        y: boundary.position.y
                    }}
                })
            ) {
                moving = false;
                break;
            }
        }
        if (moving) {
            // Check ledges second
            for (let i = 0; i < ledges.length; i++) {
                const ledge = ledges[i];
                if (ledge.value == 3) {
                    if (
                        rectangularCollision({
                            rectangle1: player,
                            rectangle2: {...ledge, position: {
                                x: ledge.position.x + movespeed,
                                y: ledge.position.y
                            }}
                        })
                    ) {
                        ledgeActive = 'west';
                        break;
                    }
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
                        x: stationaryTrainer.position.x + 6 + movespeed,
                        y: stationaryTrainer.position.y + 6
                    }}
                })
            ) {
                moving = false;
                break;
            }
        }
        if (moving) {
            statics.forEach(movable => {movable.position.x -= movespeed});
        }
    } else if (keys.s.pressed && (lastKey === 's' || !keys[lastKey].pressed)) {
        player.moving = true
        player.rows.val = 0;
        surf.rows.val = 0;
        surfer.rows.val = 0;
        for (let i = 0; i < relevantBoundaries.length; i++) {
            const boundary = relevantBoundaries[i];
            if (
                rectangularCollision({
                    rectangle1: player,
                    rectangle2: {...boundary, position: {
                        x: boundary.position.x,
                        y: boundary.position.y - movespeed
                    }}
                })
            ) {
                moving = false;
                break;
            }
        }
        if (moving) {
            // Check ledges second
            for (let i = 0; i < ledges.length; i++) {
                const ledge = ledges[i];
                if (ledge.value == 2) {
                    if (
                        rectangularCollision({
                            rectangle1: player,
                            rectangle2: {...ledge, position: {
                                x: ledge.position.x,
                                y: ledge.position.y - movespeed
                            }}
                        })
                    ) {
                        ledgeActive = 'south';
                        break;
                    }
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
                        x: stationaryTrainer.position.x + 6,
                        y: stationaryTrainer.position.y + 6 - movespeed
                    }}
                })
            ) {
                moving = false;
                break;
            }
        }
        if (moving) {
            statics.forEach(movable => {movable.position.y += movespeed});
        }
    } else if (keys.d.pressed && (lastKey === 'd' || !keys[lastKey].pressed)) {
        player.moving = true
        player.rows.val = 3;
        surf.rows.val = 2;
        surfer.rows.val = 3;
        for (let i = 0; i < relevantBoundaries.length; i++) {
            const boundary = relevantBoundaries[i];
            if (
                rectangularCollision({
                    rectangle1: player,
                    rectangle2: {...boundary, position: {
                        x: boundary.position.x - movespeed,
                        y: boundary.position.y
                    }}
                })
            ) {
                moving = false;
                break;
            }
        }
        // Check ledges second
        if (moving) {
            for (let i = 0; i < ledges.length; i++) {
                const ledge = ledges[i];
                if (ledge.value == 4) {
                    if (
                        rectangularCollision({
                            rectangle1: player,
                            rectangle2: {...ledge, position: {
                                x: ledge.position.x - movespeed,
                                y: ledge.position.y
                            }}
                        })
                    ) {
                        ledgeActive = 'east';
                        break;
                    }
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
                        x: stationaryTrainer.position.x + 6 - movespeed,
                        y: stationaryTrainer.position.y + 6
                    }}
                })
            ) {
                moving = false;
                break;
            }
        }
        if (moving) {
            statics.forEach(movable => {movable.position.x += movespeed});
        }
    }
    if (keys.w.pressed || keys.a.pressed || keys.s.pressed || keys.d.pressed) {
        if (moving && !dialogueActive) {
            let areaStr = null;
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
                steps = 10;
                if (Math.random() < 0.15) {
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
    //applyFilter();
}

function inRadius({point1, point2, radius, offset}) {
    const distance = (point1.x + offset - point2.x) ** 2 + (point1.y + offset - point2.y) ** 2;
    return (distance < radius ** 2);
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
                if (trainer.position.x - 8 == destination.x * tile_width && trainer.position.y == destination.y * tile_width) {
                    trainer.currentState = "idle";
                    trainer.currentPoint = destinationIndex;
                }
            }
        }


    })
}

animate();

let lastKey = '';
window.addEventListener('keydown', (e) => {
    switch (e.key) {
        case 'w':
            keys.w.pressed = true;
            lastKey = 'w';
            break
        case 'a':
            keys.a.pressed = true;
            lastKey = 'a';
            break
        case 's':
            keys.s.pressed = true;
            lastKey = 's';
            break
        case 'd':
            keys.d.pressed = true;
            lastKey = 'd';
            break
        case 'Enter':
            keys.enter.pressed = true;
            break
    }
})

window.addEventListener('keyup', (e) => {
    switch (e.key) {
        case 'w':
            keys.w.pressed = false;
            break
        case 'a':
            keys.a.pressed = false;
            break
        case 's':
            keys.s.pressed = false;
            break
        case 'd':
            keys.d.pressed = false;
            break
        case 'Enter':
            keys.enter.pressed = false;
            stopTravel = false;
            break
    }
})

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

function updatePos() {
    // Define the URL for your Django view
    const pos = {
        'x': player.position.x,
        'y': player.position.y,
        'map': currentMap
    }

    // Send the data asynchronously using fetch
    fetch(posUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',  // Indicate that you're sending JSON
        },
        body: JSON.stringify({pos})  // Convert the data to a JSON string
    })
    .catch(error => {
        // Handle any errors that occur during the fetch request
        console.error('Fetch error:', error);
    });
}

window.addEventListener('beforeunload', function (event) {
    // Send the position on map exit
    updatePos();
});