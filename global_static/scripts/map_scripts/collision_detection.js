function rectangularCollision({rectangle1, rectangle2}) {
    // Check if two rectangles overlap
    return (
        rectangle1.position.x + rectangle1.offset.x + rectangle1.width >= rectangle2.position.x + rectangle2.offset.x &&
        rectangle1.position.x + rectangle1.offset.x <= rectangle2.position.x + rectangle2.offset.x + rectangle2.width &&
        rectangle1.position.y + rectangle1.offset.y + rectangle1.height >= rectangle2.position.y + rectangle2.offset.y &&
        rectangle1.position.y + rectangle1.offset.y <= rectangle2.position.y + rectangle2.offset.y + rectangle2.height
    )
}


function pointCollision({rectangle1, rectangle2}) {
    // Check if object is on another object
    return (
        rectangle1.position.x + rectangle1.width / 2 + rectangle1.offset.x >= rectangle2.position.x + rectangle2.offset.x &&
        rectangle1.position.x + rectangle1.width / 2 + rectangle1.offset.x <= rectangle2.position.x + rectangle2.offset.x + rectangle2.width &&
        rectangle1.position.y + rectangle1.height / 2 + rectangle1.offset.y >= rectangle2.position.y + rectangle2.offset.y &&
        rectangle1.position.y + rectangle1.height / 2 + rectangle1.offset.y <= rectangle2.position.y + rectangle2.offset.y + rectangle2.height
    )
}


function inRadius({point1, point2, radius, offset}) {
    // Check if two points are within a certain Euclidean distance
    const distance = (point1.x + offset - point2.x) ** 2 + (point1.y + offset - point2.y) ** 2;
    return (distance < radius ** 2);
}


function getCellPartition(cell) {
    // Function to get the key for the partition a cell belongs to
    const partitionX = Math.floor(cell.position.x / (tileWidth * 3));
    const partitionY = Math.floor(cell.position.y / (tileWidth * 3));
    return [partitionX, partitionY];
}

function partitionList(objectList) {
    // Partition a list of boundary objects
    let partitionedList = {};
    objectList.forEach((boundary) => {
        const [partitionX, partitionY] = getCellPartition(boundary);
        const partitionKey = `${partitionX}-${partitionY}`;
        // Push to boundary
        partitionedList[partitionKey] ??= [];
        partitionedList[partitionKey].push(boundary);
    })
    return partitionedList;
}

function detectCollision({collidables, collisionFunc, playerObj = player, offset = {x: 0, y: 0}}) {
    // Find the player's partition
    const [partitionX, partitionY] = getCellPartition(playerObj);
    const relevantPartitions = [
        "bounding",
        `${partitionX - 1}-${partitionY - 1}`, `${partitionX}-${partitionY - 1}`, `${partitionX + 1}-${partitionY - 1}`,
        `${partitionX - 1}-${partitionY}`, `${partitionX}-${partitionY}`, `${partitionX + 1}-${partitionY}`,
        `${partitionX - 1}-${partitionY + 1}`, `${partitionX}-${partitionY + 1}`, `${partitionX + 1}-${partitionY + 1}`,
    ]
    // Iterate through each partition
    let collided = null
    relevantPartitions.forEach((partitionKey) => {
        const partitionedCollidables = collidables[partitionKey];
        if (partitionedCollidables != null) {
            // Iterate through collidables in partition
            partitionedCollidables.forEach((collidable) => {
                if (collisionFunc({
                    rectangle1: playerObj,
                    rectangle2: {...collidable, position: {
                        x: collidable.position.x + offset.x,
                        y: collidable.position.y + offset.y
                    }}
                })) {
                    collided = collidable;
                }
            })
        }
    })
    return collided;
}
