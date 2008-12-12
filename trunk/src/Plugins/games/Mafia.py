#!/usr/bin/env python
##
##    Mafia - a plugin for pyGBot
##    Copyright (C) 2008 Ben Collins-Sussman, Max Bowsher, Karl Fogel,
##                       McClain Looney, Morgan Lokhorst-Blight,
##                       Alex Soborov
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
#
# IRC Bot to moderate a game of "Mafia".
#
# Mafia is a traditional party game, sometimes known as 'Mafia',
# with dozens of variants.  This bot is following Andrew Plotkin's rules:
# http://www.eblong.com/zarf/Mafia.html
#
# Code originally based on example bot and irc-bot class from
# Joel Rosdahl <joel@rosdahl.net>, author of python-irclib.
#

"""A PyGBot plugin to for a game of "Mafia".

The main commands are:

    start game -- start a new Mafia game.

    end game -- quit the current Mafia game (you must have started it)

    stats -- print information about state of game-in-progress.

"""

import sys, string, random, time
import log
from BasePlugin import BasePlugin

#if self.bot.has_key("ChanOp"):
#    chanops = self.bot.plugins["ChanOp"]
#    self.chanoppowers = True
#else:
#	self.chanoppowers = False

#---------------------------------------------------------------------
# General texts for narrating the game.  Change these global strings
# however you wish, without having to muck with the core logic!

minUsers=3

svn_url = \
"$URL: http://ircbot-collection.googlecode.com/svn/trunk/mafiabot.py $"
svn_url = svn_url[svn_url.find(' ')+1:svn_url.rfind('/')+1]

# Printed when a game first starts:

new_game_texts = \
["This is a game of paranoia and psychological intrigue.  Everyone in this group appears to be a common citizen, but several of you are 'special'. \
 One or two of you are actually in the Mafia, trying to kill everyone while concealing their identity.",

 "One of you is also a 'sheriff'; you have the ability to learn whether a specific person is or is not in the Mafia.",
 
 "And another is the 'doctor'; you have the ability to save someone's life, if you pick the player who is chosen by the Mafia.",

 "As a community, your group objective is to weed out the Mafia and lynch them before you're all killed in your sleep."]

# Printed when informing players of their initial roles:

mafia_intro_text = \
"You are a \x034Mafia\x0f\x02.  You want to kill everyone while they sleep. Whatever happens, keep your identity secret.  Act natural!"

sheriff_intro_text = \
"You're a citizen, but also a \x034sheriff\x0f\x02.  Later on, you'll get chances to learn whether someone is or isn't a Mafia.  Keep your identity secret, or the Mafia may kill you!"

doctor_intro_text= \
"You're a citizen, but also a \x034doctor\x0f\x02.  Later on, you'll get chances to save people who are targetted by the Mafia.  Keep your identity secret, or the Mafia may kill you!"

citizen_intro_text = \
"You're an ordinary citizen."


# Printed when night begins:

night_game_texts = \
["Darkness falls:  it is \x034night\x0f\x02. The city sleeps peacefully..."]

# Printed when Mafia and citizen get nighttime instructions:

night_sheriff_texts = \
["At night, you have the ability to check whether a certain person\
  is or is not a Mafia. You must use this power now: please type 'check <nickname>' (as a\
 private message to me) to learn about one living player's true\
 identity."]
 
night_doctor_texts = \
["At night, you have the ability to attempt to save someone's life\
  if they are chosen by the Mafia. You do not need to use this power now: type 'save <nickname>' (as\
  a private message to me) to attempt to save them, or 'nosave' to\
  not attempt it this night."]

night_Mafia_texts = \
["As the citizens sleep, you must now decide whom you want to kill. You and the other Mafia (if he is exists and is alive) should discuss (privately) and choose a victim. Please type 'kill <nickname>' (as a private message to me)."]


# Printed when day begins.

day_game_texts = \
["Paranoia runs through the city!  Who is a Mafia in disguise? The citizens *must* decide to lynch one player. When each player is ready, send me the command:  'lynch <nickname>', and I will keep track of votes, until the majority agrees."]




#---------------------------------------------------------------------
# Actual code.
#
# Modified from using the bot class to being a pyGBot plugin

IRC_BOLD = "\x02"

class Mafia(BasePlugin):
    GAMESTATE_NONE, GAMESTATE_STARTING, GAMESTATE_RUNNING = range(3)
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.output = True
        self.moderation = True

    def activate(self, channel=None):
        if channel == None:
            return False
        self.channel = channel
        self._reset_gamedata()
        #self.start()

    def user_nickchange(self, channel, old, new):
        for list_ in (self.live_players, self.dead_players, self.Mafia,
                self.citizens, self.originalMafia):
            if old in list_:
                list_.append(new)
                list_.remove(old)
        for map_ in (self.mafia_votes, self.citizen_votes, self.tally):
            if map_.has_key(new):
                map_[new] = map_[old]
                del map_[old]
        for map_ in (self.mafia_votes, self.citizen_votes):
            for k, v in map_.items():
                if v == old:
                    map_[k] = new
        for var in ('game_starter', 'sheriff', 'sheriff_target', 'mafia_target', 'doctor', 'doctor_target'):
            if getattr(self, var) == old:
                setattr(self, var, new)

    def _removeUser(self, nick):

        channel = self.channel

        if nick == self.game_starter:
            self.game_starter = None
        if nick in self.live_players:
            self.bot.pubout(channel, "%s disappeared in some sort of strange wormhole." % nick)
            self.live_players.remove(nick)
            if self.gamestate == self.GAMESTATE_STARTING:
                # No more to do
                return
            self.dead_players.append(nick)
            if nick in self.Mafia:
                self.Mafia.remove(nick)
                self.bot.pubout(channel, "%nick was in the Mafia. Apparently someone made them an offer they couldn't refuse." % (nick,nick))
            if nick in self.citizens:
                self.citizens.remove(nick)
                self.bot.pubout(channel, "%s had a boring position in the game, that of a citizen. Hopefully death will be more interesting." % nick)
            if nick in self.doctor:
                self.bot.pubout(channel, "%s was a doctor. The hospitals are baffled at this unexpected erasure from reality.")
            if nick == self.doctor_target:
                self.bot.noteout(self.doctor, "Due to %s's unexpected erasure from reality, you may Save once again this night." % nick)
                self.doctor_target = None
            if nick == self.sheriff:
                self.bot.pubout(channel, "%s was a sheriff. The police force is mad that all their sheriffs get destroyed by timespace anomalies." % nick)
            if nick == self.sheriff_target:
                self.bot.noteout(self.sheriff, "Due to %s's unexpected erasure from reality, you may Check once again this night." % nick)
                self.sheriff_target = None
            if nick == self.mafia_target:
                for mafia in self.Mafia:
                    self.bot.noteout(mafia, "Due to %s's unexpected erasure from reality, you can choose someone else to kill tonight." % nick)
                self.mafia_target = None
            for map_ in (self.mafia_votes, self.citizen_votes, self.tally):
                if map_.has_key(nick):
                    del map_[nick]
            for map_ in (self.mafia_votes, self.citizen_votes):
                for k, v in map_.items():
                    if v == nick:
                        del map_[k]
            self.check_game_over()


    def msg_notice(self, c, e):
        source = u


    GAME_STARTER_TIMEOUT_MINS = 4
    def check_game_control(self, u, e):
        "Implement a timeout for game controller."
        if self.game_starter is None:
            return
        nick = u
        if self.game_starter == nick:
            self.game_starter_last_checkn = time.time()
        else:
            if self.game_starter_last_checkn < (
                    time.time() - self.GAME_STARTER_TIMEOUT_MINS * 60):
                self.bot.pubout(self.channel, "Game starter '%s' has been silent for %d minutes. "
                        "Game control is now open to all." % (self.game_starter,
                            self.GAME_STARTER_TIMEOUT_MINS))
                self.game_starter = None

    def msg_private(self, user, message):
        self.check_game_control(user, message)
        self.do_command(user, user, message)


    def user_part(self, channel, user):
        self._removeUser(user)

    #def user_kick(self, channel, user):
    #    self._removeUser(user)

    def msg_channel(self, channel, user, message):
        self.check_game_control(user, message)
        a = string.split(message, ":", 1)
        if len(a) > 1 and a[0].lower() == self.bot.nickname.lower():
            self.do_command(channel, user, string.strip(a[1]))
        elif message[0]=='!' and (len(message) > 1) and message[1]!='!':
            self.do_command(channel, user, string.strip(message[1:]))

    def _reset_gamedata(self):
        self.opmode = False
        self.gamestate = self.GAMESTATE_NONE
        self.time = None
        self.game_starter = None
        self.game_starter_last_checkn = 0
        self.live_players = []
        self.dead_players = []
        self.Mafia = []
        self.citizens = []
        self.sheriff = None
        self.doctor = None
        self.originalMafia = []
        # Night round variables
        self.sheriff_target = None
        self.doctor_target = None
        self.doctor_chosen = False
        self.mafia_target = None
        self.mafia_votes = {}
        # Day round variables
        self.citizen_votes = {}
        self.tally = {}


    def reply(self, channel, user, text):
        "Send TEXT to public channel or as private msg, in reply to event E."
        if channel != user:
            self.bot.pubout(channel, "%s: %s" % (user, text))
        else:
            self.bot.noteout(user, text)


    def start_game(self, game_starter):
        "Initialize a Mafia game -- assign roles and notify all players."
        #chname, chobj = self.channels.items()[0]
        channel = self.channel
        
        if self.gamestate == self.GAMESTATE_RUNNING:
            self.bot.pubout(channel, "A game started by %s is in progress; "
                    "that person must end it." % self.game_starter)
            return

        if self.gamestate == self.GAMESTATE_NONE:
            self._reset_gamedata()
            self.gamestate = self.GAMESTATE_STARTING
            self.game_starter = game_starter
            self.game_starter_last_checkn = time.time()
            self.live_players.append(game_starter)
            self.bot.pubout(channel, "A new game has been started by %s; "
                    "say '%s: join' to join the game."
                    % (self.game_starter, self.bot.nickname))
            self.bot.pubout(channel, "%s: Say '%s: start' when everyone has joined."
                    % (self.game_starter, self.bot.nickname))
            #self.fix_modes()
            return

        if self.gamestate == self.GAMESTATE_STARTING:
            if self.game_starter and game_starter != self.game_starter:
                self.bot.pubout(channel, "Game startup was begun by %s; "
                        "that person must finish starting it." % self.game_starter)
                return
            self.game_starter = game_starter
            self.game_starter_last_checkn = time.time()

            if len(self.live_players) < minUsers:
                self.bot.pubout(channel, "Sorry, to start a game, there must be " + \
                                                "at least active %d players."%(minUsers))
                self.bot.pubout(channel, ("I count only %d active players right now: %s."
                    % (len(self.live_players), self.live_players)))

            else:
                # Randomly select two Mafia and a sheriff and a doctor. Everyone else is a citizen.
                users = self.live_players[:]
                self.bot.pubout(channel, "A new game has begun! Please wait, assigning roles...")
                self.Mafia.append(users.pop(random.randrange(len(users))))
	if len(self.live_players) > 12:
	    self.Mafia.append(users.pop(random.randrange(len(users))))
	    self.Mafia.append(users.pop(random.randrange(len(users))))
	    self.Mafia.append(users.pop(random.randrange(len(users))))
	    self.bot.pubout(channel, "There are four Mafia.")
	elif len(self.live_players) > 8:
	    self.Mafia.append(users.pop(random.randrange(len(users))))
	    self.Mafia.append(users.pop(random.randrange(len(users))))
	    self.bot.pubout(channel, "There are three Mafia.")
	elif len(self.live_players) > 6:
	    self.Mafia.append(users.pop(random.randrange(len(users))))
	    self.bot.pubout(channel, "There are two Mafia.")
	else:
	    self.bot.pubout(channel, "There is only one Mafia.")
        self.originalMafia = self.Mafia[:]
        self.sheriff = users.pop(random.randrange(len(users)))
        self.doctor = users.pop(random.randrange(len(users)))
        
        for user in users:
            self.citizens.append(user)

        # Private message each user, tell them their role.
        self.bot.noteout(self.sheriff, sheriff_intro_text)
        self.bot.noteout(self.doctor, doctor_intro_text)
        for mafia in self.Mafia:
            self.bot.noteout(mafia, mafia_intro_text)
        for citizen in self.citizens:
            self.bot.noteout(citizen, citizen_intro_text)

        #self.debug = True
        #if self.debug:
        #    print "SHERIFF: %s, MAFIA: %s, doctor %s" % (self.sheriff, self.Mafia, self.doctor)

        self.bot.pubout(channel, "Assigning roles now... To learn how to play, say 'Siobhan: rules'.")
        self.gamestate = self.GAMESTATE_RUNNING

        #self.fix_modes()

        # Start game by putting bot into "night" mode.
        self.night()


    def end_game(self, game_ender):
        "Quit a game in progress."

        channel = self.channel

        if self.gamestate == self.GAMESTATE_NONE:
            self.bot.pubout(channel, \
                             "No game is in progress.    Use 'start' to begin a game.")
        elif self.game_starter and game_ender != self.game_starter:
            self.bot.pubout(channel, \
                ("Sorry, only the starter of the game (%s) may end it." %\
                 self.game_starter))
        else:
            self.bot.pubout(channel, "The game has ended.")
            if self.gamestate == self.GAMESTATE_RUNNING:
                self.reveal_all_identities()
            self._reset_gamedata()
            self.gamestate = self.GAMESTATE_NONE
            #self.fix_modes()


    def reveal_all_identities(self):
        "Print everyone's identities."

        channel = self.channel

        if len(self.originalMafia)==2:
            self.bot.pubout(channel, ("*** The two Mafia were %s and %s, the sheriff was %s, the doctor was %s. "
                "Everyone else was a normal citizen"
                % (self.originalMafia[0], self.originalMafia[1], self.sheriff, self.doctor)))
        else:
            self.bot.pubout(channel, ("*** The mafia was %s, the sheriff was %s, the doctor was %s. "
                "Everyone else was a normal citizen"
	% (self.originalMafia[0], self.sheriff, self.doctor)))

    def check_game_over(self):
        """End the game if either citizens or Mafia have won.
        Return 1 if game is over, 0 otherwise."""

        channel = self.channel

        # If all Mafia are dead, the citizens win.
        if len(self.Mafia) == 0:
            self.bot.pubout(channel, "The Mafia are dead!    The \x034citizens\x0f\x02 have \x034won\x0f.")
            self.end_game(self.game_starter)
            return 1

        # If the number of non-Mafia is the same as the number of Mafia,
        # then the Mafia win.
        if (len(self.live_players) - len(self.Mafia)) == len(self.Mafia):
            self.bot.pubout(channel, \
                "There are now an equal number of citizens and Mafia.")
            msg = "The Mafia have no need to hide anymore; "
            msg = msg + "They attack the remaining citizens. "
            msg = msg + "The \x034Mafia\x0f\x02 have \x034won\x0f."
            self.bot.pubout(channel, msg)
            self.end_game(self.game_starter)
            return 1

        return 0


    def check_night_done(self):
        "Check if nighttime is over.    Return 1 if night is done, 0 otherwise."

        # Is the sheriff done checking?
        if self.sheriff not in self.live_players:
            sheriff_done = 1
        else:
            if self.sheriff_target is None:
                sheriff_done = 0
            else:
                sheriff_done = 1
                
        # Is the doctor done checking?
        if self.doctor not in self.live_players:
            doctor_done = 1
        else:
            if self.doctor_chosen == False:
                doctor_done = 0
            else:
                doctor_done = 1

        if (self.mafia_target is not None) and sheriff_done and doctor_done:
            return 1
        else:
            return 0


    def night(self):
        "Declare a NIGHT episode of gameplay."

        #chname, chobj = self.channels.items()[0]
        channel = self.channel
        
        self.time = "night"

        # Clear any daytime variables
        self.citizen_votes = {}
        self.tally = {}

        # Declare nighttime.
        self.print_alive()
        for text in night_game_texts:
            self.bot.pubout(channel, text)

        # Give private instructions to Mafia and sheriff and doctor.
        if self.sheriff in self.live_players:
            for text in night_sheriff_texts:
                self.bot.noteout(self.sheriff, text)
        if self.doctor in self.live_players:
            for text in night_doctor_texts:
                self.bot.noteout(self.doctor, text)
        for text in night_Mafia_texts:
            for mafia in self.Mafia:
                self.bot.noteout(mafia, text)
        if len(self.Mafia) >= 2:
            self.bot.noteout(self.Mafia[0],\
                                             ("The other Mafia is %s.    Confer privately."\
                                                % self.Mafia[1]))
            self.bot.noteout(self.Mafia[1],\
                                             ("The other Mafia is %s.    Confer privately."\
                                                % self.Mafia[0]))

        # ... bot is now in 'night' mode;    goes back to doing nothing but
        # waiting for commands.


    def day(self):
        "Declare a DAY episode of gameplay."

        channel = self.channel

        self.time = "day"

        # Discover the dead mafia victim.
        self.bot.pubout(channel, "\x034Day\x0f\x02 Breaks!    Sunlight pierces the sky.")
        if self.doctor_target != self.mafia_target:
            self.bot.pubout(channel, ("The city awakes in horror..." + \
                                         "to find the mutilated body of \x034%s\x0f\x02!!"\
                                         % self.mafia_target))

        if not self.kill_player(self.mafia_target):
            # Clear all the nighttime voting variables:
            self.sheriff_target = None
            self.doctor_target = None
            self.doctor_chosen = False
            self.mafia_target = None
            self.mafia_votes = {}

            # Give daytime instructions.
            self.print_alive()
            for text in day_game_texts:
                self.bot.pubout(channel, text)

            # ... bot is now in 'day' mode;    goes back to doing nothing but
            # waiting for commands.



    def check(self, channel, user, who):
        "Allow a sheriff to 'check' somebody."

        if self.time != "night":
            self.reply(channel, user, "Are you a sheriff?    In any case, it's not nighttime.")
        else:
            if user  != self.sheriff:
                self.reply(channel, user, "Huh?")
            else:
                if who not in self.live_players:
                    self.reply(channel, user, "That player either doesn't exist, or is dead.")
                else:
                    if self.sheriff_target is not None:
                        self.reply(channel, user, "You've already had your vision for tonight.")
                    else:
                        self.sheriff_target = who
                        if who in self.Mafia:
                            self.reply(channel, user, "You're sure that player is a Mafia!")
                        else:
                            self.reply(channel, user, "You're sure that player is a normal citizen.")
                            
                        if self.check_night_done():
                            self.day()
                            
                            
    def save(self, channel, user, who):
        "Allow a doctor to 'save' somebody."

        if self.time != "night":
            self.reply(channel, user, "Are you a doctor?    In any case, it's not nighttime.")
        else:
            if user  != self.doctor:
                self.reply(channel, user, "Huh?")
            else:
                if who not in self.live_players:
                    self.reply(channel, user, "That player either doesn't exist, or is dead.")
                else:
                    if self.doctor_chosen is not False:
                        self.reply(channel, user, "You've already chosen someone to save tonight.")
                    elif who == user:
                        self.reply(channel, user, "You can't save yourself!")
                    else:
                        self.doctor_target = who
                        self.doctor_chosen = True
                        self.reply(channel, user, "Tonight, you will attempt to save the player %s." % who)
                        if self.check_night_done():
                            self.day()
                            
    def nosave(self, channel, user):
        "The doctor decides not to save anyone."
        
        if self.time != "night":
            self.reply(channel, user, "Are you a doctor?    In any case, it's not nighttime.")
        else:
            if user != self.doctor:
                self.reply(channel, user, "Huh?")
            else:
                self.doctor_target = None
                self.doctor_chosen = True
                self.reply(channel, user, "Tonight, no one will be saved.")
                if self.check_night_done():
                    self.day()


    def kill(self, channel, user, who):
        "Allow a Mafia to express intent to 'kill' somebody."
        if self.time != "night":
            self.reply(channel, user, "Are you a Mafia?    In any case, it's not nighttime.")
            return
        if user not in self.Mafia:
            self.reply(channel, user, "Huh?")
            return
        if who not in self.live_players:
            self.reply(channel, user, "That player either doesn't exist, or is dead.")
            return
        if len(self.Mafia) > 1:
            # Multiple Mafia are alive:
            self.mafia_votes[user] = who
            self.reply(channel, user, "Your vote is acknowledged.")

            # If all Mafia have voted, look for agreement:
            if len(self.mafia_votes) == len(self.Mafia):
                for killee in self.mafia_votes.values():
                    if who != killee:
                        break
                else:
                    self.mafia_target = who
                    self.reply(channel, user, "It is done. The Mafia agree.")
                    if self.check_night_done():
                        self.day()
                    return
                self.reply(channel, user, "Hm, I sense disagreement or ambivalence.")
                self.reply(channel, user, "You Mafia should decide on one target.")
        else:
            # only one mafia alive, no need to agree with anyone.
            self.mafia_target = who
            self.reply(channel, user, "Your decision is acknowledged.")
            if self.check_night_done():
                self.day()


    def kill_player(self, player):
        "Make a player dead.    Return 1 if game is over, 0 otherwise."

        channel = self.channel

	if self.doctor_chosen == True and self.doctor_target == player:
	    self.bot.pubout(channel, "No one was killed.")
	    self.bot.noteout(player, "You were saved by the doctor!")
	    return 0
	else:
	    self.live_players.remove(player)
            self.dead_players.append(player)
            #self.fix_modes()

            if player in self.Mafia:
                id = "a \x034mafia\x0f\x02!"
                self.Mafia.remove(player)
            elif player == self.sheriff:
                id = "the \x034sheriff\x0f\x02!"
            elif player == self.doctor:
                id = "the \x034doctor\x0f\x02!"
            else:
                id = "a normal citizen."

            self.bot.pubout(channel, \
                    ("*** Examining the body, you notice that this player was %s" % id))
            if self.check_game_over():
                return 1
            else:
                self.bot.pubout(channel, ("(%s is now dead, and should stay quiet.)") % player)
                self.bot.noteout(player, "You are now \x034dead\x0f\x02.    You may observe the game,")
                self.bot.noteout(player, "but please stay quiet until the game is over.")
                return 0


    def tally_votes(self):
        "Count votes in citizen_votes{}, store results in tally{}."

        self.tally = {}
        for key in self.citizen_votes.keys():
            lynchee = self.citizen_votes[key]
            if self.tally.has_key(lynchee):
                self.tally[lynchee] += 1
            else:
                self.tally[lynchee] = 1


    def check_for_majority(self):
        """If there is a majority of lynch-votes for one player, return
        that player's name.    Else return None."""

        majority_needed = (len(self.live_players)/2) + 1
        for lynchee in self.tally.keys():
            if self.tally[lynchee] >= majority_needed:
                return lynchee
        else:
            return None


    def print_tally(self):
        "Publically display the vote tally."

        channel = self.channel

        majority_needed = (len(self.live_players)/2) + 1
        msg = ("%d votes needed for a majority.    Current vote tally: " \
                     % majority_needed)
        for lynchee in self.tally.keys():
            if self.tally[lynchee] > 1:
                msg = msg + ("(%s : %d votes) " % (lynchee, self.tally[lynchee]))
            else:
                msg = msg + ("(%s : 1 vote) " % lynchee)
        self.bot.pubout(channel, msg)


    def print_alive(self):
        "Declare who's still alive."
        channel = self.channel
        msg = "The following players are still alive: %s"%', '.join(self.live_players)
        self.bot.pubout(channel, msg)
        if self.dead_players:
            msg = "The following players are dead : %s"%', '.join(self.dead_players)
            self.bot.pubout(channel, msg)


    def match_name(self, nick):
        """Match NICK to a username in users(), insensitively.    Return
        matching nick, or None if no match."""
        return nick

#        chname, chobj = self.channels.items()[0]
#        users = chobj.users()
#        users.remove(self._nickname)

#        for user in users:
#            if user.upper() == nick.upper():
#                return user
#        return None



    def lynch_vote(self, channel, user, lynchee):
        "Register a vote to lynch LYNCHEE."

        lyncher = user
        # sanity checks
        if self.time != "day":
            self.reply(channel, user, "Sorry, lynching only happens during the day.")
        elif lyncher not in self.live_players:
            self.reply(channel, user, "Um, only living players can vote to lynch someone.")
        elif lynchee not in self.live_players:
            self.reply(channel, user, "Um, only living players can be lynched.")
        elif lynchee == lyncher:
            self.reply(channel, user, "Um, you can't lynch yourself.")

        else:
            self.citizen_votes[lyncher] = lynchee
            self.bot.pubout(channel, ("%s has voted to lynch %s!" % (lyncher, lynchee)))
            self.tally_votes()
            victim = self.check_for_majority()
            if victim is None:
                self.print_tally()
            else:
                self.bot.pubout(self.channel, ("The majority has voted to lynch %s!! "
                    "Mob violence ensues.    This player is now \x034dead\x0f\x02." % victim))
                if not self.kill_player(victim):
                    # Day is done;    flip bot back into night-mode.
                    self.night()

    def cmd_opmode(self, args, channel, user):
        get_userlevel = self.bot.plugins['system.Auth'].get_userlevel

        if get_userlevel(user) >= 100:
            self.opmode = not self.opmode

            if self.opmode:
                self.pubout(self.channel,"%s has activated my operator mode." % user)
            else:
                self.pubout(self.channel,"%s has deactivated my operator mode." % user)

            self.do_opmode()
        else:
            self.reply(channel, user, "You do not have sufficient privileges to perform that action")

    def cmd_help(self, args, channel, user):
        cmds = [i[4:] for i in dir(self) if i.startswith('cmd_')]
        self.reply(channel, user, "Valid commands: '%s'" % "', '".join(cmds))

    def cmd_stats(self, args, channel, user):
        if self.gamestate == self.GAMESTATE_RUNNING:
            self.print_alive()
            if self.time == "day":
                self.tally_votes()
                self.print_tally()
        elif self.gamestate == self.GAMESTATE_STARTING:
            self.reply(channel, user, "A new game is starting, current players are %s"
                    % (self.live_players,))
        else:
            self.reply(channel, user, "No game is in progress.")

    def cmd_status(self, args, channel, user):
        self.cmd_stats(args, channel, user)

    def cmd_start(self, args, channel, user):
        self.start_game(user)

    def cmd_end(self, args, channel, user):
        self.end_game(user)

    def cmd_votes(self, args, channel, user):
        non_voters = []
        voters = []
        if self.citizen_votes.keys():
            for n in self.live_players:
                if not self.citizen_votes.has_key(n):
                    non_voters.append(n)
                else:
                    voters.append(n)
            if non_voters:
                self.bot.pubout(channel, "The following have no votes registered: %s"
                        % (non_voters))
	        self.bot.pubout(channel, "The votes are as follows: %s"
	                % (self.citizen_votes))
            else:
                self.bot.pubout(channel, "Everyone has voted.")
	    self.bot.pubout(channel, "The votes are as follows: %s"
	        % (self.citizen_votes))
        else:
            self.bot.pubout(channel, "Nobody has voted yet.")

    def cmd_del(self, args, channel, user):
        for nick in args:
            if nick not in self.live_players + self.dead_players:
                self.reply(channel, user, "There's nobody playing by the name %s" % nick)
            self._removeUser(nick)

    def cmd_renick(self, args, channel, user):
        if len(args) != 1:
            self.reply(channel, user, "Usage: renick <nick>")
        else:
            self.connection.nick(args[0])

    def cmd_check(self, args, channel, user):
        if len(args) == 1:
            viewee = self.match_name(args[0].strip())
            if viewee is not None:
                self.check(channel, user, viewee.strip())
                return
        self.reply(channel, user, "Check whom?")
        
    def cmd_save(self, args, channel, user):
        if len(args) == 1:
            savee = self.match_name(args[0].strip())
            if savee is not None:
                self.save(channel, user, savee.strip())
                return
        self.reply(channel, user, "Save whom?")
        
    def cmd_nosave(self, args, channel, user):
        self.nosave(channel, user)
        return

    def cmd_kill(self, args, channel, user):
        if len(args) == 1:
            killee = self.match_name(args[0].strip())
            if killee is not None:
                self.kill(channel, user, killee)
                return
        self.reply(channel, user, "Kill whom?")

    def cmd_lynch(self, args, channel, user):
        if len(args) == 1:
            lynchee = self.match_name(args[0])
            if lynchee is not None:
                self.lynch_vote(channel, user, lynchee.strip())
                return
        self.reply(channel, user, "Lynch whom?")

    def cmd_join(self, args, channel, user):
        if self.gamestate == self.GAMESTATE_NONE:
            self.reply(channel, user, 'No game is running, perhaps you would like to start one?')
            return
        if self.gamestate == self.GAMESTATE_RUNNING:
            self.reply(channel, user, 'Game is in progress; please wait for the next game.')
            return
        if user in self.live_players:
            self.reply(channel, user, 'You were already in the game!')
        else:
            self.live_players.append(user)
            self.reply(channel, user, 'You are now in the game.')
            #self.fix_modes()

    def cmd_aboutbot(self, args, channel, user):
        self.reply(channel, user, "This module is heavily modified from a bot written in Python "
                "using the python-irclib library")
        self.reply(channel, user, "The source code is available at %s" % svn_url)
       
    def cmd_rules(self, args, channel, user):
        for text in new_game_texts:
            self.bot.pubout(channel, text)

    def cmd_moderation(self, args, channel, user):
        if self.game_starter and self.game_starter != user:
            self.reply(channel, user, "%s started the game, and so has administrative control. "
                    "Request denied." % self.game_starter)
            return
        if len(args) != 1:
            self.reply(channel, user, "Usage: moderation on|off")
            return
        if args[0] == 'on':
            self.moderation = True
        elif args[0] == 'off':
            self.moderation = False
        else:
            self.reply(channel, user, "Usage: moderation on|off")
            return
        self.bot.pubout(channel, 'Moderation turned %s by %s'
                % (args[0], user))
        #self.fix_modes()

    def do_command(self, channel, user, cmd):
        """This is the function called whenever someone sends a public or
        private message addressed to the bot. (e.g. "bot: blah").    Parse
        the CMD, execute it, then reply either to public channel or via
        /msg, based on how the command was received.    E is the original
        event, and FROM_PRIVATE is the nick that sent the message."""
        if cmd=='': return
        cmds = cmd.strip().split(" ")
        cmds[0]=cmds[0].lower()
        #if self.debug and e.eventtype() == "pubmsg":
        #    if cmds[0][0] == '!':
        #        e._source = cmds[0][1:] + '!fakeuser@fakehost'
        #        cmds = cmds[1:]

        # Dead players should not speak.
        if user in self.dead_players:
            if (cmd != "stats") and (cmd != "status") and (cmd != "help"):
                self.reply(channel, user, "Please -- dead players should keep quiet.")
                return 0

        try:
            cmd_handler = getattr(self, "cmd_" + cmds[0])
        except AttributeError:
            cmd_handler = None

        if cmd_handler:
            cmd_handler(cmds[1:], channel, user)
            return

        # unknown command:    respond appropriately.

        # reply either to public channel, or to person who /msg'd
        if self.time is None:
            #self.reply(channel, user, "That command makes no sense.")
            pass
        elif self.time == "night":
            #self.reply(channel, user, "SSSHH! It's night, everyone's asleep!")
            pass
        elif self.time == "day":
            #self.reply(channel, user, "Hm? Get back to lynching.")
            pass
