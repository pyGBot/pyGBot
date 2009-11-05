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

import sys, string, random, time, re, itertools

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin

#if self.bot.has_key("ChanOp"):
#    chanops = self.bot.plugins["ChanOp"]
#    self.chanoppowers = True
#else:
#    self.chanoppowers = False

#---------------------------------------------------------------------
# General texts for narrating the game.  Change these global strings
# however you wish, without having to muck with the core logic!

minUsers=4

svn_url = \
"$URL: http://ircbot-collection.googlecode.com/svn/trunk/mafiabot.py $"
svn_url = svn_url[svn_url.find(' ')+1:svn_url.rfind('/')+1]

# Printed when a game first starts:

new_game_texts = \
["This is a game of paranoia and psychological intrigue.  Everyone in this group appears to be a common citizen, but several of you are 'special'. \
 A small amount of you are actually in the Mafia, trying to kill everyone while concealing their identity.",

 "One of you is also a 'sheriff'; you have the ability to learn whether a specific person is or is not in the Mafia.",
 
 "Another is the 'detective; you have the ability to see roles upon player deaths."
 
 "And yet another is the 'doctor'; you have the ability to save someone's life, if you pick the player who is chosen by the Mafia.",
 
 "One of the Mafia may also be an 'agent'; they have the ability to alter the Sheriff's files at night.",

 "As a community, your group objective is to weed out the Mafia and lynch them before you're all killed in your sleep."]

# Printed when informing players of their initial roles:

mafia_intro_text = \
"You're a \x02\x034Mafia\x0f.  You want to \x02kill\x0f everyone while they sleep. Whatever happens, keep your identity secret.  Act natural!"

agent_intro_text = \
"You're a \x02\x034Mafia\x0f, but also an \x02\x034agent\x0f. Later on, you'll get chances to \x02alter\x0f the 'files' the Sheriff checks to keep the Mafia a secret, or put suspicion on a villager. Act natural!"

sheriff_intro_text = \
"You're a \x02citizen\x0f, but also a \x02\x034sheriff\x0f.  Later on, you'll get chances to \x02check\x0f whether someone is or isn't a Mafia.  Keep your identity secret, or the Mafia may kill you!"

doctor_intro_text= \
"You're a \x02citizen\x0f, but also a \x02\x034doctor\x0f.  Later on, you'll get chances to \x02save\x0f people who are targeted by the Mafia.  Keep your identity secret, or the Mafia may kill you!"

detective_intro_text = \
"You're a \x02citizen\x0f, but also a \x02\x034Detective\x0f. Later on, you'll \x02learn\x0f the roles of the players killed by the Mafia. Keep your identity secret, or the Mafia may kill you!"

citizen_intro_text = \
"You're a \x02citizen\x0f."


# Printed when night begins:

night_game_texts = \
["Darkness falls:  it is \x02\x034night\x0f. The city sleeps peacefully..."]

# Printed when Mafia and citizen get nighttime instructions:

night_sheriff_texts = \
["Every night, you have the ability to check whether a certain person\
  is or is not a Mafia. You must use this power now: please type 'check <nickname>' (as a\
 private message to me) to learn about one living player's true\
 identity."]
 
night_doctor_texts = \
["Every night, you have the ability to attempt to save someone's life\
  if they are chosen by the Mafia. You do not need to use this power now: type 'save <nickname>' (as\
  a private message to me) to attempt to save them, or 'nosave' to\
  not attempt it this night."]

night_Mafia_texts = \
["As the citizens sleep, you may now decide whom you want to kill. You and the other Mafia (if they is exist and are alive) should discuss (privately) and choose a victim. Please type 'kill <nickname>' (as a private message to me). Alternatively, you can elect not to kill anyone. To do this, please type 'nokill' (as a private message to me)."]

night_agent_texts = \
["As the citizens sleep, you may now decide to alter the Sheriff's files.\
  You do not need to use this power now: type 'alter <nickname>' (as\
  a private message to me) to change the file, or 'noalter' to\
  not change any files tonight."]

# Printed when day begins.

day_game_texts = \
["The citizens may decide to lynch one player. When each player is ready, send me the command:  'lynch <nickname>' or 'nolynch', and I will keep track of votes, until the majority agrees. You can undo a lynch vote with 'unlynch'."]




#---------------------------------------------------------------------
# Actual code.
#
# Modified from using the bot class to being a pyGBot plugin

IRC_BOLD = "\x02"

class Mafia(BasePlugin):
    GAMESTATE_NONE, GAMESTATE_STARTING, GAMESTATE_RUNNING = range(3)
    NOLYNCH = 0
    NOKILL = 1
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.output = True
        self.moderation = True
        self.timer = 0
        if self.bot.plugins.has_key("system.Modes"):
            self.modeplugin = self.bot.plugins["system.Modes"]
        else:
            self.modeplugin = None

    def activate(self, channel=None):
        if channel == None:
            return False
        self.channel = channel
        self.dchatchannel = channel + "-dchat"
        self.bot.join(self.dchatchannel)
        self._reset_gamedata()
        self.c9_setup = False
        self.anon_voting = False
        self.storedtopic = ""
        self.topicchanged = False
        self.bot.topic(self.channel, None)
        #self.start()

    def user_nickchange(self, old, new):
        for list_ in (self.live_players, self.dead_players, self.Mafia,
                self.citizens, self.originalMafia, self.VotingMafia):
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
        for var in ('game_starter', 'sheriff', 'sheriff_target', 'mafia_target', 'doctor', 'doctor_target', 'agent'):
            if getattr(self, var) == old:
                setattr(self, var, new)
        if old in self.sheriff_files:
            self.sheriff_files[new] = self.sheriff_files[old]
            del self.sheriff_files[old]
                
    def user_part(self, channel, username):
        #self._removeUser(username)
        pass

    def user_quit(self, username, reason=""):
        #self._removeUser(username)
        pass
        
    def user_join(self, channel, username):
        if channel == self.channel:
            if username in self.live_players:
                if self.gamestate == self.GAMESTATE_RUNNING:
                    self.fix_modes()
        if channel == self.dchatchannel:
            if username not in self.dead_players and username not in self.spectators:
                self.bot.kick(self.dchatchannel, username, "You aren't supposed to be here.")
        pass
        
    def user_kicked(self, channel, username, kicker, message=""):
        pass

    def notify_mafia(self, msg):
        for mafia in self.Mafia:
            self.bot.noteout(mafia, msg)
            
    def notify_votingmafia(self, msg):
        for mafia in self.VotingMafia:
            self.bot.noteout(mafia, msg)

    def _removeUser(self, nick):
        channel = self.channel

        if nick in self.live_players:
            self.bot.pubout(channel, "%s disappeared in some sort of strange wormhole." % nick)
            self.live_players.remove(nick)
            if self.gamestate == self.GAMESTATE_STARTING:
                # Check if game is empty
                if len(self.live_players) == 0:
                    self.bot.pubout(channel, "There are no more users in this game. Ending.")
                    self.end_game(self.game_starter)
                return
            self.dead_players.append(nick)
            if nick in self.Mafia:
                self.Mafia.remove(nick)
                self.bot.pubout(channel, "%s was in the Mafia. Apparently someone made them an offer they couldn't refuse." % nick)
            if nick in self.citizens:
                self.citizens.remove(nick)
                self.bot.pubout(channel, "%s had a boring position in the game, that of a citizen. Hopefully death will be more interesting." % nick)
            if nick == self.doctor:
                self.bot.pubout(channel, "%s was a doctor. The hospitals are baffled at this unexpected erasure from reality." % nick)
            if nick == self.doctor_target:
                if self.has_doctor:
                    self.bot.noteout(self.doctor, "Due to %s's unexpected erasure from reality, you may Save once again this night." % nick)
                    self.doctor_target = None
                    self.doctor_chosen = False
            if nick == self.detective:
                self.bot.pubout(channel, "%s was a detective. Interpol is investigating their mysterious disappearance with the assistance of Agents Mulder and Scully." % nick)
            if nick == self.sheriff:
                self.bot.pubout(channel, "%s was a sheriff. The police force is mad that all their sheriffs get destroyed by timespace anomalies." % nick)
            if nick == self.sheriff_target:
                if self.has_sheriff:
                    self.bot.noteout(self.sheriff, "Due to %s's unexpected erasure from reality, you may Check once again this night." % nick)
                    self.sheriff_target = None
                    self.sheriff_chosen = False
            if self.has_agent and self.agent_chosen and nick == self.agent_target:
                self.bot.noteout(self.agent, "Due to %s's unexpected erasure from reality, you may Alter once again this night." % nick)
                self.agent_chosen = False
            if nick == self.mafia_target:
                self.notify_mafia("Due to %s's unexpected erasure from reality, you can choose someone else to kill tonight." % nick)
                self.mafia_target = None
            for map_ in (self.mafia_votes, self.citizen_votes, self.tally):
                if map_.has_key(nick):
                    del map_[nick]
            for map_ in (self.mafia_votes, self.citizen_votes):
                for k, v in map_.items():
                    if v == nick:
                        del map_[k]
            if not self.check_game_over():
                if self.check_night_done():
                    self.day()

        if nick in self.spectators:
            self.spectators.remove(nick)
            self.reply(channel, nick, "You are no longer spectating.")
            self.bot.kick(self.dchatchannel, nick, "You are no longer spectating.")
        
        if nick == self.game_starter:
            self.game_starter = None
            self.bot.pubout(channel, "Game start is now open to anyone. Type !start to start the game.")

    def timer_tick(self):
        self.check_game_control()
        if self.time is None:
            pass
        elif self.time == "night":
            self.timer += 1
            if self.timer == (self.nighttimeout - 60):
                # One minute remaining before night times out.
                self.bot.pubout(self.channel, "There is one minute remaining before dawn.")
                if self.mafia_target == None:
                    self.notify_votingmafia("Please hurry, %s, you have less than one minute before the night ends! (If no choice is made, a random voted-for target (or if no votes, a random non-mafia target) will be selected.)" % ", ".join(self.Mafia))
                if self.has_doctor and self.doctor_target == None and self.doctor in self.live_players:
                    self.bot.noteout(self.doctor, "Please hurry, %s, you have less than one minute before the night ends! (If no choice is made, a random target will be selected.)" % self.doctor)
                if self.has_sheriff and self.sheriff_target == None and self.sheriff in self.live_players:
                    self.bot.noteout(self.sheriff, "Please hurry, %s, you have less than one minute before the night ends! (If no choice is made, a random target will be selected.)" % self.sheriff)
                if self.has_agent and self.agent_chosen == False and self.agent in self.live_players:
                    self.bot.noteout(self.agent, "Please hurry, %s, you have less than one minute before the night ends! (If no choice is made, a random target will be selected.)" % self.agent)
            if self.timer == self.nighttimeout:
                # Some power role is taking too long at night. Doctor and sheriff get random live non-self targets.
                # Mafia get a target randomly chosen from the votes list, or just random non-mafia if no votes list.
                if self.mafia_target == None:
                    if len(self.mafia_votes) > 0:
                        self.mafia_target = random.choice(self.mafia_votes.values())
                        self.notify_mafia("Because the Mafia took too long to decide, the player %s was randomly selected for killing this night." % self.mafia_target)
                    else:
                        while self.mafia_target == None or self.mafia_target in self.Mafia:
                            self.mafia_target = random.choice(self.live_players)
                            if self.mafia_target in self.Mafia:
                                self.mafia_target = None
                        self.notify_mafia("Because the Mafia took too long to decide, the player %s was randomly selected for killing this night." % self.mafia_target)
                if self.has_doctor and self.doctor in self.live_players:
                    if self.doctor_chosen == False:
                        while self.doctor_target == None or self.doctor_target == self.doctor:
                            self.doctor_target = random.choice(self.live_players)
                        self.doctor_chosen = True
                        self.bot.noteout(self.doctor, "Because the doctor took too long to decide, the player %s was randomly selected for saving this night." % self.doctor_target)
                if self.has_sheriff and self.sheriff in self.live_players:
                    if self.sheriff_chosen == False:
                        while self.sheriff_target == None or self.sheriff_target == self.sheriff:
                            self.sheriff_target = random.choice(self.live_players)
                        self.sheriff_chosen = True
                        self.bot.noteout(self.sheriff, "Because the sheriff took too long to decide, the player %s was randomly selected for checking this night." % self.sheriff_target)
                if self.has_agent and self.agent in self.live_players:
                    if not self.agent_chosen:
                        target = None
                        while target == None or target == self.agent:
                            target = random.choice(self.live_players)
                        self.sheriff_files[target] = not self.sheriff_files[target]
                        self.agent_chosen = True
                        self.bot.noteout(self.agent, "Because the agent took too long to decide, the player %s was randomly selected for file-altering this night." % target)
                if not self.check_game_over():
                    if self.check_night_done():
                        self.day()
            pass
        elif self.time == "day":
            if self.daytimeout != 0:
                self.timer += 1
                if self.timer == self.daytimeout * 60 - 60:
                    self.bot.pubout(self.channel, "There is only one minute remaining before nightfall.")
                if self.timer >= self.daytimeout * 60:
                    self.bot.pubout(self.channel, "The town was not able to decide who to lynch.")
                    self.night()


    GAME_STARTER_TIMEOUT_MINS = 5
    def check_game_control(self, nick=None):
        "Implement a timeout for game controller."
        if self.game_starter is None:
            return
        if self.game_starter == nick:
            self.game_starter_last_checkn = time.time()
        else:
            if self.game_starter_last_checkn < (
                    time.time() - self.GAME_STARTER_TIMEOUT_MINS * 60):
                if self.gamestate != self.GAMESTATE_RUNNING:
                    self.bot.pubout(self.channel, "Game starter '%s' has been silent for %d minutes. "
                            "Game control is now open to all." % (self.game_starter,
                                self.GAME_STARTER_TIMEOUT_MINS))
                self.game_starter = None

    def msg_private(self, user, message):
        self.check_game_control(user)
        self.do_command(user, user, message)

    def msg_channel(self, channel, user, message):
        self.check_game_control(user)
        a = string.split(message, ":", 1)
        if len(a) > 1 and a[0].lower() == self.bot.nickname.lower():
            self.do_command(channel, user, string.strip(a[1]))
        elif message[0]=='!' and (len(message) > 1) and message[1]!='!':
            self.do_command(channel, user, string.strip(message[1:]))
            
    def channel_topic(self, channel, user, topic):
        if channel == self.channel and user != self.bot.nickname:
            self.storedtopic = topic

    def _reset_gamedata(self):
        self.opmode = False
        self.gamestate = self.GAMESTATE_NONE
        self.time = None
        self.game_starter = None
        self.game_starter_last_checkn = 0
        self.live_players = []
        self.dead_players = []
        self.Mafia = []
        self.VotingMafia = []
        self.citizens = []
        self.police = []
        self.has_sheriff = False
        self.sheriff = None
        self.sheriff_files = {}
        self.has_doctor = False
        self.doctor = None
        self.has_detective = False
        self.detective = None
        self.has_agent = False
        self.agent = None
        self.originalMafia = []
        self.spectators = []
        # Night round variables
        self.sheriff_target = None
        self.sheriff_chosen = False
        self.doctor_target = None
        self.doctor_chosen = False
        self.agent_target = None
        self.agent_chosen = False
        self.mafia_target = None
        self.mafia_votes = {}
        self.nighttimeout = 120
        self.daytimeout = 0
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
            random.seed()
            self.gamestate = self.GAMESTATE_STARTING
            self.game_starter = game_starter
            self.game_starter_last_checkn = time.time()
            self.live_players.append(game_starter)
            self.bot.pubout(channel, "A new game has been started by %s; "
                    "say '%s: join' to join the game."
                    % (self.game_starter, self.bot.nickname))
            self.bot.pubout(channel, "%s: Say '%s: start' when everyone has joined."
                    % (self.game_starter, self.bot.nickname))
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
                                                "at least %d active players."%(minUsers))
                self.bot.pubout(channel, ("I count only %d active players right now: %s."
                    % (len(self.live_players), self.live_players)))
            else:
                # Store the topic and set a "GAME IN PROGRESS" message.
                self.bot.topic(channel, "~GAME IN PROGRESS~ | " + self.storedtopic)
                self.topicchanged = True
            
                # Randomly select Mafia and a sheriff and a doctor. Everyone else is a citizen.
                users = self.live_players[:]
                self.bot.pubout(channel, "A new game has begun! Please wait, assigning roles...")
                
                # Moderate the channel, if possible.
                self.gamestate = self.GAMESTATE_RUNNING
                self.fix_modes()
                
                self.Mafia.append(users.pop(random.randrange(len(users))))
                if len(self.live_players) >= 6:
                    self.Mafia.append(users.pop(random.randrange(len(users))))
                if len(self.live_players) >= 9:
                    self.Mafia.append(users.pop(random.randrange(len(users))))
                if len(self.live_players) >= 12:
                    self.Mafia.append(users.pop(random.randrange(len(users))))
                if len(self.live_players) >= 15:
                    self.Mafia.append(users.pop(random.randrange(len(users))))
                if len(self.live_players) >= 18:
                    self.Mafia.append(users.pop(random.randrange(len(users))))
                if len(self.live_players) >= 21:
                    self.Mafia.append(users.pop(random.randrange(len(users))))

                if len(self.Mafia) == 1:
                    self.bot.pubout(channel, "There is only one Mafia.")
                else:
                    self.bot.pubout(channel, "There are %d Mafia." % len(self.Mafia))
                    
                self.originalMafia = self.Mafia[:]
                
                # Pick a mafia to be agent, if more than 2
                if len(self.Mafia) >= 2:
                    self.agent = random.choice(self.Mafia)
                    self.has_agent = True
                
                # Add mafia to sheriff files and non-agent mafia to voting list
                for mafia in self.originalMafia:
                    self.sheriff_files[mafia] = True
                    if mafia != self.agent:
                        self.VotingMafia.append(mafia)
                
                #Breaking C9 for now. Oh. Well.
                #if self.c9_setup == False or (self.c9_setup == True and random.randint(0,1) == 1):
                #    self.has_sheriff = True
                #    self.sheriff = users.pop(random.randrange(len(users)))
                #if self.c9_setup == False or (self.c9_setup == True and random.randint(0,1) == 1):
                #    self.has_doctor = True
                #    self.doctor = users.pop(random.randrange(len(users)))
                
                if len(self.live_players) >= 4:
                    self.has_doctor = True
                    self.doctor = users.pop(random.randrange(len(users)))
                    self.sheriff_files[self.doctor] = False
                if len(self.live_players) >= 6:
                    self.has_detective = True
                    self.detective = users.pop(random.randrange(len(users)))
                    self.sheriff_files[self.detective] = False
                if len(self.live_players) >= 5:
                    self.has_sheriff = True
                    self.sheriff = users.pop(random.randrange(len(users)))
                    self.sheriff_files[self.sheriff] = False
        
                for user in users:
                    self.citizens.append(user)
                    self.sheriff_files[user] = False

                # Private message each user, tell them their role.
                if self.has_sheriff:
                    self.bot.noteout(self.sheriff, sheriff_intro_text)
                if self.has_doctor:
                    self.bot.noteout(self.doctor, doctor_intro_text)
                if self.has_detective:
                    self.bot.noteout(self.detective, detective_intro_text)
                if self.has_agent:
                    self.bot.noteout(self.agent, agent_intro_text)
#                for cops in self.police:
#                        self.bot.noteout(cops, "The police force is: %s. You can talk to them using pchat." % ", ".join(self.police))
                self.notify_votingmafia(mafia_intro_text)
                for citizen in self.citizens:
                    self.bot.noteout(citizen, citizen_intro_text)

                self.bot.pubout(channel, "Roles assigned. To learn how to play, say '%s: rules'." % self.bot.nickname)

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

            self.gamestate = self.GAMESTATE_NONE
            self.fix_modes()
            for players in self.dead_players + self.spectators:
                self.bot.kick(self.dchatchannel, players, "The game is now over.")
            if self.topicchanged:
                self.bot.topic(channel, self.storedtopic) # Reset the topic
                self.topicchanged = False
            self._reset_gamedata()


    def reveal_all_identities(self):
        "Print everyone's identities."

        channel = self.channel

        message = "*** The mafia were %s" % ", ".join(self.originalMafia)
        if self.has_agent:
            message += ", the agent was %s" % self.agent
        if self.has_sheriff:
            message += ", the sheriff was %s" % self.sheriff
        if self.has_detective:
            message += ", the detective was %s" % self.detective
        if self.has_doctor:
            message += ", the doctor was %s" % self.doctor
        message += ". Everyone else was a normal citizen"

        self.bot.pubout(channel, message)

    def check_game_over(self):
        """End the game if either citizens or Mafia have won.
        Return 1 if game is over, 0 otherwise."""

        channel = self.channel

        # If all Mafia are dead, the citizens win.
        if len(self.Mafia) == 0:
            self.bot.pubout(channel, "The Mafia are dead!    The \x034citizens\x0f have \x034won\x0f.")
            self.end_game(self.game_starter)
            return 1

        # If the number of non-Mafia is the same as the number of Mafia,
        # then the Mafia win.
        if (len(self.live_players) - len(self.Mafia)) == len(self.Mafia):
            self.bot.pubout(channel, \
                "There are now an equal number of citizens and Mafia.")
            msg = "The Mafia have no need to hide anymore; "
            msg = msg + "They attack the remaining citizens. "
            msg = msg + "The \x034Mafia\x0f have \x034won\x0f."
            self.bot.pubout(channel, msg)
            self.end_game(self.game_starter)
            return 1

        return 0


    def check_night_done(self):
        "Check if nighttime is over.    Return 1 if night is done, 0 otherwise."
        
        # Are there mafia alive to vote?
        if len(self.VotingMafia) < 1:
            self.mafia_target = self.NOKILL

        # Is the sheriff done checking?
        if self.has_sheriff == False or self.sheriff not in self.live_players:
            sheriff_done = 1
        else:
            if self.sheriff_chosen is False:
                sheriff_done = 0
            else:
                sheriff_done = 1
                
        # Is the doctor done checking?
        if self.has_doctor == False or self.doctor not in self.live_players:
            doctor_done = 1
        else:
            if self.doctor_chosen == False:
                doctor_done = 0
            else:
                doctor_done = 1
        
        # Is the agent done altering?
        if self.has_agent == False or self.agent not in self.live_players:
            agent_done = 1
        else:
            if self.agent_chosen == False:
                agent_done = 0
            else:
                agent_done = 1

        if (self.mafia_target is not None) and sheriff_done and doctor_done and agent_done:
            return 1
        else:
            return 0


    def night(self):
        "Declare a NIGHT episode of gameplay."

        #chname, chobj = self.channels.items()[0]
        channel = self.channel

        # Set night timer to two and a half minutes plus one minute for each Mafia.
        # This seems to be a fairly optimum time.
        self.nighttimeout = 150 + (20 * len(self.live_players))
 
        self.time = "night"
        
        #Reset timer.
        
        self.timer = 0

        self.fix_modes()

        # Clear any daytime variables
        self.citizen_votes = {}
        self.tally = {}

        # Declare nighttime.
        self.print_alive()
        for text in night_game_texts:
            self.bot.pubout(channel, text)

        nighttextrandomqueue = []

        # Give private instructions to Mafia and sheriff and doctor.
        if len(self.Mafia) >= 2:
            self.notify_mafia("The Mafia that can vote are %s. The Agent is %s. You can confer with them privately using the 'mchat' command." % (", ".join(self.VotingMafia), self.agent))
        if self.has_sheriff and self.sheriff in self.live_players:
            for text in night_sheriff_texts:
                #self.bot.noteout(self.sheriff, text)
                nighttextrandomqueue.append([self.sheriff, text])
        if self.has_doctor and self.doctor in self.live_players:
            for text in night_doctor_texts:
                #self.bot.noteout(self.doctor, text)
                nighttextrandomqueue.append([self.doctor, text])
        if self.has_agent and self.agent in self.live_players:
            for text in night_agent_texts:
                #self.bot.noteout(self.agent, text)
                nighttextrandomqueue.append([self.agent, text])
        for text in night_Mafia_texts:
            for mafia in self.VotingMafia:
                #self.bot.noteout(mafia, msg)
                nighttextrandomqueue.append([mafia, text])
        for player in self.live_players:
            if player != self.sheriff and player != self.doctor and player != self.agent and player not in self.Mafia:
                nighttextrandomqueue.append([player, "Because you are a role with no night actions, there is nothing you can do at this time. Sleep soundly..."])
                
        random.shuffle(nighttextrandomqueue)
        for messages in nighttextrandomqueue:
            self.reply(messages[0], messages[0], messages[1])
        
        # ... bot is now in 'night' mode;    goes back to doing nothing but
        # waiting for commands.


    def day(self):
        "Declare a DAY episode of gameplay."

        channel = self.channel

        self.time = "day"
        
        #Reset timer.
        
        self.timer = 0
            
        # Sheriff gets their report.
        if self.has_sheriff and self.sheriff in self.live_players:
            if self.sheriff != self.mafia_target or (self.sheriff == self.mafia_target and self.sheriff == self.doctor_target):
                if self.sheriff_target == self.agent:
                    self.bot.noteout(self.sheriff, "Your files say that %s is the Agent!" % self.sheriff_target)
                elif self.sheriff_files[self.sheriff_target]:
                    self.bot.noteout(self.sheriff, "Your files say that %s is a Mafia!" % self.sheriff_target)
                else:
                    self.bot.noteout(self.sheriff, "Your files say that %s is innocent." % self.sheriff_target)

        # Discover the dead mafia victim.
        message = "\x034Day\x0f Breaks!    Sunlight pierces the sky. "
        if self.doctor_target != self.mafia_target and self.mafia_target != self.NOKILL:
            message += "The city awakes in horror... to find the mutilated body of \x034%s\x0f!!"\
                                         % self.mafia_target
        else:
            message += "No one was killed."

        self.bot.pubout(channel, message)

        if not self.kill_player(self.mafia_target):
            # Clear all the nighttime voting variables:
            self.sheriff_target = None
            self.sheriff_chosen = False
            self.doctor_target = None
            self.doctor_chosen = False
            self.mafia_target = None
            self.mafia_votes = {}
            self.agent_chosen = False
            self.agent_target = None

            # Give daytime instructions.
            self.print_alive()
            for text in day_game_texts:
                self.bot.pubout(channel, text)

            # ... bot is now in 'day' mode;    goes back to doing nothing but
            # waiting for commands.



    def check(self, channel, user, who):
        "Allow a sheriff to 'check' somebody."

        if self.time != "night":
            self.reply(channel, user, "Are you a sheriff? In any case, it's not nighttime.")
        else:
            if self.has_sheriff == False or user != self.sheriff:
                self.reply(channel, user, "Huh?")
            else:
                if who not in self.live_players:
                    self.reply(channel, user, "That player either doesn't exist, or is dead.")
                else:
                    self.sheriff_target = who
                    self.reply(channel, user, "You will check %s tonight, and see your results in the morning." % who)
                    self.sheriff_chosen = True
                    if self.check_night_done():
                        self.day()
                            
    def save(self, channel, user, who):
        "Allow a doctor to 'save' somebody."

        if self.time != "night":
            self.reply(channel, user, "Are you a doctor? In any case, it's not nighttime.")
        else:
            if self.has_doctor == False or user != self.doctor:
                self.reply(channel, user, "Huh?")
            else:
                if who not in self.live_players:
                    self.reply(channel, user, "That player either doesn't exist, or is dead.")
                else:
                    if who == user:
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
            if self.has_doctor == False or user != self.doctor:
                self.reply(channel, user, "Huh?")
            else:
                self.doctor_target = None
                self.doctor_chosen = True
                self.reply(channel, user, "Tonight, no one will be saved.")
                if self.check_night_done():
                    self.day()
                    
    def alter(self, channel, user, who):
        "Allow an agent to alter files."
        if self.time != "night":
            self.reply(channel, user, "Are you an agent?    In any case, it's not nighttime.")
        else:
            if self.has_agent == False or user != self.agent:
                self.reply(channel, user, "Huh?")
            else:
                if who not in self.live_players:
                    self.reply(channel, user, "That player either doesn't exist, or is dead.")
                else:
                    if self.agent_chosen is not False:
                        self.reply(channel, user, "You've already chosen a file to alter tonight.")
                    elif who == user:
                        self.reply(channel, user, "You can't alter your own file!")
                    else:
                        self.sheriff_files[who] = not self.sheriff_files[who]
                        self.agent_chosen = True
                        self.agent_target = who
                        self.reply(channel, user, "You have altered the file on %s." % who)
                        if self.check_night_done():
                            self.day()
                            
    def noalter(self, channel, user):
        "The agent decides not to alter any files."
        
        if self.time != "night":
            self.reply(channel, user, "Are you an agent?    In any case, it's not nighttime.")
        else:
            if self.has_agent == False or user != self.agent:
                self.reply(channel, user, "Huh?")
            else:
                if self.agent_chosen is not False:
                    self.reply(channel, user, "You've already chosen a file to alter tonight.")
                else:
                    self.agent_chosen = True
                    self.reply(channel, user, "Tonight, no files will be altered.")
                if self.check_night_done():
                    self.day()

    def kill(self, channel, user, who):
        "Allow a Mafia to express intent to 'kill' somebody."
        if self.time != "night":
            self.reply(channel, user, "Are you a Mafia?    In any case, it's not nighttime.")
            return
        if user not in self.VotingMafia:
            self.reply(channel, user, "Huh?")
            return
        if who not in self.live_players and who != self.NOKILL:
            self.reply(channel, user, "That player either doesn't exist, or is dead.")
            return
        if len(self.Mafia) > 1:
            # Multiple Mafia are alive:
            self.mafia_votes[user] = who
            if who != self.NOKILL:
                self.notify_mafia("%s has voted to kill %s." % (user, who))
            else:
                self.notify_mafia("%s has voted not to kill tonight." % user)

            # If all Mafia have voted, look for agreement:
            if len(self.mafia_votes) == len(self.VotingMafia):
                for killee in self.mafia_votes.values():
                    if who != killee:
                        break
                else:
                    self.mafia_target = who
                    self.notify_mafia("It is done. The Mafia agree.")
                    if self.check_night_done():
                        self.day()
                    return
                self.notify_mafia("Hm, I sense disagreement or ambivalence. You Mafia should decide on one target.")
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
            self.bot.noteout(player, "You were saved by the doctor!")
            self.fix_modes()
            return 0
        elif player == self.NOKILL:
            self.fix_modes()
            return 0
        else:
            self.live_players.remove(player)
            self.dead_players.append(player)
            self.fix_modes()

            if player in self.Mafia:
                id = "a \x034mafia\x0f!"
            elif player == self.sheriff:
                id = "the \x034sheriff\x0f!"
            elif player == self.doctor:
                id = "the \x034doctor\x0f!"
            else:
                id = "a normal citizen."

            examine_msg = "*** Examining the body, you notice that this player was %s" % id

            if self.has_detective and self.detective in self.live_players:
                self.bot.noteout(self.detective, examine_msg)
            elif not self.has_detective:
                self.bot.pubout(self.channel, examine_msg)
            
            if player in self.Mafia:
                self.Mafia.remove(player)
                
            if player in self.VotingMafia:
                self.VotingMafia.remove(player)
                
            if self.check_game_over():
                return 1
            else:
                self.bot.pubout(channel, ("(%s is now dead, and should stay quiet.)") % player)
                self.bot.noteout(player, "You are now \x034dead\x0f. You may observe the game, but please stay quiet until the game is over. However, you may converse with other dead players in the %s channel." % self.dchatchannel)
                self.bot.invite(player, self.dchatchannel)
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
            lynchee_name = "No Lynch" if lynchee == self.NOLYNCH else lynchee
            if self.tally[lynchee] > 1:
                msg = msg + ("(%s : %d votes) " % (lynchee_name, self.tally[lynchee]))
            else:
                msg = msg + ("(%s : 1 vote) " % lynchee_name)
        self.bot.pubout(channel, msg)


    def print_alive(self):
        "Declare who's still alive."
        channel = self.channel
        msg = "The following players are still alive: %s"%', '.join(self.live_players)
        self.bot.pubout(channel, msg)
        if self.dead_players:
            msg = "The following players are dead : %s"%', '.join(self.dead_players)
            self.bot.pubout(channel, msg)

    def fix_modes(self):
        if self.modeplugin != None:
            if self.gamestate == self.GAMESTATE_RUNNING:
                self.modeplugin.moderate(self.channel)
                self.modeplugin.protect_nickchange(self.channel)

                if self.time == "night":
                    self.modeplugin.devoice(self.channel, self.live_players)
                    self.modeplugin.devoice(self.channel, self.dead_players)
                elif self.time == "day":
                    self.modeplugin.voice(self.channel, self.live_players)
                    self.modeplugin.devoice(self.channel, self.dead_players)
            else:
                self.modeplugin.unmoderate(self.channel)
                self.modeplugin.unprotect_nickchange(self.channel)
                self.modeplugin.devoice(self.channel, self.live_players)
                self.modeplugin.devoice(self.channel, self.dead_players)

    def match_name(self, nick):
        """Match NICK to a username in users(), insensitively.    Return
        matching nick, or None if no match."""

        nick_lower = nick.lower()

        for name in self.live_players:
            if nick_lower == name.lower():
                return name

        return None

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
        elif lynchee not in self.live_players and lynchee != self.NOLYNCH:
            self.reply(channel, user, "Um, only living players can be lynched.")
        elif lynchee == lyncher:
            self.reply(channel, user, "Um, you can't lynch yourself.")

        else:
            self.citizen_votes[lyncher] = lynchee
            if self.anon_voting == False:
                if lynchee != 0:
                    self.bot.pubout(self.channel, "%s has voted to lynch %s!" % (lyncher, lynchee))
                else:
                    self.bot.pubout(self.channel, "%s has voted not to lynch." % lyncher)
            self.tally_votes()
            victim = self.check_for_majority()
            if victim is None:
                self.print_tally()
            elif victim == self.NOLYNCH:
                self.bot.pubout(self.channel, "The majority has voted not to lynch. No one will be lynched today.")
                self.night()
            else:
                self.bot.pubout(self.channel, ("The majority has voted to lynch %s!! "
                    "Mob violence ensues.    This player is now \x034dead\x0f." % victim))
                if not self.kill_player(victim):
                    # Day is done;    flip bot back into night-mode.
                    self.timer = 0
                    self.night()

    def lynch_unvote(self, channel, user):
        # sanity checks
        if self.time != "day":
            self.reply(channel, user, "Sorry, lynching only happens during the day.")
        elif user not in self.live_players:
            self.reply(channel, user, "Um, only living players can vote on lynchings.")

        else:
            if user in self.citizen_votes:
                oldlynchee = self.citizen_votes[user]
                del self.citizen_votes[user]
                if self.anon_voting == False:
                    self.bot.pubout(self.channel, "%s has retracted a lynch vote for %s!" % (user, oldlynchee))
                self.tally_votes()
                self.print_tally()
            else:
                self.reply(channel, user, "You don't have a lynch vote registered.")

#Broken anyway.
#    def cmd_setup(self, args, channel, user):
#        if len(args) > 0:
#            if args[0].lower() == 'c9':
#                self.c9_setup = True
#            else:
#                self.c9_setup = False
#        self.bot.pubout(self.channel, "Current setup: %s" % ("c9" if self.c9_setup else "original"))

    def cmd_anon(self, args, channel, user):
        if len(args) > 0:
            if self.gamestate == self.GAMESTATE_RUNNING:
                self.bot.pubout(self.channel, "You cannot change anonymous voting while a game is in progress.")
            elif self.gamestate == self.GAMESTATE_STARTING and self.game_starter != None and user != self.game_starter:
                self.bot.pubout(self.channel, "A game is starting. Only game starter %s can change anonymous voting." % self.game_starter)
            else:
                if args[0].lower() == 'on':
                    self.anon_voting = True
                elif args[0].lower() == 'off':
                    self.anon_voting = False
        self.bot.pubout(self.channel, "Anonymous voting is %s" % ("on" if self.anon_voting else "off"))
        
    def cmd_timer(self, args, channel, user):
        if len(args) > 0:
            if self.gamestate == self.GAMESTATE_RUNNING:
                self.bot.pubout(self.channel, "You cannot change the day timer while a game is in progress.")
            elif self.gamestate == self.GAMESTATE_STARTING and self.game_starter != None and user != self.game_starter:
                self.bot.pubout(self.channel, "A game is starting. Only game starter %s can change day timer." % self.game_starter)
            else:
                try: 
                    newtimeout = int(args[0])
                    if newtimeout >= 0 and newtimeout <= 120:
                        if newtimeout != 0:
                            self.bot.pubout(self.channel, "Day timer is now set to %i minutes." % newtimeout)
                            self.daytimeout = newtimeout
                        else:
                            self.bot.pubout(self.channel, "Day timer is now off.")
                            self.daytimeout = 0
                    else:
                        self.bot.pubout(self.channel, "%s: Please enter a value between 0 and 120 minutes." % user)
                except ValueError:
                    self.bot.pubout(self.channel, "%s: Invalid day timer value. Please enter an integer for day timer in minutes." % user)
        else:
            self.bot.pubout(self.channel, "Day timer is %s" % ("%i minutes." % self.daytimeout if self.daytimeout else "off."))

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
            if self.time == "night":
                self.bot.pubout(self.channel, "There are about %d seconds left before dawn." % int(round(self.nighttimeout - self.timer, -1)))
            if self.time == "day":
                if self.daytimeout != 0:
                    self.bot.pubout(self.channel, "There are about %d seconds left before nightfall." % int(round(self.daytimeout * 60 - self.timer, -1)))
        elif self.gamestate == self.GAMESTATE_STARTING:
            self.reply(channel, user, "A new game is starting. Currently %d players: %s"
                    % (len(self.live_players),self.live_players,))
        else:
            self.reply(channel, user, "No game is in progress.")

    def cmd_status(self, args, channel, user):
        self.cmd_stats(args, channel, user)

    def cmd_start(self, args, channel, user):
        self.start_game(user)

    def cmd_end(self, args, channel, user):
        self.end_game(user)

    def cmd_votes(self, args, channel, user):
        if self.anon_voting:
            self.bot.pubout(channel, "Anonymous voting is on. Not showing registered votes.")
            return

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
            else:
                self.bot.pubout(channel, "Everyone has voted.")
        else:
            self.bot.pubout(channel, "Nobody has voted yet.")
            if self.time == "day":
                self.tally_votes()
                self.print_tally()

    def cmd_del(self, args, channel, user):
        if len(args) >= 1:
            nick = self.match_name(args[0].strip())
            if nick:
                self._removeUser(nick)
            else:
                self.reply(channel, user, "There's nobody playing by the name %s" % args[0])
            
    def cmd_quit(self, args, channel, user):
        if user not in self.live_players + self.dead_players + self.spectators:
                self.reply(channel, user, "You aren't currently playing.")
        else:
            self._removeUser(user)
            

    def cmd_check(self, args, channel, user):
        if len(args) == 1:
            checkee = self.match_name(args[0].strip())
            if checkee is not None:
                self.check(channel, user, checkee.strip())
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
        
    def cmd_alter(self, args, channel, user):
        if len(args) == 1:
            alteree = self.match_name(args[0].strip())
            if alteree is not None:
                self.alter(channel, user, alteree.strip())
                return
        self.reply(channel, user, "Alter what?")
        
    def cmd_noalter(self, args, channel, user):
        self.noalter(channel, user)
        return
        
    def cmd_kill(self, args, channel, user):
        if len(args) == 1:
            killee = self.match_name(args[0].strip())
            if killee is not None:
                self.kill(channel, user, killee)
                return
        self.reply(channel, user, "Kill whom?")

    def cmd_nokill(self, args, channel, user):
        self.kill(channel, user, self.NOKILL)

    def cmd_lynch(self, args, channel, user):
        if len(args) == 1:
            lynchee = self.match_name(args[0])
            if lynchee is not None:
                self.lynch_vote(channel, user, lynchee.strip())
                return
        self.reply(channel, user, "Lynch whom?")

    def cmd_unlynch(self, args, channel, user):
        self.lynch_unvote(channel, user)

    def cmd_nolynch(self, args, channel, user):
        self.lynch_vote(channel, user, self.NOLYNCH)

    def cmd_join(self, args, channel, user):
        if self.gamestate == self.GAMESTATE_NONE:
            self.reply(channel, user, 'No game is running, perhaps you would like to start one?')
        elif self.gamestate == self.GAMESTATE_RUNNING:
            self.reply(channel, user, 'Game is in progress; please wait for the next game.')
        elif channel == user:
            self.reply(channel, user, 'Please type !join in the public channel to join the game.')
        elif user in self.live_players:
            self.reply(channel, user, 'You were already in the game!')
        elif user in self.spectators:
            self.reply(channel, user, 'You are currently spectating! Please quit first.')
        else:
            self.live_players.append(user)
            self.reply(channel, user, 'You are now in the game.')

    def cmd_mchat(self, args, channel, user):
        if user in self.Mafia:
            if self.time == "night":
                for mafioso in self.Mafia:
                    if user != mafioso:
                        self.bot.noteout(mafioso, "Mafia - <%s> %s" % (user, " ".join(args)))
                    else:
                        self.bot.noteout(mafioso, "Mafia - You: %s" % (" ".join (args)))
            else:
                self.bot.noteout(user, "You can't use mchat during the day.")
        else:
            self.bot.noteout(user, "You are not a Mafia!")
                
    """def cmd_dchat(self, args, channel, user):
        if user in (self.dead_players + self.spectators):
            for ghosts in (self.dead_players + self.spectators):
                if user != ghosts:
                    self.bot.noteout(ghosts, "Graveyard - <%s> %s" % (user, " ".join(args)))
                else:
                    self.bot.noteout(ghosts, "Graveyard - You: %s" % (" ".join(args)))"""
                    
    def cmd_dchat(self, args, channel, user):
        if user in self.dead_players or user in self.spectators:
            self.bot.invite(user, self.dchatchannel)
            self.reply(channel, user, "You have been invited to %s." % self.dchatchannel)
        else:
            self.reply(channel, user, "You are not dead or spectating!")
                    
#    def cmd_pchat(self, args, channel, user):
#        if user in self.police:
#            for cops in self.police:
#                if user != cops:
#                    self.bot.noteout(cops, "Police - <%s> %s" % (user, " ".join(args)))
#                else:
#                    self.bot.noteout(cops, "Police - You: %s" % (" ".join(args)))
#        else:
#            self.bot.noteout(user, "You are not a police officer!")

    def cmd_aboutbot(self, args, channel, user):
        self.reply(channel, user, "This module is heavily modified from a bot written in Python "
                "using the python-irclib library")
        self.reply(channel, user, "The original source code is available at %s" % svn_url)
       
    def cmd_rules(self, args, channel, user):
        for text in new_game_texts:
            self.reply(channel, user, text)
            
    def cmd_resetstarter(self, args, channel, user):
        if user == self.game_starter:
            self.game_starter = None
            self.bot.pubout(channel, "Game control is now open to all.")
        else:
            self.reply(channel, user, "You are not the game starter.")

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
        self.fix_modes()
        
    def cmd_spectate(self, args, channel, user):
        if self.gamestate == self.GAMESTATE_RUNNING or self.gamestate == self.GAMESTATE_STARTING:
            if user not in self.live_players and user not in self.dead_players:
                if user not in self.spectators:
                    self.spectators.append(user)
                    self.reply(channel, user, "You are now spectating the game. Feel free to join %s." % self.dchatchannel)
                    self.bot.invite(user, self.dchatchannel)
                else:
                    self.reply(channel, user, "You were already spectating!")
            else:
                self.reply(channel, user, "You are in the game, you can't spectate!")
        else:
            self.reply(channel, user, "There is no game in progress.")
            
    def cmd_role(self, args, channel, user):
        if self.gamestate == self.GAMESTATE_RUNNING:
            if user in self.live_players:
                if user == self.agent:
                    id = "a \x034mafia\x0f, but also the \x034agent\x0f."
                elif user in self.Mafia:
                    id = "a \x034mafia\x0f."
                elif user == self.sheriff:
                    id = "the \x034sheriff\x0f."
                elif user == self.doctor:
                    id = "the \x034doctor\x0f."
                elif user == self.detective:
                    id = "the \x034detective\x0f."
                else:
                    id = "a normal citizen."
                self.bot.noteout(user,"You are %s" % id)
            else:
                self.reply(channel, user, "You are not playing.")
        else:
            self.reply(channel, user, "There is no game in progress.")
            
    def cmd_whisper(self, args, channel, user):
        if self.gamestate == self.GAMESTATE_RUNNING:
            if self.time == "day":
                args[0] = self.match_name(args[0])
                if args[0] in self.live_players and user in self.live_players:
                    if args[0] != user:
                        caps = re.compile("[A-Z]")
                        message = " ".join(args[1:])
                        whisperchance = 5
                        if message.find("!") != -1:
                            whisperchance = whisperchance * 2
                        whisperchance += len(caps.findall(message))
                        self.reply(args[0], args[0], "<%s> %s" % (user, message))
                        self.reply(user, user, "You whisper to %s: %s" % (args[0], message))
                        chance = random.randint(1, 100)
                        if chance < whisperchance:
                            chance2 = random.randint(1, 100)
                            if chance2 < 50:
                                self.bot.pubout(self.channel, "<%s> whispers: %s" % (user, message))
                            else:
                                self.bot.pubout(self.channel, "<%s> whispers to <%s>: %s" % (user, args[0], message))
                        elif chance < whisperchance * 3:
                            message = args[1:]
                            for words in range(len(message)):
                                blankchance = random.randint(1, 100)
                                if blankchance > 50:
                                    message[words] = "..."
                            message = " ".join(x for x, group in itertools.groupby(message))
                            chance2 = random.randint(1, 100)
                            if chance2 < 50:
                                self.bot.pubout(self.channel, "<%s> whispers: %s" % (user, message))
                            else:
                                self.bot.pubout(self.channel, "<%s> whispers to <%s>: %s" % (user, args[0], message))
                    else:
                        self.reply(channel, user, "You can't whisper to yourself!")
                else:
                    self.reply(channel, user, "That player does not exist, or you are not in the game.")
            else:
                self.reply(channel, user, "You can only whisper during the day.")
        else:
            self.reply(channel, user, "There is no game in progress.")

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
             if cmds[0] not in ("stats", "status", "help", "dchat", "end", "del"):
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
