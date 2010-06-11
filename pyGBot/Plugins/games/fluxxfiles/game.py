
import random
from itertools import count

def pretty_print_list(L, use_both=False):
    L = [t for t in L if t is not None]
    if len(L) == 0:
        return ""
    elif len(L) == 1 and L[0] is not None:
        return str(L[0])
    elif use_both and len(L) == 2:
        return "both %s and %s" % tuple(L)
    return "%sand %s" % ((('%s, ' * (len(L)-1)) % tuple(L[:-1])), L[-1])

def pp_index(L, start=1, use_both=False):
    return pretty_print_list(["%d: %s" % (i, v) for i, v in zip(count(start), L)], use_both)

def plural(L):
    return "" if len(L) == 1 else "s"

class Deck(object):

    is_removable = False
    
    def __init__(self):
        self._cards = set()
        self.short_title_map = {}
    
    @property
    def cards(self):
        return self._cards
        
    @cards.setter
    def cards(self, value):
        for c in value:
            c.owner = self
        self._cards = set(value)
        
        self.short_title_map = {}
        for card in value:
            self.short_title_map[card.short_title] = card
    
    def find_card(self, short_title):
        return self.short_title_map[short_title]

    @property
    def undealt_cards(self):
        # Owner is set to the deck when undealt.
        return [c for c in self._cards if c.owner is self]
    
    def __contains__(self, card):
        return card in self._cards or card in self.short_title_map
    
    def __len__(self):
        return len(self._cards)
    
class Card(object):
    
    def __init__(self, title, short_title):
        self.title = title
        # short_title must be unique!
        self.short_title = short_title
        self.owner = None

    def del_owner(self):
        if self.owner and self.owner.is_removable and self in self.owner.cards:
            print "Removing '%s' from %r" % (self, self.owner)
            self.owner.cards.remove(self)
            print self.owner.cards
            if hasattr(self.owner, "short_title_map") and \
                    self.short_title in self.owner.short_title_map:
                del self.owner.short_title_map[self.short_title]
        
    def __repr(self):
        return "Card(%r)" % self.title
    def __str__(self):
        return self.title
    def __iter__(self):
        return iter([self])
    def __getitem__(self, i):
        if i == 0:
            return self
    
class CardPile(object):

    is_removable = True
    
    def __init__(self, name=""):
        self.cards = []
        self.name = name
        self.short_title_map = {}
    
    def shuffle(self):
        random.shuffle(self.cards)

    def receive(self, R):
        for card in R:
            print card
            card.del_owner()

        if not isinstance(R, CardPile):
            L = []
            for card in R:
                ret = self.receive_card(card)
                if ret is True:
                    self.cards.append(card)
                    self.short_title_map[card.short_title] = card
                    card.owner = self
                    L.append(card)
                elif ret is not False:
                    self.cards.append(ret)
                    self.short_title_map[ret.short_title] = ret
                    ret.del_owner()
                    ret.owner = self
                    L.append(ret)
            return L

    def receive_card(self, card):
        """
        Return True to add a card to this pile, otherwise return False or
        another card to add instead of the argument provided.
        """
        
        return True
    
    def deal(self, piles, num_cards):
        for c in xrange(num_cards):
            for pile in piles:
                pile.receive(self.draw(1))
    
    def draw(self, num_cards):
        """
        Return num_cards cards from the top of the pile.
        """
        # L = self.cards[:num_cards]
        # for card in L:
        #     self.cards.remove(card)
        #     del self.short_title_map[card.short_title]
        # return L
        return self.cards[:num_cards]
    
    def __contains__(self, card):
        return card in self.cards or card in self.short_title_map
    
    def __iter__(self):
        return iter(self.cards[:])

    def __repr__(self):
        return self.name or object.__repr__(self)
    
    def __str__(self):
        return pretty_print_list(self.cards)
    
    def __len__(self):
        return len(self.cards)
    
    def __getitem__(self, i):
        return self.cards[i]
    
    def find_card(self, short_title):
        return self.short_title_map[short_title]

    
class Player(object):
    
    player_count = 1
    
    def __init__(self, name=None):
        if name == None:
            name = "Player %d" % Player.player_count
        Player.player_count += 1
        self.name = name
        self._hand = None
    
    @property
    def hand(self):
        return self._hand
    
    @hand.setter
    def hand(self, hand):
        hand.player = self
        self._hand = hand

    def __getattr__(self, i):
        if self._hand is not None:
            return getattr(self._hand, i)
        return None

    def __str__(self):
        return self.name
