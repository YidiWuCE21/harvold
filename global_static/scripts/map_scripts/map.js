
mapInit({map: currentMap, preload: initialMap, startingPos: initialPos});




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
        case 'b':
            keys.shift.pressed = true;
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
        case 'b':
            keys.shift.pressed = false;
            break
    }
})

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