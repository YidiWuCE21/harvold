class Boundary {
    constructor({position, width = tile_width, height = tile_width, value = null}) {
        this.position = position;
        this.width = width;
        this.height = height;
        this.offset = {x: 0, y: 0};
        this.value = value;
    }

    draw() {
        c.fillStyle = 'rgba(255, 0, 0, 0.5)';
        c.fillRect(this.position.x, this.position.y, this.width, this.height)
    }
}

class Sprite {
    constructor({ position, velocity, image, crop = {x: 0, y: 0}, frames = {max: 1}, rows = {max: 1}, hitbox = 0, offset = {x: 0, y: 0}}) {
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
    }

    draw() {
        c.drawImage(
            this.image,
            this.frames.val * this.image.width / this.frames.max,
            //this.crop.y
            this.rows.val * this.image.height / this.rows.max + this.crop.y,

            this.image.width / this.frames.max - this.crop.x,
            this.image.height / this.rows.max - this.crop.y,
            this.position.x,
            this.position.y,
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