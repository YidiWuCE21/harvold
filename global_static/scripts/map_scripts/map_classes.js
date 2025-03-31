// Basic world object
class Boundary {
    constructor({position, width = tileWidth, height = tileWidth, value = null, direction = null, frames = {max: 1}}) {
        this.position = position;
        this.width = width;
        this.height = height;
        this.offset = {x: 0, y: 0};
        this.value = value;
        this.direction = direction;
        this.logicPos = position;
        this.frames = {max: 4, val: 0, elapsed: 0}
        this.image = new Image();
        //this.moving = true;
        if (this.direction != null)
            this.image.src = '/static/assets/misc/' + this.direction + '.png'
    }

    draw(cameraPosition, gameTick) {
        c.drawImage(
            this.image,
            this.frames.val * this.image.width / this.frames.max,
            0,
            this.image.width / this.frames.max,
            this.image.height,
            this.position.x - cameraPosition.x,
            this.position.y - cameraPosition.y,
            this.image.width / this.frames.max,
            this.image.height
        );
        this.frames.val = Math.floor(gameTick / 25);
        //if (!this.moving) return

        /*if (this.frames.max > 1) {
            this.frames.elapsed++
        }
        if (this.frames.elapsed % 20 === 0) {
            if (this.frames.val < this.frames.max - 1) this.frames.val++;
            else this.frames.val = 0;
        }*/
    }

    drawBox(cameraPosition, color) {
        c.fillStyle = color;
        c.fillRect(this.position.x - cameraPosition.x, this.position.y - cameraPosition.y, this.width, this.height)
    }
}

// Animated sprites
class Sprite {
    constructor({ position, velocity, image, crop = {x: 0, y: 0}, flying = false, frames = {max: 1}, rows = {max: 1}, hitbox = 0, offset = {x: 0, y: 0}}) {
        this.position = position;
        this.image = image;
        this.frames = {...frames, val: 0, elapsed: 0};
        this.rows = {...rows, val: 0};
        this.width = this.image.width / this.frames.max;
        this.height = this.image.height / this.rows.max;
        if (hitbox != 0)
            this.height = hitbox.height;
            this.width = hitbox.width;
        this.offset = offset;
        this.crop = crop;
        this.moving = false;
        this.flying = flying;
    }

    draw(cameraPosition) {
        c.drawImage(
            this.image,
            this.frames.val * this.image.width / this.frames.max,
            this.rows.val * this.image.height / this.rows.max + this.crop.y,

            this.image.width / this.frames.max - this.crop.x,
            this.image.height / this.rows.max - this.crop.y,
            this.position.x - cameraPosition.x,
            this.position.y - cameraPosition.y,
            this.image.width / this.frames.max - this.crop.x,
            this.image.height / this.rows.max - this.crop.y
        );
        if (!this.moving) return

        if (this.frames.max > 1) {
            this.frames.elapsed++
        }
        if (this.frames.elapsed % 10 === 0) {
            if (this.frames.val < this.frames.max - 1) this.frames.val++;
            else this.frames.val = 0;
        }

    }
}

// NPC trainers
class Trainer extends Sprite {
    constructor({
        position, velocity, image, wanderPoints, delay, battle = null, dialogue = null, name = null, frameTick = 10,
        speed = 1, crop = {x: 0, y: 0}, frames = {max: 1}, rows = {max: 1}, hitbox = 0, alwaysMoving = false, fast = false, flying = false,
        offset = {x: 0, y: 0}}) {
        super({
            position: position,
            velocity: velocity,
            image: image,
            crop: crop,
            frames: frames,
            rows: rows,
            hitbox: hitbox,
            offset: offset,
            flying: flying
        });
        this.wanderPoints = wanderPoints;
        this.currentPoint = 0;
        this.currentState = 'idle';
        this.idleTicks = 0;
        this.speed = speed;
        this.solid = false;
        this.wasIndependent = false;
        this.width = 12;
        this.height = 12;
        this.delay = delay;
        this.exclamation = new Image();
        if (battle != null) {
            // Trainer has battle
            this.exclamation.src = '/static/assets/misc/exclaim.png';
        } else if (dialogue != null) {
            // Trainer only has dialogue
            this.exclamation.src = '/static/assets/misc/text.png';
        }
        this.battle = battle;
        this.dialogue = dialogue;
        this.radius = (this.battle == null) ? 25 : 35;
        this.name = name;
        this.alwaysMoving = alwaysMoving;
        this.frameTick = frameTick;
        this.fast = fast;
    }

    exclaim(cameraPosition) {
        if (this.solid && (this.battle != null || this.dialogue != null)) {
            c.drawImage(
                this.exclamation,
                this.position.x - cameraPosition.x + 6,
                this.position.y - cameraPosition.y - 12
            );
        }
    }

    draw(cameraPosition) {
        // For alwaysmoving sprites, do check here as we skip in parent method
        if (!this.moving && this.alwaysMoving) {
            if (this.frames.max > 1) {
                this.frames.elapsed++
            }
            if (this.frames.elapsed % this.frameTick === 0) {
                if (this.frames.val < this.frames.max - 1) this.frames.val++;
                else this.frames.val = 0;
            }
        }
        super.draw(cameraPosition);
    }
}