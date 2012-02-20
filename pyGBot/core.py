#
##    Apples To Apples - a plugin for pyGBot
##    Copyright (C) 2008 Morgan Lokhorst-Blight and Aleksandr Soborov
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

import sys, string, random, time
from pyGBot import log
from pyGBot.BasePlugin import BasePlugin

# Import the card lists.
from ApplesCards import GREENCARDS, REDCARDS

# Note: When sending messages, codes such as "\x034" refer to IRC
# colors, and "\x0F" cancels all formatting. In this game, 
# red cards are output red, and green cards are output green.
# Player names are output in blue when deemed important (such as
# when they are judging or just won a card)

class ApplesToApples(BasePlugin):
    # Run on plugin initialization
    def __init__(self, bot, options):
        # Hook the base plugin
        BasePlugin.__init__(self, bot, options)
        # Control output
        self.output = True
        # Initialize variables
        self.resetdata()
    
    # Run every second
    def timer_tick(self):
        # Timer only needs to happen while the game is running
        if self.gamestate == "InProgress":
            # Increment timer.
            self.timer = self.timer + 1
            # Once a minute, prompt users to take their actions and reset the timer.
            if self.timer == 60:
                self.timer = 0
                self.cmd_prompt([], self.channel, self.bot.nickname)

    # Run for every public message the bot sees
    def msg_channel(self, channel, user, message):
        # ":" is commonly used to direct messages on IRC
        # Split the message over :...
        a = string.split(message, ":", 1)
        # ..and see if it's directed to the bot
        if len(a) > 1 and a[0].lower() == self.bot.nickname.lower():
            # It is! Run the command.
            self.do_command(channel, user, string.strip(a[1]))
        # "!" is also used as a bot trigger.
        # See if the message starts with a "!", and isn't only that char.
        elif message[0]=='!' and (len(message) > 1):
            # It does! Run the command.
            self.do_command(channel, user, string.strip(message[1:]))
    
    # Run for every private message the bot sees
    def msg_private(self, user, message):
        # Pass the username as the channel to denote a private message
        self.do_command(user, user, message)

    # Reply in the same fashion a command was issued in
    def reply(self, channel, user, text):
        # If the 'channel' field isn't the user, it's a public message...
        if channel != user:
            self.bot.pubout(channel, "%s: %s" % (user, text))
        # ...if it is the user, it's a private message
        else:
            self.bot.noteout(user, text)
    
    # Always reply privately
    def privreply(self, user, text):
        self.bot.noteout(user, text)
        
    # Run when the bot sees a user change names
    def user_nickchange(self, old, new):
        # Replace the old nick with the new one in every variable that
        # references a player.
        for list_ in (self.players, self.live_players, self.round_players):
            if old in list_:
                list_[list_.index(old)] = new
        for value in (self.playedcards):
            if value[0] == old:
                value[0] = new
        for map_ in (self.hands, self.woncards):
            if map_.has_key(old):
                map_[new] = map_[old]
                del map_[old]

    # Initialize or reset all game variables
    def resetdata(self):
        # All self-instantiated variables.
        # References to data structure are not actual variable names!
        
        self.gamestate = "None" # Used to track if game is not in progress, in setup, or not running.
        self.players = [] # Array of all players to participate
        self.live_players = [] # Array of all players currently in the game
        self.round_players = [] # Array of players that participated in a round
        self.greendeck = GREENCARDS.keys() # Instance of the green cards
        random.shuffle(self.greendeck) # Shuffle 'em up!
        self.reddeck = REDCARDS.keys() # Instance of the red cards
        random.shuffle(self.reddeck) # Shuffle 'em up!
        self.judgeindex = 0 # Player array index for the current judge
        self.hands={} # Dictionary of user:[hand]
        self.greencard = None # Current green card
        self.playedcards = [] # Array of [user], [card]
        self.woncards = {} # Dictonary of user:[cards won]
        self.cardstowin = 0 # How many cards a player must earn to win; based on starting user count
        self.channel = None # IRC channel to run the game in
        self.timer = 0 # Timer counter
        self.judging = False # Judging phase flag

    # Set the game up
    def startgame(self):
        # The game started; change phase
        self.gamestate = "InProgress"
        # Inform players 
        self.bot.pubout(self.channel, "A new game is starting! Please wait, dealing cards... (use !peek to see card descriptions)")
        # Add joined players to the player history
        self.players = list(self.live_players)
        # Shuffle the joined players up
        random.shuffle(self.live_players)
        # Everyone gets a blank slate
        for user in self.live_players:
            self.woncards[user] = []
            self.hands[user] = []
        # Now everyone gets seven cards to start with. Don't need the 
        # extra card text, and it takes too long to send seven messages per
        # player on most IRC servers.
        for i in range(1, 8):
            for user in self.live_players:
                self.hands[user].append(self.reddeck.pop(0))
        # Sort the cards for each user, and tell them what they have
        for user in self.live_players:
            self.hands[user].sort()
            hand = []
            for i in range (1, 8):
                hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
            self.privreply(user, "Your hand: %s" % ", ".join(hand))
        # Decide how many green cards are needed for victory
        if len(self.live_players) >= 8:
            self.cardstowin = 4
        else:
            self.cardstowin = 12 - len(self.live_players)
        # Assign judge index to the last player
        self.judgeindex = len(self.live_players) - 1
        # Initiate the first round
        self.newround()

    # Tear the game down
    def endgame(self):
        self.bot.pubout(self.channel, "The game is over.")
        # If the game was in progress, tell the users what the score was.
        if self.gamestate == "InProgress":
            # Temporary array to build a string
            greenbuild = []
            # Append "user - cards won" to the building string.
            for user in self.players:
                if len(self.woncards[user]) != 0:
                    greenbuild.append("%s - %i" % (user, len(self.woncards[user])))
            # Don't output if there are no cards won
            if greenbuild != []:
                self.bot.pubout(self.channel, "Green cards per players: %s" % ", ".join(greenbuild))
            # Run a "greens" command for each user in the game
            # so they can see which cards they won
            for user in self.live_players:
                self.cmd_greens([], user, user)
        # Clean the board
        self.resetdata()
        
    # Start a new round
    def newround(self):
        # Reset the judge flag and timers
        self.judging = False
        self.timer = 0
        # Display the score
        self.cmd_scores([], self.channel, self.bot.nickname)
        
        # Reset the cards played
        self.playedcards = []
        # Increment the judge index, unless it needs to wrap around, and 
        # tell the players who's judging
        if self.judgeindex == len(self.live_players) - 1:
            self.judgeindex = 0
        else:
            self.judgeindex = self.judgeindex + 1
        self.bot.pubout(self.channel, "This round's judge is \x02\x0312%s\x0F." % self.live_players[self.judgeindex])
        
        # Select a new green card and tell the players what it is along
        # with a short syntax reminder
        self.greencard = self.greendeck.pop(0)
        self.bot.pubout(self.channel, "The new green card is: \x02\x033%s\x0F - %s. Please play cards from your hand using '!play <number>'." % (self.greencard, GREENCARDS[self.greencard]))
    
    # Check if the round is over
    def checkroundover(self):
        # Assume everyone has played; if someone hasn't, set to false
        allplayed = True
        for player in self.live_players:
            if player != self.live_players[self.judgeindex]:
                playerplayed = False
                for card in self.playedcards:
                    if player == card[0]:
                        playerplayed = True
                if playerplayed == False:
                    allplayed = False
                    
        # Has everyone played a card? If yes, it's time to judge.
        if allplayed and not self.judging:
            self.bot.pubout(self.channel, "All cards have been played.")
            self.judging = True
            self.beginjudging()
    
    # Begin the judging phase
    def beginjudging(self):
        # Reset timer, and remind the judge what the green card is
        self.timer = 0
        self.bot.pubout(self.channel, "Green card is: \x02\x033%s\x0F - %s" % (self.greencard, GREENCARDS[self.greencard]))
        # Shuffle the played cards, and send them out with the card descriptions
        random.shuffle(self.playedcards)
        for i in range (0, len(self.playedcards)):
            self.bot.pubout(self.channel, "%i. \x034%s\x0F: %s" % (i+1, self.playedcards[i][1], REDCARDS[self.playedcards[i][1]]))
        # Judge prompt and syntax reminder
        self.bot.pubout(self.channel, "\x02\x0312%s\x0F: Please make your decision now using the '!pick <number>' command." % self.live_players[self.judgeindex])
    
    # End the round
    def cardwin(self, winningcard):
        # The winner, as picked by the judge; inform the players
        winner = self.playedcards[winningcard][0]
        self.bot.pubout(self.channel, "The judge picked \x034%s\x0F! \x02\x0312%s\x0F played that red card, and gets to keep the green card." % (self.playedcards[winningcard][1], winner))
        # Give the player the victory card
        self.woncards[winner].append(self.greencard)
        # Is the game over?
        if not self.checkgamewin():
            # Nope. Keep going.
            self.deal()
            self.newround()
        
    # Check if the game is over
    def checkgamewin(self):
        # Has anyone hit the card limit?
        for user in self.players:
            if len(self.woncards[user]) >= self.cardstowin:
                # Yep! Congratulate the victor and end the game
                self.bot.pubout(self.channel, "%s now has %i green cards. %s wins!" % (user, len(self.woncards[user]), user))
                self.endgame()
                return True
        else:
            # Nope. Keep going.
            return False
    
    # Deal cards as required
    def deal(self):
        # If any player doesn't have 7 cards, give them cards until they do.
        for user in self.live_players:
            while len(self.hands[user]) < 7:
                self.hands[user].append(self.reddeck.pop(0))
                # Tell them what card they just drew, with extra text
                self.privreply(user, "You draw: \x034%s\x0F: %s" % (self.hands[user][len(self.hands[user])-1], REDCARDS[self.hands[user][len(self.hands[user])-1]]))
        # For every player, build a string and send them their hand
        for user in self.live_players:
            self.hands[user].sort()
            hand = []
            for i in range (1, 8):
                hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
            self.privreply(user, "Your hand: %s" % ", ".join(hand))
    
    # User command: Play a card
    def cmd_play(self, args, channel, user):
        #Only works in game
        if self.gamestate == "InProgress":
            # If the player's in the game, and isn't
            # the judge, and it's not time to judge...
            if user in self.live_players and user != self.live_players[self.judgeindex] and self.judging == False:
                # Very easy for input to mess up here, and we don't want
                # the bot to crash.
                try:
                    # Is it in the valid  card range?
                    if int(args[0]) > 0 and int(args[0]) < 8:
                        # Assume they haven't played, and run a check.
                        cardplayed = False
                        for cards in self.playedcards:
                            # Oops! They already have.
                            if cards[0] == user:
                                cardplayed = True
                        if cardplayed:
                            # Don't let them play another, of course.
                            self.reply(channel, user, "You have already played a card this round.")
                        else:
                            # Only valid path. 
                            self.playedcards.append([user, self.hands[user].pop(int(args[0])-1)])
                            self.reply(channel, user, "You have played a card.")
                            self.checkroundover()
                    else:
                        # "What do you mean, card 11?"
                        self.reply(channel, user, "Please pick a valid card number (1-7).")
                except:
                    # "What do you mean, card Q?"
                    self.reply(channel, user, "Please use the card's number.")
            elif user not in self.live_players:
                # They aren't even in the game!
                self.reply(channel, user, "You are not in this game.")
            elif user == self.live_players[self.judgeindex]:
                # Judge doesn't get to play.
                self.reply(channel, user, "You are judging this round.")
            elif self.judging == True:
                # Everyone's played by now.
                self.reply(channel, user, "Judging has already begun, wait for the next round.")
        else:
            # We're not even playing!
            self.reply(channel, user, "There is no game in progress.")

    # User command: Judge a card
    def cmd_pick(self, args, channel, user):
        if self.gamestate == "InProgress":
            # Are we judging? Is this the judge?
            if self.judging == True and user == self.live_players[self.judgeindex]:
                # Did they pick a valid number?
                try:
                    if int(args[0]) > 0 and int(args[0]) <= len(self.playedcards):
                        # Yep! That card just won!
                        self.reply(channel, user, "You have chosen.")
                        self.cardwin(int(args[0]) - 1)
                    else:
                        # "What do you mean, card 11?"
                        self.reply(channel, user, "Please pick a valid card number.")
                except ValueError:
                    # "What do you mean, card Q?"
                    self.reply(channel, user, "Please use the card's number.")
            elif user != self.live_players[self.judgeindex]:
                # Not the judge
                self.reply(channel, user, "You are not the judge this round.")
            elif len(self.playedcards) != len(self.live_players) - 1:
                # Not time to judge yet
                self.reply(channel, user, "Not everyone has played a card yet.")
            elif user not in self.live_players:
                # Not a player
                self.reply(channel, user, "You are not in this game.")
        else:
            # We're not even playing!
            self.reply(channel, user, "There is no game in progress.")
    
    # User command: Read card text
    def cmd_peek(self, args, channel, user):
        if self.gamestate == "InProgress":
            # Is the user in the game?
            if user in self.live_players:
                # Is it a valid card?
                try:
                    if int(args[0]) > 0 and int(args[0]) <= len(self.hands[user]):
                        # Privately tell them the card text
                        self.privreply(user, "\x034%s\x0F - %s" % (self.hands[user][int(args[0])-1], REDCARDS[self.hands[user][int(args[0])-1]]))
                    else:
                        # "What do you mean, card 11?"
                        self.reply(channel, user, "Please pick a valid card number.")
                except:
                    # "What do you mean, card Q?"
                    self.reply(channel, user, "Please use the card's number.")
            else:
                # Not a player
                self.reply(channel, user, "You are not in this game.")
        else:
            # Not a game
            self.reply(channel, user, "There is no game in progress.")

    # User command: Start a game
    def cmd_start(self, args, channel, user):
        # No game in progress, begin setup
        if self.gamestate == "None":
            self.gamestate = "Starting"
            self.bot.pubout(channel, "A new game has been started!")
            self.live_players.append(user)
            self.channel = channel
        # Game is in setup, begin game
        elif self.gamestate == "Starting":
            if user in self.live_players and len(self.live_players) > 3:
                # Game's ready to start!
                self.startgame()
            # User isn't a player, probably trying to join
            elif user not in self.live_players:
                self.reply(channel, user, "There is a game starting already. Please join instead.")
            # Not enough players
            else:
                self.reply(channel, user, "Not enough players to start a game. Minimum of 4 required. Currently: %i" % len(self.live_players))
        # Game in progress, no function
        elif self.gamestate == "InProgress":
            self.reply(channel, user, "There is a game in progress. Please wait for it to end.")

    # User command: Check game status
    def cmd_stats(self, args, channel, user):
        # No game, not status
        if self.gamestate == "None":
            self.reply(channel, user, "No game in progress.")
        # Game is starting, output currently joined players
        elif self.gamestate == "Starting":
            self.reply(channel, user, "A new game is starting. Currently %i players: %s" % (len(self.live_players), ", ".join(self.live_players)))
        # Game is in progress, output players, score, green card
        elif self.gamestate == "InProgress":
            self.bot.pubout(self.channel, "Player order: %s. %s is the current judge. Current green card is: \x033%s\x0F" % (", ".join(self.live_players), self.live_players[self.judgeindex], self.greencard))
            greenbuild = []
            for player in self.players:
                if len(self.woncards[player]) != 0:
                    greenbuild.append("%i - %s" % (len(self.woncards[player]), player))
            greenbuild.sort(reverse=True)
            if greenbuild != []:
                self.bot.pubout(self.channel, "Green cards per players: %s. Cards to win: %i." % (", ".join(greenbuild), self.cardstowin))
            else:
                self.bot.pubout(self.channel, "No scores yet. Cards to win: %i." % self.cardstowin)
    
    # User command: Alias to cmd_stats
    def cmd_status(self, args, channel, user):
        self.cmd_stats(args, channel, user)
    
    # User command: Check game score
    def cmd_scores(self, args, channel, user):
        # No game or in setup, no score
        if self.gamestate == "None" or self.gamestate == "Starting":
            self.reply(channel, user, "No game in progress.")
        # Output players and score list
        elif self.gamestate == "InProgress":
            greenbuild = []
            for player in self.players:
                if len(self.woncards[player]) != 0:
                    greenbuild.append("%i - %s" % (len(self.woncards[player]), player))
            greenbuild.sort(reverse=True)
            if greenbuild != []:
                self.bot.pubout(self.channel, "Green cards per players: %s. Cards to win: %i." % (", ".join(greenbuild), self.cardstowin))
            else:
                self.bot.pubout(self.channel, "No scores yet. Cards to win: %i." % self.cardstowin)

    # User command: Join the game
    def cmd_join(self, args, channel, user):
        # No game, can't join one
        if self.gamestate == "None":
            self.reply(channel, user, "No game in progress. Please start one.")
        # Game in setup, go ahead and join
        elif self.gamestate == "Starting":
            if user not in self.live_players:
                self.live_players.append(user)
                self.bot.pubout(self.channel, "%s is now in the game." % user)
            else:
                self.reply(channel, user, "You are already in the game.")
        # Game in progress, join, and generate a blank slate for the player
        elif self.gamestate == "InProgress":
            if user not in self.live_players:
                self.bot.pubout(self.channel, "%s is now in the game." % user)
                if user not in self.players:
                    self.players.append(user)
                if user not in self.woncards:
                    self.woncards[user] = []
                self.live_players.insert(self.judgeindex, user)
                self.judgeindex = self.judgeindex + 1
                if user not in self.hands:
                    self.hands[user] = []
                    for i in range(1, 8):
                        self.hands[user].append(self.reddeck.pop(0))
                    self.hands[user].sort()
                else:
                    while len(self.hands[user]) < 7:
                        self.hands[user].append(self.reddeck.pop(0))
                        self.privreply(user, "You draw: \x034%s\x0F: %s" % (self.hands[user][len(self.hands[user])-1], REDCARDS[self.hands[user][len(self.hands[user])-1]]))
                hand = []
                for i in range (1, 8):
                    hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
                self.privreply(user, "Your hand: %s" % ", ".join(hand))
            else:
                self.reply(channel, user, "You are already in the game.")
    
    # User command: View hand
    def cmd_hand(self, args, channel, user):
        # Is the game in progress?
        if self.gamestate == "InProgress":
            # Is the player in the game?
            if user in self.live_players:
                # Yep, here's their hand!
                hand = []
                for i in range (1, len(self.hands[user]) + 1):
                    hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
                self.privreply(user, "Your hand: %s" % ", ".join(hand))
            else:
                # Not a player, no hand.
                self.reply(channel, user, "You are not in this game.")
        else:
            # No game, no hands.
            self.reply(channel, user, "There is no game in progress.")
    
    # User command: View cards won
    def cmd_greens(self, args, channel, user):
        # Is the game in progress?
        if self.gamestate == "InProgress":
            # Is the user in the game?
            if user in self.live_players:
                # Yep! Output the cards they've won
                if len(self.woncards[user]) != 0:
                    hand = []
                    for i in range (1, len(self.woncards[user]) + 1):
                        hand.append("%i: \x02\x033%s\x0F" % (i, self.woncards[user][i-1]))
                    self.privreply(user, "Your green cards: %s" % ", ".join(hand))
                else:
                    # No won cards :(
                    self.privreply(user, "You do not have any green cards.")
            else:
                # Not a player
                self.reply(channel, user, "You are not in this game.")
        else:
            # Not a game
            self.reply(channel, user, "There is no game in progress.")
    
    # User command: Prompt inactive players
    def cmd_prompt(self, args, channel, user):
        # Is the game in progress?
        if self.gamestate == "InProgress":
            # Are we in judge phase?
            if self.judging == False:
                # Find the players holding up the game, and tell them to play
                finishedplayers = [self.judgeindex]
                for card in self.playedcards:
                    finishedplayers.append(card[0])
                unfinishedplayers = []
                for player in self.live_players:
                    if player not in finishedplayers:
                        unfinishedplayers.append(player)
                unfinishedplayers.remove(self.live_players[self.judgeindex])
                self.bot.pubout(channel, "%s: Please play a card." % ", ".join(unfinishedplayers))
            else:
                # Tell the judge to pick
                self.bot.pubout(channel, "%s: Please pick a card to win." % self.live_players[self.judgeindex])
        else:
            # No game
            self.reply(channel, user, "There is no game in progress.")
            
    # User command: Quit the game
    def cmd_quit(self, args, channel, user):
        # Game in progress, remove user and deal with aftermath
        if self.gamestate == "InProgress":
            # Is the user playing?
            if user in self.live_players:
                # Store current judge for later checks
                judge = self.live_players[self.judgeindex]
                
                # Remove the player and inform other players
                self.bot.pubout(self.channel, "%s has quit the game." % user)
                self.live_players.remove(user)
                
                # 2 players is too little to keep going.
                if len(self.live_players) < 3:
                    self.bot.pubout(self.channel, "There are now too few players to continue the game.")
                    self.endgame()
                else:
                    # Normal judge wraparound if the removed player was last in line
                    if self.judgeindex == len(self.live_players):
                        self.judgeindex = 0
                    # Is the quitter the judge?
                    if user == judge:
                        # Select a new judge
                        self.bot.pubout(self.channel, "The judge is now %s." % self.live_players[self.judgeindex])
                        judge = self.live_players[self.judgeindex]
                        # Remove the new judge's card
                        for i in range(0, len(self.playedcards)):
                            if self.playedcards[i-1][0] == judge:
                                self.playedcards.remove(self.playedcards[i-1])
                    else:
                      # Find the old judge in the modified array
                      self.judgeindex = self.live_players.index(judge)
                # Necessary if the player who quit was either the last
                # who needed to play, or the judge (to restart judging)
                self.checkroundover()
            else:
                # How can you quit something you aren't doing?
                self.reply(channel, user, "You are not in this game.")
        # Game setup, remove user's intent to join
        elif self.gamestate == "Starting":
            # Take them out of the game
            if user in self.live_players:
                self.bot.pubout(self.channel, "%s has quit the game." % user)
                self.live_players.remove(user)
                # If it's empty, just end it
                if len(self.live_players) == 0:
                    self.bot.pubout(self.channel, "Game is now empty.")
                    self.endgame()
            else:
                # Not in the game
                self.reply(channel, user, "You are not in this game.")
        else:
            # No game, nothing to quit
            self.reply(channel, user, "There is no game in progress.")
    
    # Moderator command: Delete a player
    def cmd_del(self, args, channel, user):
        # Create a handler for authorization
        auth = self.bot.plugins['system.Auth']
        # Is the user authorized to do this?
        userlevel = auth.get_userlevel(user)
        if userlevel > 50:
            # Game in progress, remove the player
            if self.gamestate == "InProgress":
                try:
                    # Does the player exist?
                    player = args[0]
                    if player in self.live_players:
                        # Hold the judge for later checks
                        judge = self.live_players[self.judgeindex]
                        # Remove the player
                        self.bot.pubout(self.channel, "%s has quit the game." % player)
                        self.live_players.remove(player)
                        # 2 is too few to continue
                        if len(self.live_players) < 3:
                            self.bot.pubout(self.channel, "There are now too few players to continue the game.")
                            self.endgame()
                        else:
                            # Normal judge array wraparound
                            if self.judgeindex == len(self.live_players):
                                self.judgeindex = 0
                            # Was the deleted player the judge?
                            if player == judge:
                                # Assign a new judge and remove their card if in play
                                self.bot.pubout(self.channel, "The judge is now %s." % self.live_players[self.judgeindex])
                                judge = self.live_players[self.judgeindex]
                                for i in range(0, len(self.playedcards)):
                                    if self.playedcards[i][0] == judge:
                                        self.playedcards.remove(self.playedcards[i])
                            else:
                                # Find the old judge in the modified array
                                self.judgeindex = self.live_players.index(judge)
                        # Necessary if deleted player is last required to play
                        # or the judge (to restart judging).
                        self.checkroundover()
                    else:
                        # Not alive
                        self.reply(channel, user, "That player is not in this game.")
                except IndexError:
                    # Not a player
                    self.reply(channel, user, "Please specify the player to delete.")
            else:
                # Not a game
                self.reply(channel, user, "There is no game in progress.")
        # Game is starting, remove player's intent to join
        elif self.gamestate == "Starting":
            try:
                # Does this player exist?
                player = args[0]
                if player in self.live_players:
                    # Remove them.
                    self.bot.pubout(self.channel, "%s has been deleted from the game." % player)
                    self.live_players.remove(player)
                    if len(self.live_players) == 0:
                        # The game is empty, end it.
                        self.bot.pubout(self.channel, "Game is now empty.")
                        self.endgame()
                else:
                    # Not in the game
                    self.reply(channel, user, "That player is not in this game.")
            except IndexError:
                # Not a player
                self.reply(channel, user, "Please specify the player to delete.")
        else:
            # Not authorized
            self.reply(channel, user, "You need to be at least a botmod to use that command.")
    
    # Moderator command: End the game
    def cmd_end(self, args, channel, user):
        # Create a handler for authentication
        auth = self.bot.plugins['system.Auth']
        # Is the user authorized to do this?
        userlevel = auth.get_userlevel(user)
        if userlevel > 50:
            # Is a game running?
            if self.gamestate is not "None":
                # Yep, close it down.
                self.endgame()
            else:
                # Nope. Why is this being run?
                self.reply(channel, user, "There is no game in progress.")
        else:
            # Not authorized
            self.reply(channel, user, "You need to be at least a botmod to use that command during a game.")
    
    # User command: List commands.
    def cmd_help(self, args, channel, user):
        # Put all commands into an array
        cmds = [i[4:] for i in dir(self) if i.startswith('cmd_')]
        # Send to user
        self.reply(channel, user, "Valid commands: '%s'" % "', '".join(cmds))

    # User command: View rules.
    def cmd_rules(self, args, channel, user):
        # Output a simple game description.
        self.reply(channel, user, "Apples to Apples is a very simple, yet surprisingly fun, party game. Playing is easy! Just say !join to join a game, or !start to begin one if there are none starting. Every player gets 7 cards, replenished at the start of each round. A green card is also selected at the start of each round.")
        self.reply(channel, user, "If you are not judging, use !play [number from your hand] to play a card, preferably related to the green card. If you are judging, wait for everyone to play. You can use !prompt to see who has not yet played a card. If you forget your hand, use !hand to see it again. If you want to read a card, use !peek [number from your hand]. To see the green cards you have one, say !greens.")
        self.reply(channel, user, "After all players have put down a card, the Judge gets to choose the winner, with !pick [number]. There is no set criteria to determine the 'best' card. The judge simpy picks the card they like the most! It could be the one that fits the green card best, or the one they find the funniest. It's up to the judge! Players can only learn what the judges like, and use that to their advantage.")
    
    # Run a user command on correct input
    def do_command(self, channel, user, cmd):
        # No command, nothing to do
        if cmd=='': return
        
        # Split the input into [command, arguments] and make lowercase
        cmds = cmd.strip().split(" ")
        cmds[0]=cmds[0].lower()
        
        # Does this command exist?
        try:
            # Search for the command function and make a handler
            cmd_handler = getattr(self, "cmd_" + cmds[0])
        except AttributeError:
            # Doesn't exist
            cmd_handler = None

        # If it exists, pass args and run the command.
        if cmd_handler:
            cmd_handler(cmds[1:], channel, user)
            return
