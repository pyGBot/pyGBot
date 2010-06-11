
from pyGBot.Plugins.games.fluxxfiles.fluxx import FluxxCard
from pyGBot.Plugins.games.fluxxfiles.game import pretty_print_list

class KeeperCard(FluxxCard):
    information = """
When you play this card, place it face up on the table
in front of you.
    """.strip()
    type = "Keeper"
    in_play = False
    is_creeper = False
    
    def __init__(self, title, short_title=""):
        if short_title == "":
            if " " in title:
                s = ''.join(zip(*title.split())[0]) # Figure this one out... :)
            else:
                s = title[:2].upper()
            short_title = s
        short_title = self.type[0] + "_" + short_title
        FluxxCard.__init__(self, title, short_title, "")
    
    def play(self, player):
        player.keepers.receive(self)
        self.in_play = True
    
    @property
    def title_uncapped(self):
        if self.title.startswith("The"):
            return "t" + self.title[1:]
        return self.title

class CreeperCard(KeeperCard):
    information = """
You cannot hold this card, but must place it face up in front
of you as soon as you get it. If you drew it, immediately draw another
card to replace it.
    """.strip()
    type = "Creeper"
    is_creeper = True
    def __init__(self, title, description="", short_title=""):
        KeeperCard.__init__(self, title, short_title)
        self.description = description
