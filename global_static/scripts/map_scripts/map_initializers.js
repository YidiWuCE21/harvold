// File where all the functions that initialize maps live

function mapSetup({map, mapData, forcedOffset = {}, playerOffset = {}, startingPos = null}) {
    if (!(Object.keys(mapData).length === 0))
        currentData = mapData
    // Changes outside canvas
    document.getElementById("map-name").innerHTML = currentData.map_name;
    // Reset relevant vars
    boundaries = [];
    ledges = [];

    // Initialize maps to help with initializing boundary locations
    let waterMap = [];
    let maplinkMap = [];
    let battleMap = [];
    let bridgeMap = []
    let collisionsMap = [];
    let mapTrainers = [];

    // Arrays to store boundaries
    waterTiles = [];
    maplinkTiles = [];
    battleTiles = [];
    bridgeTiles = []
    bridgeBounds = [];

    collisions = currentData.collisions;
    mapTrainers = currentData.trainers;
    water = currentData.water;
    battles = currentData.battles;
    bridge = currentData.bridge || [];
    bridgeExists = bridge.length > 0;
    // Set to zero where water is not None
    if (battles == "all")
        battles = water.map(num => num === 0 ? 1 : 0);
        //battles = new Array(mapWidth * mapHeight).fill(1)
    maplink = currentData.maplink;

    mapHeight = currentData.mapHeight;
    mapWidth = currentData.mapWidth;
    default_offset = JSON.parse(JSON.stringify(currentData.default_offset));
    if (Object.keys(forcedOffset).length === 0) {
        offset = default_offset;
    } else {
        offset = forcedOffset;
    }
    offset.x = offset.x * tileWidth;
    offset.y = offset.y * tileWidth;
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
                x: Math.floor(trainer.wander_points[0].x * tileWidth + 8),
                y: Math.floor(trainer.wander_points[0].y * tileWidth),
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
    for (let i = 0; i < collisions.length; i += mapWidth) {
        collisionsMap.push(collisions.slice(i, i + mapWidth));
    }

    collisionsMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col > 1 && col < 5) {
                // 2 is down ledge, 3 is left ledge, 4 is right ledge
                ledges.push(new Boundary({
                    position: {
                        x: j * tileWidth,
                        y: i * tileWidth
                    },
                    value: col
                }))
            } else if (col != 0) {
                boundaries.push(new Boundary({position: {
                    x: j * tileWidth,
                    y: i * tileWidth
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
        width: (mapWidth + 2) * tileWidth
    });
    boundaries.push(northBound);
    southBound = new Boundary({
        position: {
            x: -16,
            y: mapHeight * tileWidth
        },
        width: (mapWidth + 2) * tileWidth
    });
    boundaries.push(southBound);
    westBound = new Boundary({
        position: {
            x: -16,
            y: -16
        },
        height: (mapHeight + 2) * tileWidth
    });
    boundaries.push(westBound);
    eastBound = new Boundary({
        position: {
            x: mapWidth * tileWidth,
            y: -16
        },
        height: (mapHeight + 2) * tileWidth
    });
    boundaries.push(eastBound);

    // Create water objects
    for (let i = 0; i < water.length; i += mapWidth) {
        waterMap.push(water.slice(i, i + mapWidth));
    }

    waterMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col != 0) {
                // Only surf if surf enabled, otherwise set water as barrier
                if (hms['surf']) {
                    waterTiles.push(new Boundary({position: {
                        x: j * tileWidth,
                        y: i * tileWidth
                    }}))
                } else {
                    boundaries.push(new Boundary({position: {
                        x: j * tileWidth,
                        y: i * tileWidth
                    }}))
                    // check for collision in case party was modified on water; don't modify surfer because we cant surf
                    for (let i = 0; i < boundaries.length; i++) {
                        const boundary = boundaries[i];
                        if (
                            pointCollision({
                                rectangle1: player,
                                rectangle2: {...boundary, position: {
                                    x: boundary.position.x,
                                    y: boundary.position.y
                                }}
                            })
                        ) {
                            statics.forEach((static) => {
                                static.position.x = currentData.default_offset.x * tileWidth;
                                static.position.y = currentData.default_offset.y * tileWidth;
                            })
                            // Move the camera further up by 1/2 the screen
                            camera.position.x -= canvas.width / 2;
                            camera.position.y -= canvas.height / 2;
                        }
                    }
                }
            }
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
                        x: j * tileWidth,
                        y: i * tileWidth
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
                        x: j * tileWidth,
                        y: i * tileWidth
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
                        x: j * tileWidth,
                        y: i * tileWidth
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
    mapLoad = false;
}


function mapInit({map, forcedOffset = {}, preload = null, playerOffset = {}, startingPos = null}) {
    if (!mapLoad) {
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
            }).fail(function( response ) {

                dialogueActive = true;
                // Prepare speaker name and image
                document.getElementById("speaker_name").innerHTML = "Me";
                document.getElementById("speaker_sprite").src = playerImage.src;
                document.getElementById("speaker_sprite").style.top = '2px';
                toggleDialogueWindow({'open': true});
                writeDialogue(response.responseJSON.error);
                // Refresh
                setTimeout(() => {
                    window.location.reload();
                }, Math.max(response.responseJSON.error.length * delayPerCharacter - 300, 0));
            });
        } else {
            mapSetup({map: map, mapData: preload, forcedOffset: forcedOffset, playerOffset: playerOffset, startingPos: startingPos});
        }
    } else {
        console.log("Did not load map")
    }
}