// Basic setup

const canvas = document.querySelector('canvas');
const c = canvas.getContext('2d')

canvas.width = 496;
canvas.height = 400;

// Consts to plug in
const movespeed = 4;
const tile_width = 16;

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

// Variables declared for collision logic
let offset = {};
let boundaries = [];
let waterMap = [];
let waterTiles = [];
let maplinkMap = [];
let maplinkTiles = [];

// Bounding boxes
let northBound = null;
let southBound = null;
let westBound = null;
let eastBound = null;

// Render variables
let mapImage = new Image();
let mapForeground = new Image();
let background = null;
let foreground = null;

let movables = [];
let stopTravel = false;

// Player sprite constants
const playerImage = new Image();
playerImage.src = '/static/assets/player/overworld/' + playerNum + '.png';
const surfImage = new Image();
surfImage.src = '/static/assets/player/overworld/surf.png';
const surferImage = new Image();
surferImage.src = '/static/assets/player/overworld/' + playerNum + 's.png';

const player = new Sprite({
    position: {
        x: canvas.width / 2 - (64 / 4) / 2,
        y: canvas.height / 2 - (96 / 4) / 2,
    },
    frames: {max: 4},
    rows: {max: 4},
    image: playerImage,
    crop: {x: 0, y: 0},
    hitbox: {width: 12, height: 12},
    offset: {x: 3, y: 12}
})

const surf = new Sprite({
    position: {
        x: (canvas.width / 2 - (124 / 4) / 2) + 1,
        y: (canvas.height / 2 - (128 / 4) / 2),
    },
    frames: {max: 4},
    rows: {max: 4},
    image: surfImage
})

const surfer = new Sprite({
    position: {
        x: canvas.width / 2 - (64 / 4) / 2,
        y: canvas.height / 2 - (96 / 4) / 2 - 8,
    },
    frames: {max: 4},
    rows: {max: 4},
    image: surferImage,
})

function mapSetup({map, forcedOffset = {}}) {
    console.log("Setting up map with parameters")
    console.log(map)
    console.log(forcedOffset)
    // Reset relevant vars
    boundaries = [];
    waterMap = [];
    waterTiles = [];
    maplinkMap = [];
    maplinkTiles = [];
    movables = [];

    // Retrieve relevant info from JSON
    console.log(jsonPath + map + '.json')
    $.ajax({
        url: jsonPath + map + '.json',
        async: false,
        dataType: 'json',
        success: function (response) {
            currentData = response;
        }
    })

    collisions = currentData.collisions;
    water = currentData.water;
    battles = currentData.battles;
    if (battles == "all")
        battles = new Array(mapWidth * mapHeight).fill(1)
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
    maplinkKey = currentData.maplinkKey;

    // Create collision objects
    collisionsMap = [];
    for (let i = 0; i < collisions.length; i += mapWidth) {
        collisionsMap.push(collisions.slice(i, i + mapWidth));
    }

    collisionsMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col != 0)
                boundaries.push(new Boundary({position: {
                    x: j * tile_width + offset.x,
                    y: i * tile_width + offset.y
                }}))
        })
    })
    // Create bounding box
    northBound = new Boundary({
        position: {
            x: -16 + offset.x,
            y: -16 + offset.y
        },
        width: (mapWidth + 2) * tile_width
    });
    boundaries.push(northBound);
    southBound = new Boundary({
        position: {
            x: -16 + offset.x,
            y: mapHeight * tile_width + offset.y
        },
        width: (mapWidth + 2) * tile_width
    });
    boundaries.push(southBound);
    westBound = new Boundary({
        position: {
            x: -16 + offset.x,
            y: -16 + offset.y
        },
        height: (mapWidth + 2) * tile_width
    });
    boundaries.push(westBound);
    eastBound = new Boundary({
        position: {
            x: mapWidth * tile_width + offset.x,
            y: -16 + offset.y
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
                    x: j * tile_width + offset.x,
                    y: i * tile_width + offset.y
                }}))
        })
    })

    // Create maplink objects
    for (let i = 0; i < maplink.length; i += mapWidth) {
        maplinkMap.push(maplink.slice(i, i + mapWidth));
    }

    maplinkMap.forEach((row, i) => {
        row.forEach((col, j) => {
            if (col != 0)
                maplinkTiles.push(new Boundary({
                    position: {
                        x: j * tile_width + offset.x,
                        y: i * tile_width + offset.y
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
        position: {x: offset.x, y: offset.y},
        image: mapImage
    });

    foreground = new Sprite({
        position: {x: offset.x, y: offset.y},
        image: mapForeground
    });
    // Create movables
    movables = [background, foreground, ...boundaries, ...waterTiles, ...maplinkTiles];

}

mapSetup({map: currentMap});

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

function animate(looped = true) {
    if (looped)
        window.requestAnimationFrame(animate);
    c.fillStyle = 'black';
    c.fillRect(0, 0, canvas.width, canvas.height);
    background.draw();

    /*boundaries.forEach((boundary) => {
        boundary.draw();
    })
    waterTiles.forEach((boundary) => {
        boundary.draw();
    })
    maplinkTiles.forEach((boundary) => {
        boundary.draw();
    })*/

    // Detect if on water
    let surfing = false;
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
    // Detect if on battle

    if (surfing) {
        surf.draw();
        surfer.draw();
    } else {
        player.draw();
    }
    foreground.draw();

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
                    const newMap = maplinkKey[maplinkTile.value]
                    console.log(newMap)
                    mapSetup(newMap)
                    stopTravel = true;
                }
            }
        }

    }

    // Manage movement
    let moving = true;
    player.moving = false;
    surf.moving = true;
    surfer.moving = true;
    if (keys.w.pressed && (lastKey === 'w' || !keys[lastKey].pressed)) {
        player.moving = true;
        player.rows.val = 2;
        surf.rows.val = 3;
        surfer.rows.val = 2;
        for (let i = 0; i < boundaries.length; i++) {
            const boundary = boundaries[i];
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
        if (moving)
            movables.forEach(movable => {movable.position.y += movespeed});
    } else if (keys.a.pressed && (lastKey === 'a' || !keys[lastKey].pressed)) {
        player.moving = true
        player.rows.val = 1;
        surf.rows.val = 1;
        surfer.rows.val = 1;
        for (let i = 0; i < boundaries.length; i++) {
            const boundary = boundaries[i];
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
        if (moving)
            movables.forEach(movable => {movable.position.x += movespeed});
    } else if (keys.s.pressed && (lastKey === 's' || !keys[lastKey].pressed)) {
        player.moving = true
        player.rows.val = 0;
        surf.rows.val = 0;
        surfer.rows.val = 0;
        for (let i = 0; i < boundaries.length; i++) {
            const boundary = boundaries[i];
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
        if (moving)
            movables.forEach(movable => {movable.position.y -= movespeed});
    } else if (keys.d.pressed && (lastKey === 'd' || !keys[lastKey].pressed)) {
        player.moving = true
        player.rows.val = 3;
        surf.rows.val = 2;
        surfer.rows.val = 3;
        for (let i = 0; i < boundaries.length; i++) {
            const boundary = boundaries[i];
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
        if (moving)
            movables.forEach(movable => {movable.position.x -= movespeed});
    }
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