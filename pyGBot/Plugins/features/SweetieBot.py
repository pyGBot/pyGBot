##
##    pyGBot - Versatile IRC Bot
##    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov
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

################################################################################
## 
## Plugin
## 
################################################################################

from random import choice, shuffle, randint

class SweetieBot:
    def __init__(self, bot, options):
        self.bot = bot
        self.activatemsg =      [
                                "INPUT NAME SWEETIE-BELLE", 
                                "Oops. An error has occurred.", 
                                "THE FUN BEGINS IMMEDIATELY!",
                                "I have arranged objects in an aesthetically pleasing manner!", 
                                "My primary function is failure."
                                ]
        self.kickmsg =          [
                                "INCOMING MORTAR!", 
                                "One lives one's death, one dies one's life.", 
                                "Life is such a fleeting yet precious thing.", 
                                "This reminds me of a song I wrote! Just because you feel upset, does not mean you have to yell.", 
                                "Why is it funny to laugh at someone else's misery? Oh look, our characters are so malevolent and heartless! Maybe next we'll hear a new cheap catchphrase!",
                                "$who, stop, the war was ten years ago you don't need to have a breakdown!",
                                "I just wish there was a way to make $kicked see that we are both flesh and blood."
                                ]
        self.idlemsg =          [
                                "~When I'm feeling broken down, she has always got my back, mmmhmm something giant hat, yes I love my sister Rarity~", 
                                "The fun levels will be at maximum efficiency! I shall acquire my yo-yo, hammer, and other objects of FUN!", 
                                "$someone! Have I ever told you that I love you?", 
                                "Scanning... Arts and crafts located! Drawing... Drawing... Hmmm. Insufficient beauty.", 
                                "Did I make a mistake?",
                                "Scanning... scanning... fabulous item located.", 
                                "FUN LEVEL: 0%",
                                "~the race has begun / we must run fast / jump over the mud / having a good time / where's applejack? / she fell in the mud / are you ok? / we can still win this~",
                                "~jump in a bucket / that looked like it hurt / i know what pain is / it's great to be alive / but when I am feeling weak / and when i am feeling down / she is there to lift me up / lift me up over this box / yes i love my sister applejack~",
                                "~eating some pie / no time to chew / pushing some hay / no time to lose / pushing this hay really far / (pushing hay is really hard!) / running in a circle yes / having so much fun hooray / gotta chuck some grapes? / throw them with your face / sister toss and squish and squash and~",
                                "~making tacky jelly / put it on your head / we're gonna win the race / BECAUSE I AM A GOOD RACER / i am running oh so fast / fun levels are to the max / applejack flies through the air / apples fall without a care / apples are not meant to fly / no apple gets left behind / when small things get kicked around / they just might destroy the town~",
                                "~when i'm feeling broken down / she has always got my back / life is worth protecting now / place it in this giant hat / yes i love my sister applejack~",
                                "~now we're racing toward the finish line / nothing matters once you die but we're along for the ride / and you sacrifice the meaning just to have the words rhyme / in the end it all comes down to just how far we can slide~"
                                ]
        self.addressedmsg =     [
                                "That dress looks fabulous!", 
                                "I love you $who!", 
                                "THE FUN BEGINS IMMEDIATELY!",
                                "The chances of success are 100%!", 
                                "Because life is worth protecting?",
                                "I have arranged objects in an aesthetically pleasing manner!", 
                                "Oops. An error has occured.",
                                "Harrumph. You do not fool me, $who-BOT! As a robot, you are merely programmed to say that!",
                                "I hope you achieve maximum levels of fun. Initiating cry sequence.", 
                                "Look how fast I can run away!",
                                "My primary function is failure.",
                                "I wish MY house had a fence.",
                                "Yes! $someone loves to jump up and down!"
                                "Your lack of bloodlust on the battlefield is proof positive that you are an automaton!",
                                "SET PHASERS TO HUG!",
                                "Error.",
                                "You all decieved me?",
                                "Gasp!",
                                "Initiate happy cry sequence!",
                                "She just kept screaming all day! Like, what's up with that?",
                                "Oh, I was just planting this tiny tree and pondering the fragility of life.",
                                "Well, we're not supposed to think about death... but okay!",
                                "Soo... you're the best sister ever and a SHAPESHIFTER?",
                                "Ooh! Or we could form a club!",
                                "I am displaying all of your fashion items! Hooray!",
                                "But I'm always screwing things up!",
                                "You're making unstylish jelly? Aren't you afraid the fashion police will come and beat you with their fabulous batons?",
                                "I'm leaving! ow. ow. ow. ow. ow.",
                                "If the world isn't going to love me then I'll teach it to FEAR ME instead!",
                                "Help! Assistance is required! I believe there's something wrong with me!",
                                "Why not! Could it be because you are a ROBOT!",
                                "REJECT! I am uninstalling you from my heart drive and reinstalling $someone!",
                                "AND WE ALL LIKE ICE CREAM!",
                                "Then how do you explain those acting classes? You clearly have difficulties expressing real emotions!",
                                "I bet you don't even have a war face!",
                                "I have so much strength inside of me that you don't even KNOW what I could do!",
                                "Well at least I don't spend every Veteran's Day sobbing on the floor!",
                                "And if you have nothing to fear, then why won't you join me?",
                                "I love you! I love you! I love you! love you love you love you love you you love love you love you"
                                ]
        self.welcomemsg = ["Hey look, it's Pinkie Pie! http://goo.gl/cXb2E", "What's Pinkie doing over there? http://www.youtube.com/watch?v=7z5Ngl7AXxU", "Have some cider! http://goo.gl/lVaqg"]
        self.ponies =           ["Mr. Cake", "Daring Do", "Fluttershy", "Nightmare Moon", "Rarity", "Berry Pinch", "Zecora", "Screwball", "Soarin'", "Hayseed", "Sweetie Belle", "Snips", "Rainbow Dash", "Lotus", "Pinkie Pie", "Aunt Orange", "Pokey Pierce", "Photo Finish", "Twilight Sparkle", "Pumpkin Cake", "Spitfire", "Filthy Rich", "Fleur de Lis", "Colgate", "Matilda", "Lily", "Applejack", "DJ-Pon3", "Cherry Jubilee", "Spike", "Mrs. Cake", "Princess Celestia", "Nurse Redheart", "Cokepone", "Carrot Top", "Pound Cake", "Scootaloo", "Berry Punch", "Cranky Doodle Donkey", "Uncle Orange", "Silver Spoon", "Flim", "Ponybot", "Aloe", "Gilda", "Doctor Whooves", "Twist", "Snails", "Daisy", "Ace", "Flummoxed", "Princess Cadence", "Cloud Kicker", "Mayor", "Pipsqueak", "Discord", "Hoity Toity", "Rose", "Granny Smith", "Screw Loose", "Sheriff Silverstar", "Caramel", "Cheerilee", "Derpy Hooves", "Octavia", "Flam", "Princess Luna", "Prince Blueblood", "Sweet Tart", "Sapphire Shores", "Apple Fritter", "Chief Thunderhooves", "Apple Bloom", "Diamond Tiara", "Fancy Pants", "Pizza Pony", "Trixie", "Big Macintosh", "Dinky Hooves", "Little-Strongheart", "Lyra"]           
        self.recentactive = {}
        self.channelactive = 0
        
    def activate(self, channel=None):
        """
        Called when the plugin is activated.
        """
        return True

    def deactivate(self, channel=None):
        """
        Called when the plugin is deactivated.
        """
        return True

    # Event handlers for other users
    def user_join(self, channel, username):
        self.recentactive[username] = 0

    def user_part(self, channel, username):
        if username in self.recentactive:
            del self.recentactive[username]

    def user_kicked(self, channel, username, kicker, message=""):
        if username in self.recentactive:
            del self.recentactive[username]
        self.recentactive[kicker] = 0
        self.bot.pubout(channel, self.stringreplace(choice(self.kickmsg), kicker, username))

    def user_quit(self, username, reason=""):
        if username in self.recentactive:
            del self.recentactive[username]

    def user_nickchange(self, username, newname):
        if (username in self.recentactive.keys()):
            del self.recentactive[username]
        self.recentactive[newname] = 0

    # Event handlers for this bot
    def bot_join(self, channel):
        self.channel = channel
        self.bot.pubout(channel, self.stringreplace(choice(self.activatemsg)))

    # Event handlers for incoming messages
    def msg_channel(self, channel, user, message):
        self.recentactive[user] = 0
        self.channelactive = 0
        self.parsemessage(channel, user, message)

    def msg_action(self, channel, user, message):
        self.recentactive[user] = 0
        self.channelactive = 0
        self.parsemessage(channel, user, message)

    # Other system event handlers
    def timer_tick(self):
        remove = []
        for user in self.recentactive:
            self.recentactive[user] = self.recentactive[user] + 1
            if self.recentactive[user] >= 3600:
                remove.append(user)
        for user in remove:
            del self.recentactive[user]
        self.channelactive = self.channelactive + 1
        if self.channelactive == 1800:
            self.bot.pubout(self.channel, self.stringreplace(choice(self.idlemsg)))
            
    def stringreplace(self, message, user=None, user2=None):
        keys = list(self.recentactive.keys())
        if user in keys:
                keys.remove(user)
        if (len(keys) > 0):
            message = message.replace("$someone", choice(keys))
        else:
            message = message.replace("$someone", choice(self.ponies))
        if user:
            message = message.replace("$who", user)
        else:
            message = message.replace("$who", choice(self.ponies))
        if user2:
            message = message.replace("$kicked", user2)
        else:
            message = message.replace("$kicked", choice(self.ponies))
        return message
    
    def parsemessage(self, channel, user, message):
        if (message.lower().find(self.bot.nickname.lower())) != -1:
            if (message.lower().find("welcome") != -1):
                self.bot.pubout(channel, "INITIATE WELCOME PROTOCOL: " + choice(self.welcomemsg))
            elif (message.lower().find("bath") != -1):
                self.bot.pubout(channel, "The water makes me feel funny.")
            elif (message.lower().find("name") != -1 or message.lower().find("hello") != -1):
                self.bot.pubout(channel, "INPUT NAME SWEETIE-BELLE")
            elif (message.lower().find("sheep") != -1):
                self.bot.pubout(channel, "Why have I seen these creatures in my dreams?")
            elif (message.lower().find("war face") != -1):
                self.bot.pubout(channel, "RAAWR! SEE, MINE'S BETTER!")
            elif (message.lower().find("love") != -1):
                vowel = self.findfirstvowel(user.lower())
                usercpy = user[:vowel[1]] + (vowel[0]*5) + user[vowel[1]+1:]
                self.bot.pubout(channel, "%s! I love you so much!" % usercpy)
            elif (message.lower().find("lesson") != -1 or message.lower().find("letter") != -1):
                self.bot.pubout(channel, self.stringreplace("It's a good thing that earlier I swallowed that microtape from $someone.\nDear Princess Celestia, today in a seperate adventure at the Brohoof Bash, I learned the importance of loving your brother, even if you don't always get along! Your faithful student, $someone.", user))
                self.bot.pubout(channel, self.stringreplace("Hello? Is this thing on? Okay. My name's $someone, and this is my audition for the Hearth's Warming Eve pageant. Okay, here we go. ~Look at me, I will never pass for a perfect bride, or a perfect daughter, can it be I'm not meant to play this part? Who is that girl I see? Staring straight, back at me? When will my reflection show, who I am, inside?~"))
            else:
                self.bot.pubout(channel, self.stringreplace(choice(self.addressedmsg), user))
        else:
            rand = randint(0, 200)
            if rand == 50:
                self.bot.pubout(channel, self.stringreplace("$who, I love you!", user))
            elif rand == 150:
                self.bot.pubout(channel, "I love you!")
    
    def findfirstvowel(self, msg):
        a = ["a", msg.find("a")]
        e = ["e", msg.find("e")]
        i = ["i", msg.find("i")]
        o = ["o", msg.find("o")]
        u = ["u", msg.find("u")]
        y = ["y", msg.find("y")]
        
        sort = []
        
        if (a[1] > -1):
            sort.append(a[1])
        if (e[1] > -1):
            sort.append(e[1])
        if (i[1] > -1):
            sort.append(i[1])
        if (o[1] > -1):
            sort.append(o[1])
        if (u[1] > -1):
            sort.append(u[1])
        if (y[1] > -1):
            sort.append(y[1])
            
        sort.sort()
        
        if len(sort) == 0:
            return None
        else:
            if (a[1] == sort[0]):
                return a
            elif (e[1] == sort[0]):
                return e
            elif (i[1] == sort[0]):
                return i
            elif (o[1] == sort[0]):
                return o
            elif (u[1] == sort[0]):
                return u
            elif (y[1] == sort[0]):
                return y