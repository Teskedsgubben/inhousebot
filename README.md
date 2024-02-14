# InhouseBot Instructions

*Welcome to the InhouseBot Dota League*

Join us by typing `/register` in the commands channel! Playing games using the bot allows you to keep track of your stats, earn points, bet on games and more!

**Protip**: Mute the commands channel, it may get messy...

### Quickstart

- Start a new game with `/newgame gamename`
- Join teams by reacting to the creeps
- **In progress, released soon:** Place bets with `/bet XXX team`
- Set winning team with `/winner team`

### Playing a game

Typing `/newgame` in the *#commands* channel creates a new game in the *#games* channel. You can add a name to the game like `/newgame gamename` when creating it. 

The bot now posts the game in the *#games* channel as a professionally styled message. The bot adds reactions with a Radiant <:Creep_Radiant:1207041014481682502> and Dire <:Creep_Dire:1207041042780790784> creep automatically. Players can join the respective team by clicking that creep, which will automatically move them into the *:loud_sound:Radiant* or *:loud_sound:Dire* voice channel. 

For a limited time after creating the game, players can place their bets. Players that have joined the game can do so like `/bet 100` to place a bet of 100 on their own team. Players not in the game can bet on any team like `/bet 100 radiant`. Note that joining the other team after placing that bet will discard it, no 322 here. Leaving the team will activate it again though.

When the game is over, register the winner of the current game with `/winner team` to close the game. This moves all players back into the *:loud_sound:Lobby* channel and archives the match data.

All players in the match have their Inhouse MMR updated after the game. Each player in the winning team is awarded 50 points, regardless of bets. Players with bets on the losing team have their points taken away, while players with bets on the winning team receive their earnings.

### Points system

The InhouseBot Points League is the third most prestigious league in the world according to the New York Times\*. When registering to the league, the new player recieves 100 points to start. Each game victory grants an additional 50 points. 

However, the action starts when you get into the betting game! When a new game is created, it is open for bets during the initial betting period. When you enter a game, you can bet on your own team with points from your points pool. If your team wins, you get your earned winnings based on your bet multiplied by that team's odds at the time your bet was placed. As a spectator, you can bet on any team!

*\* This is not entirely true*

### MMR system

The Inhouse MMR works almost just like the DotA MMR, but with one key difference! It's completely different. With that we mean it has no correlation to your DotA MMR as mechanics like balanced shuffle, immortal draft etc will spread out DotA MMRs across the teams. A low ranked player that plays above their level will therefore have a higher Inhouse MMR than a much higher ranked player that plays below their level. See how that works?

Other than that, it works very similarly. Upon registration you get assigned a default value of 3000 MMR. Each game gives or takes 25, with the calibration period taking more per game.

This MMR value is used when computing the odds of the game. This inderectly implies that the odds are not based on skill, but only relative performance. It's up to you to identify the opportunities where it's completely wrong and place a massive bet, pushing you to the top of the scoreboard!

### List of commands
- **/test**: See if the bot is even alive
- **/roll**: Roll a number between 0-100
- **/rollall**: Roll a number between 0-100 for all players in the *Lobby* voice channel
- **/lobby**: Moves everyone in the *Radiant* and *Dire* voice channels to *Lobby*
- **/updateinstructions**: Updates this page to reflect the latest version of the README.md file in the repository
- **/newgame**: Starts a new game in the #games channel
- **/winner**: Registers a winner to the current game and shuts it down
- **/register**: Register your account as a user to start tracking stats
- **/mystats**: Show your personal stats
- **/scoreboard**: Show the summarized scoreboard for all players
- **/setname**: Change your display name in the Inhouse League
- **/addid**: Adds an id associated with your account, not used atm