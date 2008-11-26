import log
from random import choice
from BasePlugin import BasePlugin

class Decide(BasePlugin):
    __plugintype__ = "active"
    
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.activeGame = False
        self.output = True

# LOAD: This will load our rules.
sub load {
    my $rulefile = option('global', 'rules');
    my ($lfound, $rfound);
    my $deleted = 0;
    print "Loading $rulefile... "
    $loaded = 0;
    if(open(RULES, $rulefile)) {
        foreach(<RULES>) {
            chomp;
            s/\r//;
            my @rule = split (/\t/);
            $chat_words{$rule[0]}{$rule[1]}[1] = $rule[2];
            $chat_words{$rule[1]}{$rule[0]}[0] = $rule[2];
        }
        close(RULES);
        print "Rules loaded successfully!\n", DEBUG_NO_PREFIX);
        $loaded = 1;

        print "Checking for lost words... "
        foreach my $word (keys(%chat_words)) {
            next if ($word =~ /^__[\!\?]?[A-Z]*$/);
            $lfound = 0;
            $rfound = 0;
            foreach (keys(%{$chat_words{$word}})) {
                # If we find out a word has any links to the right, we're good.
                if (defined $chat_words{$word}{$_}[1] && $rfound == 0) {
                    $rfound = 1;
                }
                # If we find out a word has any links to the left, we're good.
                if (defined $chat_words{$word}{$_}[0] && $lfound == 0) {
                    $lfound = 1;
                }
            }
            if ($lfound == 0 || $rfound == 0) {
                print "\n" if !$deleted;
                $deleted = 1;
                delete_word($word, 0);
            }
        }
        if (!$deleted) {
            print "No lost words found!\n");
        } else {
            print "All lost words removed successfully.\n");
        }

    } elsif (!-e $rulefile) {
        &debug(DEBUG_WARN, "File does not exist and will be created on save.\n");
        $loaded = 1;
    } else {
        &debug(DEBUG_ERR, "Cannot read from the rules file! This session will not be saved!\n");
    }
}

    def pubout(self, channel, message):
        pass

    # Event handlers for other users
    def user_join(self, channel, username):
        pass

    def user_part(self, channel, username):
        pass

    def user_quit(self, username, reason=""):
        pass

    def user_nickchange(self, channel, username, newname):
        pass

    # Event handlers for this bot
    def bot_connect(self):
        pass

    def bot_join(self, channel):
        pass

    def bot_kicked(self, channel, kicker="", reason=""):
        pass

    def bot_disconnect(self):
        pass


    # Event handlers for incoming messages
    def msg_channel(self, channel, user, message):
        pass
            
    def msg_action(self, channel, user, message):
        pass

    def msg_private(self, user, message):
        pass

    def msg_notice(self, user, message):
        pass

    def channel_names(self, channel, nameslist):
        pass