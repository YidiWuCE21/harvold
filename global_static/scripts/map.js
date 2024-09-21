const canvas = document.querySelector('canvas');
const c = canvas.getContext('2d')

canvas.width = 496;
canvas.height = 400;

// Consts to plug in
const movespeed = 2;
const tile_width = 16;
const map_width = 48;
const map_height = 36;
const offset = {x: -176, y: -176};

const collisionsMap = [];
for (let i = 0; i < collisions.length; i += map_width) {
    collisionsMap.push(collisions.slice(i, i + map_width));
}

const boundaries = [];
collisionsMap.forEach((row, i) => {
    row.forEach((col, j) => {
        if (col != 0)
            boundaries.push(new Boundary({position: {
                x: j * tile_width + offset.x,
                y: i * tile_width + offset.y
            }}))
    })
})

// Render map
const mapImage = new Image();
mapImage.src = '/static/assets/maps/oak_village/oak_village.png';
const mapForeground = new Image();
mapForeground.src = '/static/assets/maps/oak_village/oak_village_top.png';


const playerImage = new Image();
playerImage.src = '/static/assets/player/overworld/01.png';



const player = new Sprite({
    position: {
        x: canvas.width / 2 - (64 / 4) / 2,
        y: canvas.height / 2 - (96 / 4) / 2,
    },
    frames: {max: 4},
    rows: {max: 4},
    image: playerImage,
    crop: {x: 0, y: 4},
    hitbox: {width: 10, height: 10},
    offset: {x: 3, y: 6}
})

const background = new Sprite({
    position: {x: offset.x, y: offset.y},
    image: mapImage
});

const foreground = new Sprite({
    position: {x: offset.x, y: offset.y},
    image: mapForeground
});

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
    }
};


const movables = [background, foreground, ...boundaries];
function rectangularCollision({rectangle1, rectangle2}) {
    return (
        rectangle1.position.x + rectangle1.offset.x + rectangle1.width >= rectangle2.position.x + rectangle2.offset.x &&
        rectangle1.position.x + rectangle1.offset.x <= rectangle2.position.x + rectangle2.offset.x + rectangle2.width &&
        rectangle1.position.y + rectangle1.offset.y + rectangle1.height >= rectangle2.position.y + rectangle2.offset.y &&
        rectangle1.position.y + rectangle1.offset.y <= rectangle2.position.y + rectangle2.offset.y + rectangle2.height
    )
}
function animate() {
    window.requestAnimationFrame(animate);
    background.draw();
    /*boundaries.forEach((boundary) => {
        boundary.draw();
    })*/
    player.draw();
    foreground.draw();
    let moving = true;
    player.moving = false
    if (keys.w.pressed && (lastKey === 'w' || !keys[lastKey].pressed)) {
        player.moving = true
        player.rows.val = 3;
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
        player.rows.val = 2;
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
    }
})