// Canvas setup
const canvas = document.querySelector('canvas');
const c = canvas.getContext('2d');
canvas.width = 576;
canvas.height = 400;

// Tile width
const tileWidth = 16;
const maxSteps = 500;
const minSteps = 150;
const delayPerCharacter = 50;

let movespeed = 2; // Movement speed

let gameTick = 0; // Game tick tracker

const enablePartitioning = true;

// Variables to be filled from map JSON
let mapWidth = 0;
let mapHeight = 0;
let maplinkKey = {}; // Mapping from maplink values to which maps they lead to
let default_offset = {x: 0, y: 0}; // Default landing tile on maps
let collisions = []; // Wall tiles
let water = []; // Water tiles
let battles = []; // Battle tiles
let maplink = []; // New map tiles
let mapTrainersSprites = []; // Trainers on map
let currentMap = mapName;
let currentData = null;
let wildPokemon = null;
let timeOfDay = 'night';

// Variables declared for collision logic
let offset = {};

let boundaries = [];
let ledges = null;
let waterTiles = null;
let maplinkTiles = null;
let battleTiles = null;
let bridgeTiles = null;
let bridgeBounds = null;
let maplinkUnpartitioned = null;

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

let statics = [];
let nonCameraStatics = [];
let stopTravel = false;

let mapLoad = false;
let travelDir = null;
// move surfing out for early access
let surfing = false;
let grass = false;
let currentArea = null;

// Wild Pokemon generators
let steps = 20;
let wildShow = null;
let wildHide = null;
let wildArea = null;

// Ledge related variables
const defaultLedgeFrames = 15;
let ledgeActive = null;
let ledgeFrames = defaultLedgeFrames;

// Trainer dialogue flag
let dialogueActive = false;

// Bridge flag
let bridgeExists = false;
let onBridge = false;

// Input keys
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
    },
    shift: {
        pressed: false
    }
};


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

// Statics to "move"
statics = [player, surf, surfer];