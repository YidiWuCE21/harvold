# Pokémon Harvold

Pokémon Harvold is a browser-based, fan-made game by me. At the time of writing, it features 63 unique maps, 500+ obtainable Pokémon, and 400+ supported moves. It is a Django web app running on an ASGI server, hosted on Heroku, with a MySQL DB hosted on AWS RDS. You can play the game here:

https://harvold-fa155374a9eb.herokuapp.com/

![Map scene](https://i.imgur.com/gepUYQV.png)
![Battle](https://i.imgur.com/05k1Xei.png)
![Pokemon](https://i.imgur.com/LPiFMoK.png)

## Motivation

The motivation behind Pokémon Harvold is twofold; the first is to improve as a developer by deepening my understanding of certain frameworks and tools. The second is because creating a Pokémon has been a personal goal of mine ever since my favourite browser-based game, Pokémon Omega, was nuked from orbit by Nintendo in 2014.

The game generally uses Gen VI as a guideline for battle mechanics, although some mechanics like Mega Evolution are deliberately not supported. Pokémon past Gen V are not obtainable for nostalgia reasons. The story is not 

## Game Guide

The generic gameplay loop is not much different from standard Pokémon games; you explore maps, catch Pokémon, and level them up. The Pokécenter can be used for healing in between battles. Trainers on routes can be fought for money, which can be used to purchase supplies and useful items at the Pokémart. Excess Pokémon are stored in your Box, and can be swapped into your party between battles. Items are stored in the bag, including TMs, HMs, and held items, which is where they can also be used.

The game is not as railroaded as the handheld games in that there is no explicit story that limits map progression. Some regions, however, are gated behind certain HMs, which can be obtained from beating Gym Leaders.

The current "end-game" is the Battle Mansion, a Pokémon Omega inspired Battle Facility, where you challenge 5 floors of trainers to fight. This activity can award rare TMs and evolution items unobtainable in the shop.

<a name="choices"></a>
## Tech Stack Choices

Django was an obvious choice for me as it was the web framework I used at my job. This was not a choice made for the sake of comfort, but because my work didn't let me fully explore the use of the framework. I wanted to understand how a web server actually functioned, how to use Django's ORM (we preferred raw SQL), and so on. I wanted the flexibility to play with all the tools in the Django environment and commit to my own design choices without going through the usual pipelines at work.

MySQL was chosen because it happened to be the database I clicked when I was exploring RDS. Migrating to Postgres is on the backlog for better write performance, feature richness, support from Django, and parity with the SQLite DB I use for development and testing.

Daphne was chosen because Channels required an ASGI server.

Most of the frontend is written in vanilla HTML, CSS, and JavaScript. React was used for dynamically updating the Pokémon box.

<a name="details"></a>
## Implementation Details

### Turn-Based Battles

Pokémon battles are turn based. In the case of an NPC battle, the server could simply receive a move from the player, choose a move for the opponent, process the game state, and update the player's client. For live battles, this was a bit more complex.

Player clients were built using WebSockets, connected to Consumer objects on the backend. My initial approach to a battle server was to instantiate a worker process that would handle the state update. The problem was that worker tasks in Channels trade feature richness for speed, and don't have a retry mechanism. Stalling a battle in this way was very bad, as players are locked out of basic game features like using the Pokécenter when they were in battle.

My approach was to allow for the individual consumers to execute a battle state update. When a player submitted a move, the consumer would authenticate the player and validate the move, before acquiring a lock on a shared buffer and storing the move. If the buffer has two moves, the consumer proceeded with the state update. If not, it would release the lock, and the state update would be executed when the second player submits their move. The lock is to ensure that both consumers do not try to independently update the states, as Pokémon battles are non-deterministic (you can miss, for instance).

### Collision Detection

Collision detection was implemented by creating square Boundary objects with coordinates and dimensions. Collisions were detected by projecting the player forward in the direction of travel, checking for overlap with a Boundary object, and stopping movement if there was. A similar approach was used to detect if a player was on grass or on water, or if a player was within interaction distance of an NPC.

Optimizations to this including spatial partitioning (discussed in the Hurdles section), and combining contiguous Boundary squares into larger rectangles.

### NPC Collisions

Static NPCs were treated as simple Boundary objects for collision detection. Moving NPCs would stop when the player approached within a certain radius, and offer dialogue or a battle. The main consideration was for moving NPCs not to move into a spot that blocks a player and become stationary, thus trapping them.

When a player left a map, the server would remember their location on the map and place them there when they started. If an NPC moved off of their spawn point and a player walked on to it, the player could reload the map and be stuck inside the NPC. This was just resolved by setting a flag where the NPC would not become solid until the player did not collide with them; in the case where a player spawned on an NPC, they could freely move off before the NPC became "solid" and interactable.

<a name="hurdles"></a>
## Hurdles

### FPS Capping

One of my first alpha testers mentioned that his character would "zoom" across maps when he pressed a movement key. This was the result of my naive implementation of map animation, where my animate() function directly called requestAnimationFrame(). The frequency this function is called generally matches the display refresh rate, and his was over 120Hz. My initial fix involved a setTimeout() on calling the function, which then evolved to manually tracking the elapsed time since the last animation frame and only executing if it exceeded a set interval. The second approach was favoured as setTimeout() had inaccuracies and inconsistent implementations across browsers.

### Spatial Partitioning

If you explore the map for a bit, you will notice that the size of the maps get bigger. This culminated in Route 25, a 240x160 tile monstrosity with over 30 000 instantiated Boundary objects, each of which were checked individually. A previous boundary-dense map took about 0.1ms took as much as 0.9ms. The obvious solution was some form of partitioning, where only Boundary objects close to the player would get checked for collisions.

My initial approach was to define a partition key generator using the coordinates of an object (whether it's a player, boundary, or NPC). All arrays of boundaries would be sorted into a dictionary, with each key corresponding to a list of all the boundaries in its partition. The first pitfall of my initial implementation was trying to dynamically calculate the partition sizes; I reasoned that the optimal partition size was proportional to the square root of the map dimensions. The immediate mistake was calling an expensive sqrt() function every time I checked the player's position (despite the map dimensions not changing), but the less obvious mistake was that this only made sense if I was doing multiple passes of collision detection. I didn't need to; I could just use the same partition key generator on the player to get a hash key and retrieve the objects in O(1) time. I settled on partition sizes that were as small as possible. The final algorithm took an average of 0.07ms for a single pass on Route 25, a better performance than brute-force being run on a map 5% of its size.

A further optimization could be made by only checking in the direction of player movement, but the performance gain here would be fairly small.
