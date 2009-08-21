#!/usr/bin/env python
##
##    Werewolf - a plugin for pyGBot
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
# IRC Bot to moderate a game of "Werewolf".
#
# Werewolf is a traditional party game, sometimes known as 'Mafia',
# with dozens of variants.  This bot is following Andrew Plotkin's rules:
# http://www.eblong.com/zarf/werewolf.html
#
# Code originally based on example bot and irc-bot class from
# Joel Rosdahl <joel@rosdahl.net>, author of python-irclib.
#

"""A PyGBot plugin to for a game of "Werewolf".

The main commands are:

    start game -- start a new werewolf game.

    end game -- quit the current werewolf game (you must have started it)

    stats -- print information about state of game-in-progress.

"""

import sys, string, random, time

from pyGBot import log
from pyGBot.BasePlugin import BasePlugin

#---------------------------------------------------------------------
# General texts for narrating the game.  Change these global strings
# however you wish, without having to muck with the core logic!

minUsers=4

svn_url = \
"$URL: http://ircbot-collection.googlecode.com/svn/trunk/wolfbot.py $"
svn_url = svn_url[svn_url.find(' ')+1:svn_url.rfind('/')+1]

# Printed when a game first starts:

new_game_texts = \
["This is a game of paranoia and psychological intrigue.  Everyone\
 in this group appears to be a common villager, but several of\
 you are 'special'.  One or two of you are actually evil werewolves, seeking\
 to kill everyone while concealing their identity.",

 "And one of you is also a 'seer'; you have the ability to learn\
 whether a specific person is or is not a werewolf.",

 "As a community, your group objective is to weed out the werewolves\
 and lynch them before you're all killed in your sleep."]

# Printed when informing players of their initial roles:

wolf_intro_text = \
"You are a \x034werewolf\x0f\x02.  You want to kill everyone while they sleep. \
Whatever happens, keep your identity secret.  Act natural!"

seer_intro_text = \
"You're a villager, but also a \x034seer\x0f\x02.  Later on, you'll get chances to \
learn whether someone is or isn't a werewolf.  Keep your identity \
secret, or the werewolves may kill you!"

villager_intro_text = \
"You're an ordinary villager."


# Printed when night begins:

night_game_texts = \
["Darkness falls:  it is \x034night\x0f\x02.",
 "The whole village sleeps peacefully...",
 "Everyone relax and wait for morning... I'll tell you when night is over."]

# Printed when wolves and villager get nighttime instructions:

night_seer_texts = \
["In your dreams, you have the ability to see whether a certain person\
  is or is not a werewolf.",

 "You must use this power now: please type 'see <nickname>' (as a\
 private message to me) to learn about one living player's true\
 identity."]

night_werewolf_texts = \
["As the villagers sleep, you must now decide whom you want to kill.",
 "You and the other werewolf (if he is exists and is alive) should discuss (privately) and choose a victim.",
 "Please type 'kill <nickname>' (as a private message to me)."]


# Printed when day begins.

day_game_texts = \
["Paranoia runs through the village!  Who is a werewolf in disguise?",
 "The villagers *must* decide to lynch one player.",
 "When each player is ready, send me the command:  'lynch <nickname>',",
 "and I will keep track of votes, until the majority agrees."]




#---------------------------------------------------------------------
# Actual code.
#
# Modified from using the bot class to being a pyGBot plugin

IRC_BOLD = "\x02"

class Werewolf(BasePlugin):
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

    def user_nickchange(self, old, new):
        for list_ in (self.live_players, self.dead_players, self.wolves,
                self.villagers, self.originalwolves):
            if old in list_:
                list_.append(new)
                list_.remove(old)
        for map_ in (self.wolf_votes, self.villager_votes, self.tally):
            if map_.has_key(new):
                map_[new] = map_[old]
                del map_[old]
        for map_ in (self.wolf_votes, self.villager_votes):
            for k, v in map_.items():
                if v == old:
                    map_[k] = new
        for var in ('game_starter', 'seer', 'seer_target', 'wolf_target'):
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
            if nick in self.wolves:
                self.wolves.remove(nick)
                self.bot.pubout(channel, "The only relic left by %s was a copious amount of lupine fur.    "
	        "Now we know why %s always growled whenever a cat was nearby." % (nick,nick))
            if nick in self.villagers:
                self.villagers.remove(nick)
                self.bot.pubout(channel, "%s had a boring position in the game, that of a villager.    "
                        "Hopefully death will be more interesting." % nick)
            if nick == self.seer:
                self.bot.pubout(channel, "%s was a seer.    Apollo is mad that all his seers "
                        "get destroyed by timespace anomalies." % nick)
            if nick == self.seer_target:
                self.bot.noteout(self.seer, "Due to %s's unexpected erasure from reality, "
                        "you may See once again this night." % nick)
                self.seer_target = None
            if nick == self.wolf_target:
                for wolf in self.wolves:
                    self.bot.noteout(wolf, "Due to %s's unexpected erasure from reality, "
                            "you can choose someone else to kill tonight." % nick)
                self.wolf_target = None
            for map_ in (self.wolf_votes, self.villager_votes, self.tally):
                if map_.has_key(nick):
                    del map_[nick]
            for map_ in (self.wolf_votes, self.villager_votes):
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
            self.game_starter_last_seen = time.time()
        else:
            if self.game_starter_last_seen < (
                    time.time() - self.GAME_STARTER_TIMEOUT_MINS * 60):
                self.bot.pubout(channel, "Game starter '%s' has been silent for %d minutes. "
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
        self.gamestate = self.GAMESTATE_NONE
        self.time = None
        self.game_starter = None
        self.game_starter_last_seen = 0
        self.live_players = []
        self.dead_players = []
        self.wolves = []
        self.villagers = []
        self.seer = None
        self.originalwolves = []
        # Night round variables
        self.seer_target = None
        self.wolf_target = None
        self.wolf_votes = {}
        # Day round variables
        self.villager_votes = {}
        self.tally = {}


    def reply(self, channel, user, text):
        "Send TEXT to public channel or as private msg, in reply to event E."
        if channel != user:
            self.bot.pubout(channel, "%s: %s" % (user, text))
        else:
            self.bot.noteout(user, text)


    def start_game(self, game_starter):
        "Initialize a werewolf game -- assign roles and notify all players."
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
            self.game_starter_last_seen = time.time()
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
            self.game_starter_last_seen = time.time()

            if len(self.live_players) < minUsers:
                self.bot.pubout(channel, "Sorry, to start a game, there must be " + \
                                                "at least active %d players."%(minUsers))
                self.bot.pubout(channel, ("I count only %d active players right now: %s."
                    % (len(self.live_players), self.live_players)))

            else:
                # Randomly select two wolves and a seer.    Everyone else is a villager.
                users = self.live_players[:]
                self.bot.pubout(channel, "A new game has begun! Please wait, assigning roles...")
                self.wolves.append(users.pop(random.randrange(len(users))))
	if len(self.live_players) > 7:
	    self.wolves.append(users.pop(random.randrange(len(users))))
	    self.bot.pubout(channel, "There are 8 or more players so there are two werewolves.")
	else:
	    self.bot.pubout(channel, "There are not enough players for two werewolves so there is only one werewolf.")
            self.originalwolves = self.wolves[:]
            self.seer = users.pop(random.randrange(len(users)))
            for user in users:
                self.villagers.append(user)

            # Private message each user, tell them their role.
            self.bot.noteout(self.seer, seer_intro_text)
            for wolf in self.wolves:
                self.bot.noteout(wolf, wolf_intro_text)
            for villager in self.villagers:
                self.bot.noteout(villager, villager_intro_text)

            #if self.debug:
            #    print "SEER: %s, WOLVES: %s" % (self.seer, self.wolves)

            for text in new_game_texts:
                self.bot.pubout(channel, text)
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

        if len(self.originalwolves)==2:
            self.bot.pubout(channel, ("*** The two wolves were %s and %s, the seer was %s. "
                "Everyone else was a normal villager"
                % (self.originalwolves[0], self.originalwolves[1], self.seer)))
        else:
            self.bot.pubout(channel, ("*** The wolf was %s, the seer was %s. "
                "Everyone else was a normal villager"
	% (self.originalwolves[0], self.seer)))

    def check_game_over(self):
        """End the game if either villagers or werewolves have won.
        Return 1 if game is over, 0 otherwise."""

        channel = self.channel

        # If all wolves are dead, the villagers win.
        if len(self.wolves) == 0:
            self.bot.pubout(channel, "The wolves are dead!    The \x034villagers\x0f\x02 have \x034won\x0f.")
            self.end_game(self.game_starter)
            return 1

        # If the number of non-wolves is the same as the number of wolves,
        # then the wolves win.
        if (len(self.live_players) - len(self.wolves)) == len(self.wolves):
            self.bot.pubout(channel, \
                "There are now an equal number of villagers and werewolves.")
            msg = "The werewolves have no need to hide anymore; "
            msg = msg + "They attack the remaining villagers. "
            msg = msg + "The \x034werewolves\x0f\x02 have \x034won\x0f."
            self.bot.pubout(channel, msg)
            self.end_game(self.game_starter)
            return 1

        return 0


    def check_night_done(self):
        "Check if nighttime is over.    Return 1 if night is done, 0 otherwise."

        # Is the seer done seeing?
        if self.seer not in self.live_players:
            seer_done = 1
        else:
            if self.seer_target is None:
                seer_done = 0
            else:
                seer_done = 1

        if (self.wolf_target is not None) and seer_done:
            return 1
        else:
            return 0


    def night(self):
        "Declare a NIGHT episode of gameplay."

        #chname, chobj = self.channels.items()[0]
        channel = self.channel
        
        self.time = "night"

        # Clear any daytime variables
        self.villager_votes = {}
        self.tally = {}

        # Declare nighttime.
        self.print_alive()
        for text in night_game_texts:
            self.bot.pubout(channel, text)

        # Give private instructions to wolves and seer.
        if self.seer in self.live_players:
            for text in night_seer_texts:
                self.bot.noteout(self.seer, text)
        for text in night_werewolf_texts:
            for wolf in self.wolves:
                self.bot.noteout(wolf, text)
        if len(self.wolves) >= 2:
            self.bot.noteout(self.wolves[0],\
                                             ("The other werewolf is %s.    Confer privately."\
                                                % self.wolves[1]))
            self.bot.noteout(self.wolves[1],\
                                             ("The other werewolf is %s.    Confer privately."\
                                                % self.wolves[0]))

        # ... bot is now in 'night' mode;    goes back to doing nothing but
        # waiting for commands.


    def day(self):
        "Declare a DAY episode of gameplay."

        channel = self.channel

        self.time = "day"

        # Discover the dead wolf victim.
        self.bot.pubout(channel, "\x034Day\x0f\x02 Breaks!    Sunlight pierces the sky.")
        self.bot.pubout(channel, ("The village awakes in horror..." + \
                                         "to find the mutilated body of \x034%s\x0f\x02!!"\
                                         % self.wolf_target))

        if not self.kill_player(self.wolf_target):
            # Clear all the nighttime voting variables:
            self.seer_target = None
            self.wolf_target = None
            self.wolf_votes = {}

            # Give daytime instructions.
            self.print_alive()
            for text in day_game_texts:
                self.bot.pubout(channel, text)
            self.bot.pubout(channel, "Remember:    votes can be changed at any time.")

            # ... bot is now in 'day' mode;    goes back to doing nothing but
            # waiting for commands.



    def see(self, channel, user, who):
        "Allow a seer to 'see' somebody."

        if self.time != "night":
            self.reply(channel, user, "Are you a seer?    In any case, it's not nighttime.")
        else:
            if user  != self.seer:
                self.reply(channel, user, "Huh?")
            else:
                if who not in self.live_players:
                    self.reply(channel, user, "That player either doesn't exist, or is dead.")
                else:
                    if self.seer_target is not None:
                        self.reply(channel, user, "You've already had your vision for tonight.")
                    else:
                        self.seer_target = who
                        if who in self.wolves:
                            self.reply(channel, user, "You're sure that player is a werewolf!")
                        else:
                            self.reply(channel, user, "You're sure that player is a normal villager.")
                        if self.check_night_done():
                            self.day()


    def kill(self, channel, user, who):
        "Allow a werewolf to express intent to 'kill' somebody."
        if self.time != "night":
            self.reply(channel, user, "Are you a werewolf?    In any case, it's not nighttime.")
            return
        if user not in self.wolves:
            self.reply(channel, user, "Huh?")
            return
        if who not in self.live_players:
            self.reply(channel, user, "That player either doesn't exist, or is dead.")
            return
        if len(self.wolves) > 1:
            # Multiple wolves are alive:
            self.wolf_votes[u ] = who
            self.reply(channel, user, "Your vote is acknowledged.")

            # If all wolves have voted, look for agreement:
            if len(self.wolf_votes) == len(self.wolves):
                for killee in self.wolf_votes.values():
                    if who != killee:
                        break
                else:
                    self.wolf_target = who
                    self.reply(channel, user, "It is done. The werewolves agree.")
                    if self.check_night_done():
                        self.day()
                    return
                self.reply(channel, user, "Hm, I sense disagreement or ambivalence.")
                self.reply(channel, user, "You wolves should decide on one target.")
        else:
            # only one wolf alive, no need to agree with anyone.
            self.wolf_target = who
            self.reply(channel, user, "Your decision is acknowledged.")
            if self.check_night_done():
                self.day()


    def kill_player(self, player):
        "Make a player dead.    Return 1 if game is over, 0 otherwise."

        channel = self.channel

        self.live_players.remove(player)
        self.dead_players.append(player)
        #self.fix_modes()

        if player in self.wolves:
            id = "a \x034wolf\x0f\x02!"
            self.wolves.remove(player)
        elif player == self.seer:
            id = "the \x034seer\x0f\x02!"
        else:
            id = "a normal villager."

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
        "Count votes in villager_votes{}, store results in tally{}."

        self.tally = {}
        for key in self.villager_votes.keys():
            lynchee = self.villager_votes[key]
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
            self.villager_votes[lyncher] = lynchee
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
        if self.villager_votes.keys():
            for n in self.live_players:
                if not self.villager_votes.has_key(n):
                    non_voters.append(n)
                else:
                    voters.append(n)
            if non_voters:
                self.bot.pubout(channel, "The following have no votes registered: %s"
                        % (non_voters))
	        self.bot.pubout(channel, "The votes are as follows: %s"
	                % (self.villager_votes))
            else:
                self.bot.pubout(channel, "Everyone has voted.")
	    self.bot.pubout(channel, "The votes are as follows: %s"
	        % (self.villager_votes))
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

    def cmd_see(self, args, channel, user):
        if len(args) == 1:
            viewee = self.match_name(args[0].strip())
            if viewee is not None:
                self.see(channel, user, viewee.strip())
                return
        self.reply(channel, user, "See whom?")

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
        self.reply(channel, user, "I am a bot written in Python "
                "using the python-irclib library")
        self.reply(channel, user, "My source code is available at %s" % svn_url)

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
            pass
            #self.reply(channel, user, "That command makes no sense.")
        elif self.time == "night":
            pass
            #self.reply(channel, user, "SSSHH! It's night, everyone's asleep!")
        elif self.time == "day":
            pass
            #self.reply(channel, user, "Hm? Get back to lynching.")
