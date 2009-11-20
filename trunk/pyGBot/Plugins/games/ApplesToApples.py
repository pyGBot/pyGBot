##
##    Apples To Apples - a plugin for pyGBot
##    Copyright (C) 2008 Morgan Lokhorst-Blight
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
import random
from pyGBot.BasePlugin import BasePlugin

# Card lists. This is the Party basic set, without expansions.
# Considering adding the expansions in the near future.

GREENCARDS = {
'Absurd':'ridiculous, senseless, foolish',
'Addictive':'obsessive, consuming, captivating',
'Adorable':'lovable, charming, delightful',
'Aged':'old, ancient, mature',
'American':'U.S. Citizen, Yankee, Apple Pie',
'Ancient':'elderly, old, antique',
'Animated':'lively, exuberant, spirited',
'Annoying':'irritating, bothersome, teasing',
'Appetizing':'appealing, tasty, flavorful',
'Arrogant':'egotistical, overconfident, conceited',
'Awesome':'amazing, remarkable, majestic',
'Awkward':'clumsy, bumbling, uncoordinated',
'Believable':'trustworthy, credible, convincing',
'Bogus':'fraudulent, phony, insincere',
'Boisterous':'loud, rambunctious, rowdy',
'Bold':'daring, brave, courageous',
'Boring':'dull, tedious, monotonous',
'Bright':'brilliant, radiant, shiny',
'Brilliant':'dazzling, gleaming, intelligent',
'Busy':'occupied, meddlesome, engrossed',
'Calm':'peaceful, tranquil, placid',
'Casual':'easygoing, blase, nonchalant',
'Charismatic':'alluring, magnetic, charming',
'Charming':'captivating, enchanting, fascinating',
'Cheesy':'trashy, tawdry, far-fetched',
'Chewy':'gummy, rubbery, stringy',
'Chunky':'lumpy, chubby, bumpy',
'Classic':'timeless, definitive, vintage',
'Clean':'washed, pure, tidy',
'Clueless':'unaware, oblivious, ignorant',
'Cold':'chilly, icy, aloof',
'Colorful':'vivid, brilliant, kaleidoscopic',
'Comfortable':'cozy, snug, restful',
'Comical':'funny, hilarious, amusing',
'Complicated':'difficult, complex, involved',
'Confused':'muddled, bewildered, perplexed',
'Cool':'chilly, hip, cold-blooded',
'Corrupt':'dishonest, underhanded, shady',
'Cosmic':'limitless, planetary, far out',
'Cosmopolitan':'sophisticated, urbane, well-informed',
'Courageous':'brave, gallant, dauntless',
'Cowardly':'fearful, afraid, spineless',
'Cranky':'crabby, cantankerous, grouchy',
'Crazed':'insane, wild, deranged',
'Crazy':'insane, bizarre, wacky',
'Creative':'imaginative, artistic, original',
'Creepy':'frightening, slithering, scary',
'Cruel':'mean, harsh, merciless',
'Cuddly':'loving, tender, huggable',
'Cute':'pretty, perky, delightful',
'Dainty':'delicate, fragile, thin',
'Dangerous':'risky, chancy, hazardous',
'Dead':'deceased, expired, unresponsive',
'Deadly':'fatal, lethal, murderous',
'Delicate':'dainty, tender, elegant',
'Delicious':'tasty, pleasing, appetizing',
'Delightful':'pleasing, enjoyable, charming',
'Demanding':'difficult, exacting, bothersome',
'Depressing':'dismal, gloomy, sad',
'Desperate':'frantic, headlong, reckless',
'Dignified':'stately, honorable, distinguished',
'Dirty':'unclean, soiled, impure',
'Distinguished':'dignified, extraordinary, acclaimed',
'Disturbing':'unsettling, troubling, worrisome',
'Dramatic':'exciting, sensational, theatrical',
'Dreamy':'fanciful, whimsical, heavenly',
'Dull':'boring, stupid, blunt',
'Dysfunctional':'impaired, damaged, maladjusted',
'Earthy':'unrefined, natural, crude',
'Easy':'effortless, gentle, promiscuous',
'Eccentric':'peculiar, odd, bizarre',
'Elitist':'snobbish, arrogant, smug',
'Emotional':'passionate, moving, volatile',
'Eternal':'timeless, immortal, perpetual',
'European':'of Europe, from Europe, about Europe',
'Exciting':'thrilling, breathtaking, arousing',
'Exhausting':'weakening, tiring, draining',
'Expensive':'costly, valuable, exorbitant',
'Explosive':'bursting, blasting, dangerous',
'Exquisite':'excellent, refined, flawless',
'Extreme':'exceptional, superlative, radical',
'Fabulous':'marvelous, wonderful, incredible',
'Fake':'unreal, counterfeit, deceptive',
'Fancy':'showy, ornate, decorated',
'Fantastic':'awesome, outrageous, imaginary',
'Feminine':'womanly, ladylike, unmanly',
'Filthy':'dirty, foul, unclean',
'Flirtatious':'brazen, saucy, forward',
'Foreign':'alien, unfamiliar, exotic',
'Fragrant':'aromatic, odorous, perfumed',
'Frazzled':'exhausted, frayed, worn',
'Fresh':'new, original, good',
'Friendly':'affectionate, comforting, welcoming',
'Frightening':'scary, horrifying, awesome',
'Frivolous':'trivial, silly, shallow',
'Funky':'groovy, psychedelic, hip',
'Funny':'amusing, comic, odd',
'Furious':'angry, raging, wild',
'Fuzzy':'downy, unclear, furry',
'Glamorous':'beautiful, dazzling, stylish',
'Glitzy':'flashy, showy, gaudy',
'Global':'world-wide, spherical, universal',
'Glorious':'magnificent, delightful, splendid',
'Goody-Goody':'sweet, well-behaved, virtuous',
'Graceful':'elegant, supple, limber',
'Handsome':'attractive, elegant, fine',
'Hardworking':'industrious, diligent, busy',
'Harmful':'hurtful, unhealthy, damaging',
'Haunting':'unforgettable, bewitching, unearthly',
'Healthy':'hearty, robust, wholesome',
'Heartless':'insensitive, cruel, uncaring',
'Hilarious':'funny, witty, amusing',
'Honorable':'honest, just, virtuous',
'Hopeless':'pessimistic, desperate, downhearted',
'Horrifying':'offensive, abominable, disgusting',
'Hostile':'antagonistic, aggressive, warlike',
'Hot':'blazing, heated, spicy',
'Idiotic':'foolish, dumb, moronic',
'Important':'significant, substantial, momentous',
'Industrious':'diligent, busy, hard-working',
'Influential':'powerful, prominent, important',
'Innocent':'guiltless, pure, naive',
'Insane':'psychotic, deranged, mad',
'Inspirational':'exhilarating, inspiring, stimulating',
'Insulting':'offending, discourteous, rude',
'Intelligent':'bright, smart, brainy',
'Intense':'extreme, passionate, strained',
'Irresistible':'overpowering, overwhelming, compelling',
'Irritating':'annoying, troublesome, provoking',
'Juicy':'drippy, luscious, tantalizing',
'Lazy':'lifeless, apathetic, weary',
'Legendary':'famous, distinctive, prominent',
'Loud':'noisy, boisterous, deafening',
'Lovable':'adorable, endearing, cuddly',
'Lucky':'fortunate, serendipitous, favored',
'Luscious':'delicious, savory, juicy',
'Luxurious':'opulent, lavish, sumptuous',
'Magical':'enchanting, miraculous, marvelous',
'Manly':'masculine, virile, strong',
'Masculine':'male, manly, virile',
'Meek':'shy, mild, timid',
'Melodramatic':'theatrical, sensational, showy',
'Mischievous':'naughty, prankish, sly',
'Miserable':'wretched, pitiful, forlorn',
'Misunderstood':'not grasped, not learned, not absorbed',
'Mysterious':'secretive, puzzling, strange',
'Mystical':'spiritual, secretive, esoteric',
'Naive':'unsophisticated, childlike, simple',
'Nasty':'mean, inclement, offensive',
'Natural':'pure, simple, unadorned',
'Neat':'tidy, orderly, cool',
'Neglected':'ignored, disregarded, rejected',
'Nerdy':'unhip, uncool, dorky',
'Normal':'usual, common, ordinary',
'Obnoxious':'offensive, repulsive, annoying',
'Odd':'different, eccentric, bizarre',
'Offensive':'insulting, vulgar, attacking',
'Ordinary':'usual, common, plain',
'Organic':'natural, clean, biological',
'Outrageous':'shocking, scandalous, disgraceful',
'Overwhelming':'exhaustive, breathtaking, monumental',
'Painful':'hurtful, agonizing, unbearable',
'Pathetic':'pitiful, distressing, heart-rending',
'Patriotic':'nationalistic, loyal, public-spirited',
'Peaceful':'serene, restful, calm',
'Perfect':'faultless, consummate, exact',
'Philosophical':'thoughtful, contemplative, wise',
'Phony':'false, artificial, imitation',
'Playful':'fun, frisky, entertaining',
'Popular':'well-liked, accepted, preferred',
'Powerful':'strong, forceful, robust',
'Primitive':'prehistoric, primal, uncivilized',
'Principled':'conscientious, ethical, scrupulous',
'Profound':'deep, wise, thoughtful',
'Puffy':'swollen, billowy, bloated',
'Pure':'innocent, unadulterated, chaste',
'Quiet':'peaceful, silent, calm',
'Radiant':'shining, glowing, sparkling',
'Radical':'unconventional, revolutionary, extreme',
'Rare':'scarce, unusual, half-cooked',
'Realistic':'authentic, lifelike, reasonable',
'Refined':'well-bred, purified, cultivated',
'Refreshing':'brisk, invigorating, rejuvenating',
'Relaxing':'restful, calming, peaceful',
'Repulsive':'disgusting, offensive, foul',
'Responsible':'accountable, obligated, mature',
'Revolutionary':'innovative, rebellious, radical',
'Rich':'wealthy, affluent, moneyed',
'Ridiculous':'preposterous, absurd, ludicrous',
'Risky':'hazardous, daring, speculative',
'Rough':'scratchy, uneven, jagged',
'Saintly':'virtuous, angelic, divine',
'Sappy':'gooey, mushy, romantic',
'Scary':'frightening, absurd, ugly',
'Scenic':'picturesque, dramatic, panoramic',
'Selfish':'stingy, greedy, miserly',
'Senseless':'meaningless, absurd, foolish',
'Sensitive':'susceptible, sympathetic, tender',
'Sensual':'tactile, pleasing, sexual',
'Sexy':'arousing, appealing, seductive',
'Shallow':'superficial, trivial, not deep',
'Sharp':'pointed, keen, acute',
'Shiny':'reflective, gleaming, polished',
'Shocking':'frightening, electrifying, startling',
'Shy':'bashful, timid, cautious',
'Silly':'goofy, absurd, nonsensical',
'Smart':'intelligent, stylish, witty',
'Smelly':'stinky, odorous, rank',
'Smooth':'even, level, flat',
'Snappy':'stylish, trendy, fast',
'Soft':'malleable, pliable, mushy',
'Speedy':'quick, rapid, fast',
'Spicy':'flavorable, tangy, hot',
'Spiritual':'religious, inspired, supernatural',
'Spooky':'scary, weird, ghostly',
'Spunky':'perky, lively, spirited',
'Squeaky Clean':'pure, immaculate, unapproachable',
'Stereotyped':'pigeonholed, caricatured, characterized',
'Stunning':'astonishing, staggering, astounding',
'Sultry':'sweltering, humid, sensual',
'Sweet':'sugary, caring, good',
'Swift':'quick, speedy, expeditious',
'Talented':'gifted, clever, skillful',
'Tame':'subdued, gentle, trained',
'Technological':'scientific, futuristic, mechanical',
'Temperamental':'moody, irritable, short-tempered',
'Timeless':'classic, ageless, well-established',
'Touchy-Feely':'affectionate, tactile, huggy',
'Tough':'strong, firm, difficult',
'Trustworthy':'honest, reliable, unfailing',
'Twisted':'distorted, warped, perverted',
'Unbelievable':'incredible, far-fetched, impossible',
'Unforgettable':'notable, impressive, remarkable',
'Unhealthy':'risky, sickly, dangerous',
'Unnatural':'abnormal, artificial, bizarre',
'Unreal':'imaginary, illusionary, unbelievable',
'Unscrupulous':'unethical, corrupt, unprincipled',
'Unusual':'rare, odd, uncommon',
'Useless':'worthless, ineffective, unneeded',
'Violent':'furious, vicious, destructive',
'Virtuous':'worthy, righteous, chaste',
'Visionary':'idealistic, prophetic, far-seeing',
'Weird':'abnormal, peculiar, odd',
'Wicked':'evil, corrupt, depraved',
'Wild':'untamed, savage, ferocious',
'Witty':'clever, humorous, cunning',
'Woebegone':'dismal, sorrowful, bummed out',
'Worldly':'experienced, sophisticated, materialistic',
'Zany':'crazy, funny, wacky',
}

REDCARDS = {'A Bad Haircut':'\x02The perfect start to a bad hair day.\x0f',
'A Bull Fight':'\x02Also known as "la fiesta brava" (the brave festival).\x0f A whole lot of bull..',
'A Car Crash':'"Hey, it was an accident!"',
'A Cheap Motel':'No charge for the cockroaches.',
'A Crawl Space':'Where you\'ll find something the cat dragged in.',
'A Dozen Red Roses':'When eleven just won\'t do.',
'A Flat Tire':'"Whaddya mean, there\'s no spare?"',
'A Full Moon':'\x02"When the moon hits your eye like a big pizza pie, that\'s amore!"\x0f -Dean Martin',
'A Haunted House':'Maybe if people would STOP building their dream homes on ancient burial grounds ...',
'A High School Bathroom':'\x02"Fools rush in where angels fear to tread" \x0f-Alexander Pope',
'A Honeymoon':'\x02America\'s top honeymoon spots are Hawaii, Niagara Falls, Las Vegas and Florida. You can get there by air, land, sea \x0f... or shotgun.',
'A Locker Room':'Steamy atmosphere ... bawdy humor ... sweaty bodies ... HEY! Sounds like Cable TV!',
'A Morgue':'\x02"Given strange eons, even death may die..." \x0f-H.P. Lovecraft',
'A Nine Iron':'\x02A golf club best used on short shots \x0for large opponents.',
'A School Bus':'\x02The only thing we have to fear is fear itself. \x0f-Franklin D. Roosevelt',
'A School Cafeteria':'Food fight!',
'A Sunrise':'\x02"But he who kisses the joy as it flies/ Lives in eternity\'s sunrise." \x0f-William Blake',
'A Sunset':'\x02The sun never set on the British Empire \x0f... because God didn\'t trust the English in the dark.',
'A Tree House':'\x02Your first high-rise apartment.\x0f',
'A Used Car Lot':'One of the most honest places around. Honest ...',
'Abraham Lincoln':'\x021809-65, 16th U.S. president, led the Union to victory in the American Civil War and abolished slavery.\x0f Was assassinated for his efforts.',
'Adam Sandler':'\x021966- , American comedian, film star, and Saturday Night Live alumnus. Genius or goofball - you make the call.',
'Adolph Hitler':'\x021889-1945, turned Germany into a militarized dictatorship, caused the slaughter of millions and launched World War II.\x0f',
'AIDS':'\x02Acquired Immune Deficiency Syndrome.\x0f',
'Airline Food':'Since when is a bag of peanuts considered a meal?',
'Al Pacino':'\x021940- , Oscar winning American actor and star of "The Godfather," "Dog Day Afternoon" and "Scent Of A Woman." \x0fOne very intense guy.',
'Albert Einstein':'\x021879-1955, German-born American physicist and Nobel laureate who created theories of relativity. \x0fNice hair.',
'Alfred Hitchcock':'\x021899-1980, British-born American director and producer of brilliant psychological thrillers. \x0fRight, mother? MOTHER!',
'Alien Abductions':'\x02There was a blinding light \x0f-and she was gone!',
'Americans':'How many Americans does it take to screw in a light bulb? THAT\'S NOT FUNNY! WE\'RE SUING!',
'Amputations':'\x02"A SCRATCH? Your arm\'s off!" \x0f- Monty Python and the Holy Grail.',
'Angry Hornets':'Who put the bees in their bonnets?.',
'Andy Warhol':'\x021928-87, American painter and filmmaker, a leader of the pop art movement. \x0fFamous for slightly more than 15 minutes.',
'Anne Frank':'\x021929-45, German Jewish girl who wrote in her diary about her family hiding from the Nazis. She died in a concentration camp.\x0f',
'Antarctica':'\x02Home to the lowest temperature ever recorded on earth, -126.9 F.\x0f',
'Anthony Hopkins':'\x021937- , British actor starred in The Elephant Man, Howard\'s End, and, of course, The Silence Of The Lambs. Knighted in 1992.',
'Apple Pie':'\x02It\'s as American as ... as ... something ...\x0f',
'Apples':'\x02More than 40 million metric tons are produced worldwide every year. \x0fHow \'bout them apples?',
'Armed Robbery':'\x02You got your Robbery, your Armed Robbery, your Strong Armed Robbery, and, of course, the \x0ffive finger discount.',
'Assembly Lines':'Faster. FASTER!',
'At My Parent\'s House':'Like never-never land, you\'re never seen as an adult here.',
'Atlantis':'Mythological city where the folks had that sinking feeling.',
'Atomic Bombs':'\x02The Italian physicist Enrico Fermi succeeded in producing the first nuclear chain reaction in 1942, at the University of Chicago.\x0f',
'Attack On Pearl Harbor':'\x02"Yesterday, December 7th, 1941, a date which will live in infamy ..." \x0f-Franklin D. Roosevelt',
'Austin Powers':'\x02Fictional British man of mystery. \x0fYeah, bay-beee, yeah!',
'Australian Outback':'\x02Beware of dangerous temperatures, strange animals, and \x0fdidgeridoos.',
'Babe Ruth':'\x021895-1948, American baseball legend, \x0fand one heck of a candy bar!',
'Babies':'\x02Little bundles of joy \x0f... and who needs sleep, anyway?',
'Baby Showers':'Baby showers may bring flowers ...',
'Backstreet Boys':'\x02The latest American pop boy band. \x0fWhich one do you think is the cutest?',
'Bad Dogs':'Bad dog, bad dog. What\'cha gonna do?',
'Bagpipes':'\x02A shrill-toned musical instrument consisting of a leather bag and pipes. \x0fAlso available in plaid.',
'Baked Beans':'\x02Add a little bacon, brown sugar \x0fand Beano!',
'Baked Potatoes':'\x02Hot potato, couch potato, potato head, twice baked, half-baked, \x0f... whatever.',
'Baking Cookies':'\x02An experience only surpassed by eating them.\x0f',
'Bald Eagles':'\x02Known for their majestic appearance and powerful flight. In 1782, the bald eagle was chosen as the emblem of the United States.\x0f',
'Ballerinas':'\x02Beautiful, graceful dancers \x0fwho are always on their toes.',
'Bangkok':'\x02Capital of Thailand. Location: near the Gulf of Siam. Population: five million. \x0fReputation: seedy.',
'Bankruptcy':'It\'ll be the debt of you.',
'Barbara Walters':'\x021931- , American television journalist and author. Voted one of the most important women of the century by "Ladies Home Journal."\x0f',
'Barbed Wire':'\x02Wire with sharp points, used for fences. \x0fCreated havoc on the western frontier.',
'Barfing':'We didn\'t want to bring that up ...',
'Barney':'\x02Purple dinosaur. \x0f"I love you, you love me, blah, blah, blah ... "',
'Bart Simpson':'\x02Fictional animated character. \x0fDon\'t have a cow, man!"',
'Bates Motel':'\x02The haunt of Alfred Hitchcock\'s psycho, Norman Bates \x0f... and mother, of course ...',
'Batman':'\x02How does Batman\'s mother call him home? \x0f"Dinner, dinner, dinner, dinner, dinner, dinner, dinner, dinner - BATMAN!"',
'Bats':'\x02The little brown bat consumes as many as 600 mosquitoes in an hour. \x0fThe vampire bat dines elsewhere ...',
'Beach Parties':'Up for some "Beach Blanket Bingo," Annette?',
'Beanie Babies':'\x02Tiny plush collectibles to love and cherish. \x0fDon\'t take that tag off!',
'Beauty And The Beast':'\x02A tale as old as time \x0f... so Disney didn\'t have to pay royalties.',
'Beer':'\x02"Beer is proof that God loves us and wants us to be happy." \x0f- Benjamin Franklin',
'Beer Bellies':'Just think of them as microbreweries.',
'Beethoven':'\x021770-1827, German composer, considered one of the greatest of the western world.\x0f',
'Beets':'Beats Brussels sprout.',
'Being In Love':'\x02"Love\'s like the measles, all the worse when it comes late." \x0f-Douglas Jerrold',
'Bell-Bottoms':'\x02Bell-bottoms and pea coats \x0f-who would have thought the Navy could be such a trendsetter?',
'Ben Stiller':'\x021965-, American actor, director, and funny guy of Reality Bites, There\'s Something About Mary, and Meet The Parents\x0f',
'Berlin - 1945':'\x02Adolph Hitler\'s last stand. \x0fBunker ... I mean -hunker down, soldier.',
'Big Bang Theory':'\x02A cosmological theory for the origin of the universe. \x0fAn explosive idea!',
'Big Macs':'\x02T w o a l l b e e f p a t t i e s s p e c i a l s a u c e l e t t u c e c h e e s e p i c k l e s o n i o n s o n a s e s a m e s e e d b u n .\x0f',
'Bigfoot':'\x02Legendary North American monster, a.k.a. Sasquatch or the Abominable Snowman.\x0f',
'Bill Clinton':'\x021946- , popular, yet embattled, 42nd president of the United States.\x0f',
'Bill Gates':'\x021955-, chairman and chief software architect of Microsoft Corporation. \x0fA very rich guy.',
'Bill Murray':'\x021950-, American actor and comedian. Star of Ghostbusters, Stripes, Groundhog Day, and Lost In Translation.\x0f',
'Billboards':'Only 1,254 miles to Wall Drug ...',
'Bingo':'\x02"There was a farmer, had a dog, and Bingo was his name-o ..."\x0f',
'Bird Watching':'\x02A hobby that relies on a wing and a prayer.\x0f',
'Black Holes':'\x02The gravitational field of a black hole is so strong that nothing, including light, can escape from its vicinity.\x0f',
'Black Velvet':'\x02Smooth, silky and sophisticated \x0f... until you paint an Elvis on it.',
'Blizzard':'\x02Extreme cold, strong winds, and a head snowfall. \x0fAlso known as Canada.',
'Blood':'\x02A healthy human body contains between five and six quarts of blood. \x0fBloody right they do!',
'Board Games':'\x02Games have been played for thousands of years. \x0fSome games of Monopoly just SEEM that long.',
'Body Odor':'\x02Over $1.6 billion is spent each year on antiperspirants in the United States. \x0fThat stinks!',
'Body Piercing':'YOU STUCK WHAT? WHERE?',
'Body Surfing':'When you\'re too cheap to buy a surfboard.',
'Bonbons':'Sweets for the sweet ...',
'Bongos':'\x02Small drums played with the fingers. Used in Latin American and African music. The choice of American beat poets.\x0f',
'Bottled Water':'How much are you willing to pay for something you can get for free?',
'Boxing':'\x02An ancient and honorable sport \x0f- not just for boys anymore ...',
'Boy Scouts':'\x02International organization for boys and young men founded in England in 1908, to foster character, citizenship and outdoor life.\x0f',
'Boyfriends':'\x02"My boyfriend\'s back and you\'re gonna be in trouble." \x0f- The Angels',
'Brad Pitt':'\x021963- , American actor and heart-throb.\x0f',
'Brain Surgeons':'Hey, it ain\'t brain surgery ... oh ... wait a second ...',
'Brains':'\x02Vital to human existence \x0fand mad scientists.',
'Britney Spears':'\x021981-, American singer. \x0fFrom mouseketeer to international pop star.',
'Broadway':'\x02The New York theater district. "They say the neon lights shine bright on Broadway." \x0f-Barry Mann',
'Bruce Willis':'\x021955- , Diehard American action movie star who has moonlighted on TV. He also starred in Pulp Fiction, Armageddon and The Sixth Sense.\x0f',
'Bubble Gum':'\x02Crack it, snap it, pop it, and blow it!\x0f',
'Bubbles':'\x02"Tiny bubbles, in the wine/ Tiny bubble make me feel fine ..." \x0f-Don Ho',
'Bullwinkle':'\x02As in the cartoon "The Adventures of Rocky and Bullwinkle" \x0f- the moose half of moose and squirrel.',
'Bumper Stickers':'\x02Your personal billboard!\x0f',
'Bungee Jumping':'Another sport hanging on by a thread.',
'Buying A House':'If only we had the money, we could get a mortgage.',
'Cabbage':'\x02From the French word caboche, meaning "big head."\x0f',
'Cactus':'\x02Require little care and exhibit bizarre forms. \x0fAs such, they are often mistaken for Survivalists.',
'California':'\x02Sacramento is its capital, Los Angeles its largest city. \x0fHere we come.',
'Camping Trip':'\x02When you just have to get s\'more nature.\x0f',
'Canada':'\x02Federated country of North America. \x0fThe Great White North - eh?',
'Canadians':'How many Canadians does it take to screw in a lightbulb? Fifteen. Fourteen to chip it out of the ice, and one to screw it in.',
'Captain Kirk':'\x02Fictional starship captain. "Beam me up Scotty, there is no intelligent life on this planet!" \x0f- bumper sticker, 1980s',
'Car Bombs':'Not including the Ford Pinto, of course.',
'Car Horns':'Blow it, buddy!',
'Carl Sagan':'\x021934-96, American astronomer and pioneer exobiologist. Touched many lives. \x0fBillions and billions of them.',
'Carnival Workers':'Step right up ...',
'Cary Grant':'\x021904-86, British-born American actor known for his debonair manner. He can be found \x0fNorth by Northwest.',
'Casablanca':'\x02The largest city in Morocco, and one heck of a good movie. \x0f"Of all the gin joints in all the towns in all the world..."',
'Casinos':'Slots and slots of fun.',
'Castles':'\x02Kings, queens, knights in shining armor, \x0fand little square hamburgers.',
'Caves':'\x02Stalactites, stalagmites. \x0fWhich go up and which go down?',
'Celine Dion':'\x021968-, Canadian singer \x0fwhose heart will go on, and on ...',
'Cell Phones':'Get off the phone or get off the road!',
'Cesar Chavez':'\x021927-93, American labor leader who led the 1965 nationwide boycott of California grapes \x0f... a bunch of sour grapes!',
'Chain Letters':'\x02Send this game to ten of your friends and good luck will follow. \x0fHonest!',
'Chains':'Gold or iron: name your shackles.',
'Challenger Explosion':'\x02"Without a wish, without a will/ I stood upon that silent hill/ and stared into the sky ..." \x0f- Ralph Hodgeson',
'Chameleons':'\x02The chameleon is a lizard that changes color when frightened \x0f-or is that a politician?',
'Charging Rhinos':'How do you stop a rhino from charging? Take away its credit cards.',
'Cheesecake':'A really tasty dish.',
'Cher':'\x021946- , American singer and actor, \x0fshe makes aging look good.',
'Chicago':'\x02Third largest city in the United States. \x0fOur kind of town.',
'Chicken Pox':'\x02Infectious disease usually contracted in childhood. \x0fJust don\'t scratch \'em!',
'Chickens':'\x02From incubator to rotisserie in 56 days! \x0fRun, chicken, run!',
'Chimpanzees':'Sure, they\'re related to us; but they don\'t write, and they NEVER call!',
'China':'\x02The most populous country in the world. More than one-fifth of the world\'s total population lives within its borders.\x0f',
'Chinatown':'\x02International travel, \x0fjust around the corner.',
'Choir Boys':'\x02They \x0fsound \x02angelic, \x0fbut ...',
'Chorus Girls':'Long legs and high kicks!',
'Cigarette Burns':'\x02Another reason to give up smoking.\x0f',
'Cigarettes':'Mind if I smoke?',
'Cinco de Mayo':'\x02Marks the victory of the Mexican Army over the French at the Battle of Puebla, in 1862.\x0f',
'Cindy Crawford':'\x021966- , American Supermodel. \x0fWhat dreams are made of.',
'Clark Gable':'\x021901-60, American film actor, noted as a romantic lead. \x0fFrankly, my dear, he didn\'t give a damn.',
'Claude Monet':'\x021840-1926, French painter, regarded as one of the leaders on the impressionist movement.\x0f',
'Cleaning The Bathroom':'It\'s YOUR turn!',
'Cleopatra':'\x02c. 69-30 BC, Queen of Egypt, noted for love affairs with Julius Caesar and Mark Antony, \x0fwhich came back to bite her in the asp.',
'Clint Eastwood':'\x021930-, American film actor and director, past mayor of Carmel, California. \x0fHas earned fistfuls of dollars.',
'Clowns':'\x02They would be \x0freally funny \x02if they weren\'t so darn scary.',
'Cocaine':'\x02Alkaloid obtained from leaves of the coca plant and used as a local anesthetic and abused as a drug.\x0f',
'Cockroaches':'\x02Annoying insects that can survive a nuclear war. \x0fFortunately, they can\'t survive the heel of your shoe.',
'Coconuts':'\x02"Put the lime in the coconut, and drank them both up." \x0f-Harry Nillson',
'Cold Pizza':'The breakfast of champions.',
'Communists':'\x02"From each, according to their ability, to each according to their need." \x0fI need a new Ferrari.',
'Commuting':'\x02The daily grind. \x0fAnd we\'re not talking coffee.',
'Computer Hackers':'\x02We didn\'t mean to shut down the entire government ...\x0f',
'Computers':'\x02British mathematician Charles Babbage worked out the principles of the modern digital computer in the late 1800s.\x0f',
'Confucius':'\x02c. 551-479 BC, K\'ung Fu-Tzu, Chinese philosopher and one of the most influential figures in Chinese history.\x0f',
'Conspiracy Theories':'Oh, that was just a coincidence!',
'Construction Workers':'Hard hats -hard bodies.',
'Corn On The Cob':'\x02A grain native to the Americas, corn was a staple food for many centuries \x0fbefore corn holders were invented.',
'Corvettes':'\x02In 1953, Chevrolet introduced the Corverre, the first mass-produced sports car with a fiberglass body. \x0fThe perfect cure for a midlife crisis.',
'Count Dracula':'"I vant to suck your blood!"',
'Country Music':'\x02Encompassing styles such as western swing, honky-tonk, bluegrass and rockabilly. \x0fShould mention a pickup truck and a dog named "Bo."',
'Cow-Pies':'\x02When dried, these "cow chips" are hurled discus-like over great distances. \x0fIt\'s true.',
'Crazy Horse':'\x021849?-77, chief of the Oglala Sioux. A leader in the Native American resistance to the westward expansion on the United States.\x0f',
'Creamed Corn':'Eat it, it\'s good for you.',
'Crystal Balls':'\x02I see a Green Apple card in your future.\x0f',
'Cuba':'\x02Island republic in the Caribbean, just south of Florida. \x0fBeans and rice never tasted so good.',
'Cults':'\x02They \x0fseemed \x02nice ...\x0f',
'Custer\'s Last Stand':'\x021866, Little Big Horn. \x0fVery big mistake.',
'Dandruff':'\x02Dry skin on your scalp? \x0fSounds a bit flaky.',
'Danielle Steel':'\x021947- , Prolific romance novelist. \x0f"Suddenly, Stephanie spotted Lance on the beach ..."',
'Danny DeVito':'\x021944- , American television, motion-picture actor, and director. Star of Taxi, Romancing The Stone, Twins, and Get Shorty.\x0f',
'Dark Alleys':'Don\'t go there!',
'Darth Vader':'\x02"Luke \x0f... (wheeze) .. \x02I am \x0f... (wheeze) ... \x02your father \x0f... and you don\'t write, you don\'t call ... NOTHING."',
'Dating':'First stage of the human mating ritual.',
'David Letterman':'\x021947- , American television entertainer and talk-show host. And ... the Number One reason to watch him (drum roll, please): \x0fTOP TEN LISTS!',
'Daytime TV':'\x02Soap operas, game shows, talk shows and reruns ... \x0fis this a great country or what?',
'Death Valley':'\x02Arid, desolate and hellish region of California. Named by a survivor of an attempted 1849 crossing.\x0f',
'Deer Hunting':'Nooo! Nooooo! Not BAMBI\'S MOTHER!',
'Demi Moore':'\x021962-, American actor in St. Elmo\'s Fire, Ghost and GI Jane.\x0f',
'Democrats':'\x02Their symbol is the donkey, or ass. \x0fInsert your own joke here.',
'Denzel Washington':'\x021954- , American actor known for his powerful roles in such movies as Cry Freedom, Malcolm X, and Mississippi Masala.\x0f',
'Detroit':'\x02The Motor City is the world\'s foremost automobile manufacturing center, and the tenth largest city in the U.S.\x0f',
'Diamonds':'\x02The hard fact: they are just highly refractive crystalline allotropes.\x0f',
'Discos':'Where you go to catch "Saturday Night Fever."',
'Discovering America':'1492, Christopher Columbus discovered that America was discovered centuries before he arrived.',
'Disneyland':'You\'ve just won the "Apples to Apples(R) Grand Masters Tournament." Where\'re you gonna go?',
'Divorce':'It\'s a trial separation that goes to trial.',
'Doctors':'\x02Over twenty years of education and \x0fthey\'re still "practicing" medicine?',
'Doing The Dishes':'You wash, I\'ll watch.',
'Dolly Parton':'\x021967- , American singer, songwriter, and actor. Known as much for her personal style as for her successful career.\x0f',
'Dr. Kevorkin':'\x021928- , Controversial advocate of doctor-assisted suicide.\x0f',
'Dr. Seuss':'\x021904-1991, Theodor Suess Geisel, \x0fthe cat who came up with "The Cat in the Hat."',
'Driving Off A Cliff':'It was either that or hire someone to do my takes.',
'Duct Tape':'All-purpose, ... all the time ...',
'E-Mail':'You\'ve got JUNK mail!',
'Ear Wax':'\x02A waxy, yellowish substance that protects the ear from dust, bacteria, \x0fand from hearing things you don\'t want to hear.',
'Earthquakes':'\x02The Richter scale is named after the American seismologist Charles Richter. \x0fDid the earth move for you?',
'Earwigs':'\x02Nocturnal insects with abdominal pincers. \x0fNothing to do with ears or wigs.',
'East Coast':'\x02From New England to Florida. \x0fThey\'re not like folks \'round here ...',
'Eddie Murphy':'\x021961-, American comedian, actor, and producer. Best known for his work in 48 Hours, Beverly Hills Cop and on Saturday Night Live.\x0f',
'Eleanor Roosevelt':'\x021884-1962, first lady, social activist, author, lecturer, and U.S. representative to the United Nations.\x0f',
'Electric Eels':'\x02Slippery and slimy snakelike fishes that emit electrical charges. \x0fThe shocking truth!',
'Electricity':'\x02The repulsive or attractive force between two stationary bodies. \x0fNo problem unless one of those bodies is yours.',
'Elephants':'\x02The largest living land mammal, with two species: Indian and African. \x0fNot counting Dumbo, there are no American elephants.',
'Elizabeth Taylor':'\x021932- , American actor, noted for her lush beauty, emotional performances and multiple husbands.\x0f',
'Elvis Presley':'\x021935-77, American singer and actor and the king of rock-and-roll. \x0fHis death left the music world all shook up.',
'Emily Dickinson':'\x021830-86, American poet, whose lyrics are psychologically astute treatments of love, death, and immortality. \x0fSo there.',
'Ernest Hemingway':'\x021899-1961, American novelist and short-story writer, whose macho style is crisp, laconic and understated.\x0f',
'Europe':'\x02The Old Country \x0f... except to people who live there.',
'Exorcism':'\x02To ceremoniously expel an evil spirit.\x0f',
'Eyes':'\x02Light-sensitive organ of vision in animals. \x0fSee?',
'Falling Down':'\x02"What we call failure is not the falling down, but the staying down." \x0f-Mary Pickford',
'Family Reunions':'\x02Just to remind you why you moved away in the first place ...\x0f',
'Family Vacations':'Dad? Dad? Are we there yet? Are we there yet? Are we? Huh? Dad?',
'Family Values':'Often said but seldom understood.',
'Fast Food':'You want fries with that?',
'Feathers':'\x02Which weighs more, a pound of feathers or a pound of rocks?\x0f',
'Feminists':'\x02Political and social activists who support selected women\'s causes.\x0f',
'Festering Wounds':'Quit picking at that!',
'Fidel Castro':'\x021927-, Cuban revolutionary and Communist dictator since 1976. He earned a PhD in law in 1950.\x0f',
'Firefighters':'\x02Emperor Augustus instituted a corps of fire-fighting "watchmen" in 24 B.C. \x0fNero, on the other hand, fiddled while Rome burned.',
'Firestorms':'\x02Some severe wildfires require more than 10,000 firefighters. \x0fAnd, wouldn\'t ya know it, some idiot parked in front of the hydrant!',
'Fireworks':'\x02Includes firecrackers, Roman candles, and bottle rockets. \x0fIt\'s all fun until someone loses an eye ... and a nose ... and an arm ...',
'First Man On The Moon':'\x02July 20, 1969. "That\'s one small step for a man, one giant leap for mankind." \x0f-Neil A. Armstrong',
'Flipper':'\x02American television dolphin of the 1960\'s \x0f... like Lassie, only wetter.',
'Fly Fishing':'... if you can"t catch flies any OTHER way ...',
'Flying Monkeys':'\x02The reason why "The Wizard Of Oz" still gives us nightmares.\x0f',
'Forest Fires':'\x02"Only YOU can prevent forest fires." \x0fThe heat is on!',
'Fort Knox':'\x02American military post in Kentucky, containing the greater part of the gold reserve of the U.S. government.\x0f',
'Fourth Of July':'\x02"Independence Day" in the United States. \x0f"Thank Goodness We Got Rid of Them Day" in Britain.',
'Frank Lloyd Wright':'\x021867-1959, pioneering American architect. Considered one of the greatest designers of the 20th century.\x0f',
'Frank Sinatra':'\x021915-98, the greatest American pop singer of his generation, award winning film and television actor. \x0fDo-be do-be do, baby.',
'Freckles':'No matter what they tell you, freckles won\'t grow together to form a great-looking tan.',
'Freedom':'Express yourself!',
'French Wines':'The perfect complement to an overpriced meal.',
'Fresh Water Pearls':'String them along ...',
'Friction':'\x02Resistance to the motion of a body in contact with another body \x0f... any body will do.',
'Fund Raising':'\x02Hello ... my name is Jonathan, would you like to buy some fruit, magazines, candy bars, wreaths, pizzas ... ?\x0f',
'Funerals':'\x02"He who dies with the most toys is, nonetheless, still dead." \x0f- Anonymous',
'Fur':'\x02The characteristic covering of mammals \x0fand people with money.',
'Fuzz':'Lint ... Policemen ... Whatever ...',
'Gall Bladder':'\x02Where excess bile is stored. \x0fStored for what, we don\'t know.',
'Gang Members':'\x02"When you\'re a Jet, you\'re a Jet all the way..." \x0f-West Side Story',
'Garrison Keillor':'\x021942- , American author and radio star. He shares the Midwest perspective with 2.6 million listeners each week on A Prairie Home Companion.\x0f',
'Garth Brooks':'\x021962- , American country music singer and songwriter. \x0fHe\'s got friends in low places.',
'Geishas':'\x02Japanese women training in traditional singing, dancing, and entertaining. \x0fOf course, you would never recognize them without all that make-up.',
'Gen. George S. Patton':'\x021885-1945, the commander of the American Third Army during World War II. \x0f-a.k.a. Olf Blood and Guts',
'Genetic Engineering':'What DO you get when you cross a monkey with a potato?',
'George W. Bush':'\x021946- , 43rd president of the United States. The second time ever that the son of a former president was elected to the office.\x0f',
'George Washington':'\x021732-99, First President of the United States. \x0fHe chopped down a cherry tree to make false teeth, or something like that ...',
'Georgia O\'Keeffe':'\x021887-1986, American abstract painter known for her still life compositions. \x0fHer skull paintings prove that beauty is more than skin deep.',
'Getting A Hug':'Hmmmm ... nice.',
'Ghost Towns':'\x02Population unknown.\x0f',
'Ghosts':'\x02Nonmaterial embodiments or the essence of organisms (mostly human beings). \x0fQuite spirited',
'Giant Squid':'\x02Going fishing for giant squid? \x0fNautilus I have to ...',
'Gila Monsters':'\x02The largest, and only poisonous lizard found in the United States.\x0f',
'Gingko Trees':'\x02An Asiatic tree, Gingko biloba, known for its fan shaped leaves. \x0fWe can\'t remember what it\'s good for.',
'Ginseng':'\x02Common name for plants of the ginseng family, source of a stimulant and a supposed aphrodisiac.\x0f',
'Girl Scouts':'I\'ll take six boxes of Thin Mints and three of the ... you know, the kind with the peanut butter.',
'Girlfriends':'Girlfriend - let\'s talk!',
'Giving A Hug':'\x02"One may give without loving; but none can love without giving." \x0f-Anonymous',
'Glaciers':'It\'ll be a cold day when we see THEM again ...',
'Glazed Donuts':'If you\'re going to be late, take a box of donuts.',
'Global Warming':'Is it hot in here, or is it just me?',
'Going To Church':'\x02Weddings, funerals, bazaars, and bingo!\x0f',
'Going To Grandma\'s':'\x02"Grandmother, what big teeth you have!" \x0f-Little Red Riding Hood',
'Going To School':'Secondary education? It\'s elementary.',
'Going To The Dentist':'This won\'t hurt a bit ...',
'Going To The Gym':'No pain, no gain.',
'Gold Chains':'The more, the better.',
'Goldfish':'The pet, the carnival prize, or the snack cracker.',
'Golf-Ball-Sized Hail':'\x02... which is almost as impressive as hail-sized golf balls ...\x0f',
'Grace Kelly':'\x021929-82, Princess of Monaco and American film star of Dial M for Murder, Rear Window, and To Catch a Thief. Always chic, always elegant.\x0f',
'Graffiti':'Art in a can. We"re drawn to it.',
'Grass Skirts':'Hula loves you, baby?',
'Grave Robbers':'Famous for their bodies of work.',
'Gravity':'\x02In 1684, the law of gravitation was formulated by English physicist Sir Isaac Newton, \x0fwho recognized the gravity of the situation.',
'Greenpeace':'\x02International organization dedicated to preserving the Earth\'s natural resources, and its diverse plant and animal life.\x0f',
'Gym Teachers':'\x02"I am a \x0fPhysical Education Teacher\x02. Call me a \x0fgym teacher\x02 again and you can drop and give me ten!"',
'Hair Transplants':'Oh, it looks so natural ...',
'Hairballs':'Cough it up, kitty ...',
'Halloween':'\x02October 31, the eve of All Saints\' Day, celebrated with costumes, treats, and scary stuff. \x0fNot just for kids any more!',
'Hand Grenades':'\x02Close only counts in horseshoes and hand grenades!\x0f',
'Handcuffs':'"You have the right to remain silent..."',
'Handguns':'\x02Source of a never-ending controversy as to how to get them out of the hands of the bad guys and into the hands of the good guys.\x0f',
'Hangnails':'We\'ve fingered the cause of the pain.',
'Having A Baby':'\x02"Rock-a-bye baby, on the tree top ..." \x0fWho would put a kid on a tree top?',
'Having An Operation':'What a cutup! A real stitch.',
'Hawaii':'\x02The eight islands that make up America\'s 50th state entered the Union on August 21, 1959.\x0f',
'Helen Keller':'\x021880-1968, American author and lecturer who overcame deafness and blindness with the help of her companion, Anne Sullivan.\x0f',
'Hiccups':'\x02How do you, \x0fhic\x02, get em? How do you, \x0fhic\x02, get rid of "em?',
'High School Football':'The whole ten yards!',
'High School Reunions':'\x02See also: \x0f"root canal, as fun as ..."',
'Hillary Rodham Clinton':'\x021947- , New York Senator, lawyer, and former American First Lady.\x0f',
'Hiroshima - 1945':'\x02"I am become death, the destroyer of worlds" \x0f- J. Robert Oppenheimer, on the detonation of the first atmoic bomb.',
'HMOs':'\x02Heath Maintenance Organizations. \x0fHere\'s to your health ...',
'Hockey':'Did you hear about the big fight last night? All of a sudden, a hockey game broke out!',
'Hollywood':'\x02Motion picture and television industry center of the world. \x0fHooray for Hollywood!',
'Homeless Shelters':'\x02In the United States, nearly three-quarters of the help for the homeless comes from the private sector, mostly from church soup kitchens.\x0f',
'Homer Simpson':'\x02Fictional cartoon character created by Matt Groening. \x0fD\'oh!',
'Homework':'Something to do during comercials.',
'Hooligans':'"Hey! Kids! Get outta my yard!"',
'Horseback Riding':'WHOAAA!!!',
'Hot Lava':'There\'s no better way to serve it.',
'House Guests':'\x02How many visitors does it take to drive you crazy? \x0fGo on - take a guest!',
'Hummingbirds':'\x02Why do hummingbirds hum? \x0fBecause they don\'t know the words ... ... da-dum, dum!',
'Humphrey Bogart':'\x021899-1957, American film actor, starred in such classics as The Maltese Falcon and Casablanca. "Here\'s looking at you kid."\x0f',
'Icebergs':'\x02May reach 300 to 500 feet above the oceans\'s surface. \x0fAsk the captain of the Titanic about the 90 percent that\'s UNDER water.',
'In A Coma':'\x02A deep, prolonged state of unconsciousness \x0f... sometimes you just feel that way.',
'Incense':'Incense is better than no sense at all.',
'India':'\x02The world\'s seventh largest country by area, but the second most populous, with one billion people.\x0f',
'Indiana Jones':'\x02Fictional archeologist and action hero. \x0fProof that a good hat and a whip can take you a long way.',
'Industrial Revolution':'\x02The first Industrial Revolution occurred in Great Britain at the end of the 1700s. \x0fThe second came with the invention of the "Clapper."',
'Infomercials':'One of these days, one of them may even say something informative.',
'Inside The Sun':'\x02Consisting mostly of hydrogen, the temperature reaches almost 16,000,000 K (about 29,000,000 F).\x0f',
'Intellectuals':'They think they\'re so smart.',
'Ireland':'\x02Island of the British Isles, west of Great Britain. Known for its distinctive traditional dance and music.\x0f',
'Israel':'\x02Located on the Mediterranean, the state of Israel was reated by a 1948 U.N. mandate.\x0f',
'Italy':'\x02European Republic, shaped like a boot \x0f- a very fashionable boot.',
'Jack Nicholson':'\x021937- , American motion-picture actor of "Chinatown," "Terms Of Endearment" and "The Shining." \x0fHe\'s as good as it gets!',
'Jack The Ripper':'\x02Accused of murdering six women in 1888, and suspected in other murders. \x0fStill at large.',
'Jackie Chan':'\x021954-, actor, director, martial artist. Screen name, Sing Lung, means "Becoming the Dragon." \x0fThat\'s "MISTER Becoming the Dragon" to you!',
'Jacques Cousteau':'\x021910-97, French naval officer, marine explorer, and author. Best known as a documentary filmmaker.\x0f',
'Jamaica':'\x02Third largest island of the Greater Antilles, south of Cuba. Tropical climate, reggae music, and jerk cooking.\x0f',
'James Bond':'\x02Fictional British secret agent created by English author Ian Fleming. \x0fShaken, but never stirred.',
'James Dean':'\x021931-55, American actor of film, stage, and television. His role in Rebel Without a Cause helped define "cool."\x0f',
'Japan':'\x02An Asian constitutional monarchy. The capital city is Tokyo. \x0fLet\'s see ... sushi, Godzilla, earthquakes ...',
'Japanese':'How many Japanese does it take to screw in a light bulb? Who needs light bulbs when you\'ve got OUR new technology!',
'Jelly Beans':'Well, as long as we HAVE to eat our vegetables ...',
'Jennifer Lopez':'\x021970-, American singer and actor of Selena, Money Train, and Maid In Manhattan.\x0f',
'Jerry Springer':'\x021944- , controversial talk-show host. \x0fDon\'t those people know that millions of us are watching?',
'Jesse Jackson':'\x021941-, American civil rights leader. Named to "The Gallup List of Ten Most Respected by Americans" for ten years.\x0f',
'Jesse Ventura':'\x021951-, wrestler, Navy Seal, and former governor of Minnesota. Author of I Ain\'t Got Time To Bleed.\x0f',
'Jim Carrey':'\x021962- , Canadian comedian and actor. Famous for outrageous faces, \x0fand dumb and dumber characters.',
'Jimmy Stewart':'\x021908-97, America\'s favorite self-image. Mr. Smith Goes to Washington, Rear Window, Vertigo, and It\'s a Wonderful Life, ... and it probably was.\x0f',
'Joan Of Arc':'\x021412-31, patron saint of France who decisively turned the tide of the Hundred Years\' War, \x0fwhich really burned her up.',
'Jodie Foster':'\x021962- , American actor began her career on Mayberry, R.F.D. and went on to win Academy Awards for The Accused and Silence Of The Lambs.\x0f',
'John F. Kennedy':'\x021917-63, 35th president of the US. "Ask not what your country can do for you; ask what you can do for your country."\x0f',
'John Glenn':'\x021921- , The first U.S. astronaut to orbit the earth in 1962, and a U.S. Senator. \x0fNever too old to shoot for the moon!',
'John Philip Sousa':'\x021854-1932, American bandmaster and composer of Stars and Stripes Forever. Known as "The March King."\x0f',
'John Travolta':'\x021954-, American actor of "Welcome Back, Kotter," "Grease," "Saturday Night Fever" and "Pulp Fiction." \x0fThat man can dance!',
'Judge Judy':'\x02Ms. Sheindlin presides over real-life cases on this TV courtroom show. \x0f"I\'m the boss, applesauce!"',
'Julia Roberts':'\x021967-, American actor and Pretty Woman. Also starred in Steel Magnolias, My Best Friend\'s Wedding, and Erin Brockovich.\x0f',
'Junk Mail':'\x02Contests, credit card applications, solicitations and political ads.\x0f',
'Jupiter':'\x02Story Problem: \x0fIf one year on Jupiter equals 11.86 Earth years, and one day equals 9.92 Earth hours, how many Earth hours are there in a Jupiter year?',
'Katherine Hepburn':'\x021909-2003, American actor and winner of four Academy Awards. She starred in such classics as The African Queen.\x0f',
'Keanu Reeves':'\x021964- , American actor of Bill And Ted\'s Excellent Adventure, The Matrix and Speed. Keanu means "cool breeze over the mountains."\x0f',
'Killer Whales':'\x02Black and white predatory whales. \x0fBoy, can they sing!',
'Kilts':'If Mel Gibson can wear one, so can you.',
'King Arthur':'\x02Legendary British king best known for Camelot and round tables.\x0f',
'King Henry VIII':'\x021491-1547, King of England, and founder of the Church of England. \x0fSix wives, no waiting.',
'Knock-Knock Jokes':'Who\'s there?',
'Labor Unions':'\x02Look for the Union label. \x0fAnd, while you\'re at it, look for Jimmy Hoffa ...',
'Large Mouth Bass':'Oh, please, let it not sing ...',
'Las Vegas':'\x02The first casino opened in Las Vegas in 1946. \x0fLas Vegas ... or it that Lost Wages?"',
'Lawyers':'We\'d throw some joke in here, but we\'re afraid of getting sued.',
'Leaf Blowers':'Toro, Toro, Toro!',
'Leather':'\x02Animal hide. \x0fLeather you like it or not.',
'Leeches':'Any mention of lawyers, agents, or reporters would be FAR too easy ...',
'Lemons':'\x02When life gives you lemons, make lemonade ... or, in the case of a car, take it back. \x0fThere\'s a law, you know!',
'Lenin\'s Tomb':'We\'d love to visit Lenin\'s Tomb, but it\'s probably just another communist plot.',
'Leonardo Da Vinci':'\x021452-1519, Florentine artist, sculptor, architect, engineer, scientist, \x0fand all-around smartypants.',
'Lightning':'\x02Electrical discharge between rain clouds, or between a rain cloud and the earth, \x0for between a rain cloud and an idiot with a kite.',
'Loan Sharks':'As dangerous as "Jaws", but without the charisma.',
'Lobster':'\x02Crustaceans closely related to freshwater crayfishes. \x0fMarket price.',
'Local Police':'\x02They know who you are and they know where you live.\x0f',
'Log Cabins':'\x02Among the many Americans born in log cabins were Preisdents Harrison, Lincoln, and Grant. \x0fJust pass the maple syrup.',
'Lollipops':'Sucker!',
'London':'\x02Founded even before the Romans reached England\'s shores, now the capital of Great Britain.\x0f',
'Looking For A Job':'Will work for fool ...',
'Los Angeles':'LA LA Land.',
'Losing Your Job':'They just didn\'t understand me!',
'Lucille Ball':'\x021911-89, American actor and comedian. \x0fYou love Lucy? I love Lucy.',
'Machine Guns':'\x02Automatic, rapid-fire, repeating weapons. The Gatling gun was used as early as the American Civil War.\x0f',
'Mad Cow Disease':'\x02Degenerative brain disorder in cattle. \x0fThe reason they don\'t know enough to come in out of the rain?',
'Madame Curie':'\x021867-1934, French chemist and physicist who won a Nobel Prize for her work on radiation. \x0fFun fact: \x02A "curie" is a unit of radioactivity.',
'Madonna':'\x021958-, American singer, songwriter, actor, writer, and 1980s pop icon. \x0fBlond Ambition.',
'Magic Tricks':'\x02"Nothin\' up my sleeve ..." \x0f- Bullwinkle',
'Mahatma Gandhi':'\x021869-1948, Indian leader and philosopher who preached nonviolence. \x0fWas assassinated for his efforts.',
'Manhattan':'I\'ll take Manhattan!.',
'Mardi Gras':'\x02Fat Tuesday marks the final day before the Christian fast of Lent, a 40-day period of self-denial and abstinence. \x0fSO LET\'S PARTY!',
'Marilyn Monroe':'\x021926-62, American movie star, pinup and sex symbol. \x0fJust ask the Kennedys.',
'Mark Twain':'\x021835-1910, American writer and humorist, best known for the adventures of Tom Sawyer and Huckleberry Finn.\x0f',
'Marriage':'If love and marriage go together like a horse and carriage ... who\'s the horse?',
'Mars':'\x02The fourth planet from the sun. \x0fWhere men come from.',
'Martha Stewart':'\x021941-, television personality, magazine editor, and author. \x0fDomestic arts are her stock-in-trade.',
'Martin Luther King, Jr.':'\x021929-68, American civil rights leader and advocate of nonviolent resistance. \x0fWas assassinated for his efforts.',
'Meat Cleavers':'\x02No relation to Ward, June, or the Beaver ...\x0f',
'Meatloaf':'\x02Large and intimidating \x0f-the dish not the singer!',
'Meg Ryan':'\x021961- , American actor and girl-next-door star of When Harry Met Sally, Sleepless In Seattle, and You\'ve Got Mail.\x0f',
'Mel Gibson':'\x021956-, Australian actor. Known for The Road Warrior, Braveheart and Lethal Weapon I, II, III, IV ...\x0f',
'Men':'REAL Men.',
'Men In Black':'We\'re not here. You don\'t see us. The government did NOT send us.',
'Meryl Streep':'\x021959-, accomplished American actor, two-time Oscar winner, with over a dozen Academy Award nominations.\x0f',
'Mexico':'\x02Federal republic in North America. The capital and largest city is Mexico City.\x0f',
'Mice':'\x02"The best-laid schemes o\' mice an\' men ..." \x0f-Robert Burns',
'Michael Jackson':'\x021958- , American popular singer, dancer, and songwriter. \x0fWelcome to Neverland.',
'Michael Jordon':'\x021963- , American professional basketball legend, led Chicago to six world championships. \x0fNo bull.',
'Michelangelo':'\x021475-1564, inspired Italian sculptor, architect, painter, and poet. \x0fA REAL Renaissance man.',
'Michelle Pfeiffer':'\x021957-, American actor whose career began with Grease 2. \x0fShe\'d like us to forget that but remember her Oscar nominations.',
'Microsoft':'\x02A leading American software company. \x0fWe\'d say more but we don\'t want to monopolize your time ...',
'Midlife Crisis':'\x02"Here comes your 19th nervous breakdown ..." \x0f-The Rolling Stones',
'Mike Tyson':'\x021966- , American heavyweight boxer. \x0fLend him your ear ...',
'Miles Davis':'\x021926-91, innovative, influential, and respected American jazz trumpter player and band layer.\x0f',
'Milk':'Three glasses a day will give you ... the gratitude of the dairy industry.',
'Milk Duds':'\x02Chocolate and caramel candy balls. \x0fTooth extractions at no extra charge!',
'Mirrors':'And now, a moment for reflection.',
'Mold':'\x02Fuzzy growth produced on organic matter by several types of fungi. \x0fParticularly attracted to students\' refrigerators',
'Money':'\x02"The best things in life are free/ But you can give them to the birds and bees/ Just give me money ..." \x0f-Bradford and Gordy',
'Morticians':'Why do you hang around with THOSE stiffs ...?',
'Mosquitoes':'They suck.',
'Motorcycles':'The air in your hair and bugs in your teeth.',
'Mount Rushmore':'\x02Memorial carved into the side of the Black Hills in South Dakota. \x0fHeads above all other monuments.',
'MTV':'\x02"Video killed the radio star." \x0f-The Buggles',
'Mud':'Water. Dirt. You do the math.',
'Mudslides':'\x02Chocolate drink or natural disaster \x0f... both occur frequently in California.',
'Muhammad Ali':'\x021942- , American heavyweight boxing champion. "Floats like a butterfly, stings like a bee."\x0f',
'Musicals':'South Pacific, The King and I, The Sound of Music, A Chorus Line, Cats, Rent ...',
'My 16th Birthday':'Dad, can I have the keys to the car, please?',
'My Bank Account':'Speaking of theoretical mathematics and unreal numbers ...',
'My Bathroom':'\x02"The bathroom was drenched with their splashings" \x0f-Aldous Huxley',
'My Bedroom':'\x02"No one knows what goes on behind closed doors." \x0f-Charlie Rich',
'My Body':'\x02Mine is a temple. \x0fSpecifically, the Temple of Doom ...',
'My Boss':'... is an idiot. You know it; we know it.',
'My Dreams':'\x02"What dreams may come ..." -Shakespeare\'s \x0fHamlet',
'My Family':'They\'ll drive you nuts. As long as you do the same to them, it\'s all even.',
'My First Kiss':'Sparks were flying. Of course, that could have been the braces ...',
'My Friends':'With friends like these, who needs enemies?',
'My Future':'\x02"The future\'s so bright, I gotta wear shades ..." \x0f-Timbuk-3',
'My Hair':'Hair today, gone tomorrow ...',
'My High School Prom':'As if adolescence isn\'t awkward and painful enough ...',
'My Job':'Love it or leave it.',
'My Love Life':'\x02"All you need is love ..." \x0f-The Beatles',
'My Mind':'It\'s a terrible thing to waste.',
'My Neighborhood':'\x02"Please, won\'t you be my neighbor?" \x0f-Fred Rogers',
'My Past':'What\'s past is past ... unless you\'re a politician ...',
'My Personality':'\x02"I\'m good enough, smart enough and, gosh darn it, people like me." \x0f-Stewart Smalley played by Al Franken',
'My Refrigerator':'It\'s a science experiment!',
'Napoleon Bonaparte':'\x021769-1821, Emperor of France. Met his Waterloo at the Battle of Waterloo. \x0fThe name should have tipped him off ...',
'NASCAR':'\x02Stock car racing began after World War II, breaking records for speed \x0fand for the number of advertisements on a single jacket.',
'Neil Simon':'\x021927-, American producer, playwright, and screenwriter of The Odd Couple, Biloxi Blues, The Sunshine Boys, California Suite, and many more.\x0f',
'New Orleans':'\x02The Big Easy.\x0f',
'New Shoes':'\x02Make you feel like dancing ...\x0f',
'New York City':'\x02America\'s most populous city. \x0fSo good, they named it twice.',
'Niagara Falls':'\x02Niagara Falls was formed about 12,000 years ago, when glaciers retreated north, \x0fand honeymooners approached from the south.',
'Nicholas Cage':'\x021964- , American actor known for his edgy characters in Leaving Los Vegas, Raising Arizona, and Moonstruck.\x0f',
'Ninjas':'Teenage mutant turtles need not apply.',
'Nobel Peace Prize':'\x02Established by Alfred Nobel. Swedish industrialist and inventor of dynamite. \x0fLed to an explosion of peace efforts.',
'Noisy Neighbors':'WHAT? I CAN\'T HEAR YOU!',
'Norman Rockwell':'\x021894-1978, American painter, illustrator and all-around interpreter of small town American life.\x0f',
'Nuclear Power Plants':'\x02"You\'ve turned a potential Chernobyl into a mere Three Mile Island." \x0f-Montgomery Burns, "The Simpsons"',
'NYPD':'\x02The New York Police Department. \x0fThey\'re so good, they have their own TV show.',
'Oil Spills':'\x02The American oil tanker, Exxon Valdez, went aground in Prince William Sound, Alaska, Mar. 24, 1989. \x0fSlick Move.',
'Olive Oil':'\x02Derived from fresh ripe fruit, which contain about 20% oil. \x0fBetter than "olive" the other oils.',
'On-Line Shopping':'\x02Enter your credit card number now. This is a secure site \x0f... Sure it is ...',
'Oprah Winfrey':'\x021954- , Television talk show host, actor and all-around American success story.\x0f',
'Oral Surgery':'You said a mouthful.',
'Oranges':'Face it ... nothing rhymes with orange.',
'Oxygen':'\x02Oxygen was discovered in 1774. \x0fYou\'d think someone would have noticed it earlier.',
'Pablo Picasso':'\x021881-1973, Spanish painter and sculptor, one of the greatest artists of the 20th century. \x0fIf only he could draw eyes ...',
'Parenting':'The process of discovering you are becoming just like YOUR parents.',
'Paris, France':'\x02The governmental, cultural and gastronomic capital of France. Or the world. \x0fJust ask the French.',
'Paying Bills':'Also known as "Debt Restructuring."',
'Paying Taxes':'Death or Taxes? Do we have to choose right away?',
'Penguins':'\x02Flightless, aquatic birds that reside in the Southern Hemisphere. \x0fAll dressed up and no place to go.',
'Picking Your Nose':'Noses run in our family.',
'Pigeons':'\x02Birds with small heads, short necks, stout bodies, \x0fand an incredible attraction to statues.',
'Pigs':'\x02Domesticated mammal of the swine family. \x0fThaaa ... thaaa ... that\'s all, folks!',
'Piranha':'\x02Carnivorous fish found in rivers of South America. \x0fWhen you feel like a bite ...',
'Pirates':'\x02"Yo, ho, yo, ho, a pirate\'s life for me ..." \x0f- Pirates of the Caribbean',
'Pit Bulls':'\x02Any of several crossbreeds of bulldogs with terriers. \x0fOr, several radio hosts we could mention.',
'Plane Crashes':'\x02Statistically safer than driving \x0f... unless you crash.',
'Plastic':'\x02Giant molecules of organic polymeric materials. \x0fBags and bags of the stuff.',
'Playing Chess':'\x02Has tantalized many of the world\'s greatest minds for almost 14 centuries. \x0fIt just confuses the rest of us.',
'Poison Ivy':'Itching for a walk in the woods?',
'Pokemon':'\x02Cute cartoon monsters you gotta catch. \x0fWhat you do with them is up to you ...',
'Pond Scum':'\x02Simple organisms that carry out photosynthesis \x0f... or spammers.',
'Poodles':'The only breed that is better groomed than their owners.',
'Popcorn':'Air poppers are for air heads ... I say bring on the butter!',
'Porsche Boxster':'\x02A two-seat, six cylander roadster- elegant design and superior drivability.\x0f',
'Postal Workers':'\x02"Neither snow, nor rain, nor heat, nor gloom of night, stays these couriers from the swift completion of their appointed rounds."\x0f',
'Power Tools':'"More power! More power! Argh! Argh!" -Tim, the Tool Man, Taylor, "Home Improvement"',
'Prince Charming':'\x02The perfect man \x0f... mythical, of course.',
'Princess Di':'\x021962-97, beloved English Princess who died in an auto crash. "Good-bye England\'s Rose ..." \x0f-Elton John',
'Pro Wrestling':'They\'re just faking it. But then, so are we.',
'Psychiatrists':'\x02"And how do you \x0ffeel\x02 about that?"\x0f',
'Psychics':'\x02The Psychic Friends Network went bankrupt in 1997. \x0fPerhaps they should have seen it coming ...',
'Public Radio':'"Good morning . . . . . This morning . . . . . . . . . . . .we have Wolfgang . . . Amadeus Mozart . . . for your listening pleasure . . ."',
'Puff Daddy':'\x021971- , American rap artist. "I\'ll be Missing You" shot him to stardom; \x0fno pun intended.',
'Pulling Weeds':'It\'s either this or chemical warfare.',
'Pumping Iron':'When a great weight needs to be lifted.',
'Pushups':'Exercises, a type of bra, or the ice cream treat.',
'Pyramids':'\x02Built by ancient civilizations, found mainly in Egypt, Guatemala, Honduras, Mexico and Peru. \x0fProbably the result of some pyramid scheme.',
'Quentin Terantino':'\x021963- , Groundbreaking American director and actor. \x0fNice movies, but not nearly enough blood.',
'Quicksand':'Just don\'t let it get you down.',
'Ragweed':'\x02A weed of the genus Ambrosia. \x0fNothing to sneeze at.',
'Rain':'\x02"When the rain comes, they run and hide their heads; they might as well be dead." \0f-The Beatles',
'Rainbows':'\x02"Someday they\'ll find it/ The Rainbow Connection/ The lovers, the dreamers and me ..." \x0f-Kermit the Frog',
'Rappers':'\x02PARENTAL ADVISORY EXPLICIT CONTENT \x0fHasn\'t seemed to hurt sales...',
'Reading A Good Book':'\x02So many books, so little time.\x0f',
'Recreational Vehicles':'If they\'re trying to get away from it all, why are they taking it all with them?',
'Recycling':'\x02More than one million tons of aluminum are NOT recycled each year. \x0fWhere do you throw your cans?',
'Red Raspberries':'Worth a few scratches.',
'Rednecks':'"You might be a redneck if ..." -Jeff Foxworthy',
'Redwood Forests':'\x02"From the Redwood Forests to the Gulf Stream Waters/ This land was made for you and me." \x0f-Woody Guthrie',
'Reggae Music':'\x02This contemporary Caribbean music, originating in Jamaica, remains an influential style of popular music. \x0fYa mon!',
'Regis Philbin':'\x021934- , American talk and game show host. \x0fWho wants to be a millionaire? Regis, apparently.',
'Remote Controls':'The world\'s handiest invention. That is, if you can find it.',
'Republicans':'\x02A U.S. political party symbolized by an elephant \x0f... and don\'t forget it!',
'Richard Nixon':'\x021913-94, 37th President of the United States and the only president to have resigned from office. \x0fAt least that\'s what the tapes say ...',
'Robert DeNiro':'\x021943- , Pre-eminent American actor who earned Academy Awards for The Godfather II and Raging Bull. \x0f"Are you looking at me?"',
'Road Kill':'Mmmmmm. Them\'s good eatin\'.',
'Road Trips':'\x02"Get Your Kicks on Route 66." \x0f-Nelson Riddle',
'Robin Williams':'\x021952- , versatile American comedian and actor. \x0fThe furriest man in show business.',
'Rock And Roll':'\x02It\'s here to stay!\x0f',
'Rock Concert':'If it\'s too loud - you\'re too old.',
'Rocket Scientists':'\x02Hey! They\'re not rocket scie \x0f... oh ... never mind.',
'Rocky Mountains':'\x02These extend 2,000 miles from northeastern British Columbia to central New Mexico, \x0fand keep the Californians away from everyone else ...',
'Rolling The Car':'You\'ll flip for this one ...',
'Roman Numerals':'There\'s a I in VII chance you\'ll know them.',
'Romeo And Juliet':'\x02William Shakespeare\'s best known play, written in 1595. \x0fYouthful love and hasty temperaments.',
'Root Beer Floats':'Actually, it\'s the ice cream that floats!',
'Rosa Parks':'\x021913-, civil rights icon arrested in 1956 for violating U.S. segregation laws by refusing to give up her bus seat to a white passenger.\x0f',
'Rosie O\'Donnell':'\x021962-, American actor and comedian. \x0fShe\'s in a league of her own!',
'Rubber Gloves':'Just in case ...',
'Running A Marathon':'\x0226 miles, 385 yards: the distance run by a Greek soldier from the town of Marathon to Athens in 490 BC.\x0f',
'Rush Limbaugh':'\x021951- , conservative talk-radio personality. Claims to host his radio show with half his brain tied behind his back, just to make it fair.\x0f',
'Russia':'\x02The world\'s largest country, spanning 11 time zones. Famous for borscht, ballet, chess and vodka \x0f-just don\'t mix them.',
'Rust':'\x02"Rust never sleeps." \x0f-Neil Young',
'Saddam Hussein':'\x021937-, dictator of Iraq 1979-2003.\x0f',
'Sailors':'\x02"In the Navy, you can sail the seven seas ..." \x0f-The Village People',
'Salads':'Lettuce not knock the vegetarians.',
'Salsa Dancing':'\x02Popular form of Latin American dance. A little jazz, a little blues, a touch of rock \x0fand lots of heat.',
'Salvador Dali':'\x021904-89, Spansih artist best known for his dream imagery and surrealism, including the limp watches in The Persistence Of Memory.\x0f',
'Samuel L. Jackson':'\x021948-, powerful American actor of Pulp Fiction, Jackie Brown, and The Negotiator.\x0f',
'Saturday Cartoons':'\x02Get your blanket, a bowl of cereal and snuggle in for three hours of commercials.\x0f',
'San Francisco':'\x02California\'s City by the Bay. \x0fWhere many hearts are left.',
'Saturn':'\x02Sixth planet from the sun, and the second largest in the solar system. \x0fHas a nice ring to it, don\'t you think?',
'Scavenger Hunt':'OK kids, here\'s your list: a marshmallow, a safety pin, a red rubber band, and a moon rock. Go find \'em!',
'Scene Of The Crime':'It was Colonel Mustard, in the library, with the candlestick.',
'Schindler\'s List':'\x021993 Steven Spielberg film. Powerful real-life story of a Catholic businessman who eventually saved over 1000 Jews in Nazi Poland.\x0f',
'Science Fair Projects':'\x02No human subjects, please!\x0f',
'Science Fiction':'In a galaxy far, far away ...',
'Screeching':'\x02Please stop.\x0f',
'Sean Connery':'\x021930- , Accomplished Scottish actor, although best known as the REAL Bond, \x0fJAMES Bond ...',
'Shania Twain':'\x021965- , Canadian country singer and songwriter. "Shania" means "I\'m on my way" in Ojibwa.\x0f',
'Sharks':'\x02Many species living today are similar to those from 100 million years ago. \x0fBecause change is scary.',
'Shopping Mall':'\x02Three-quarters of the North American population visit a shopping mall at least once a month.\x0f',
'Silk':'\x02Produced as a cocoon covering by the silk worm, and used in fine fabrics and textiles.\x0f',
'Silly Putty':'It\'s putty in your hands!',
'Skateboarding':'It\'s just going downhill ... down stairs ... down ramps ...',
'Skiing':'\x02The Super Giant Slalom: \x0fSwiss for "suicide."',
'Skinheads':'\x02Shaved heads, big boots. \x0fSome are Nazis, some are not.',
'Skunks':'\x02Black and white striped mammals known for their offensive smelling defensive spray.\x0f',
'Skydiving':'\x02Parachute canopies are usually made from nylon fabric that lasts for thousands of jumps \x0f- whether the skydiver does or not.',
'Sleeping Pills':'\x02I remember taking them \x0f... I just ... don\'t rememmer ... how mamy.',
'Slivers':'\x02Also known as splinters. The worst ones are under your fingernails.\x0f',
'Sloppy Joes':'\x02My favorite recipe \x0f-open the can.',
'Smithsonian Institution':'\x02Located in Washington, D.C., the largest museum complex in the world. \x0fWouldn\'t that be a great garage sale?',
'Snakes':'\x02Surprising, snakes move rapidly without legs. \x0fAlso surprising, they find OTHER snakes attractive.',
'Snow':'\x02Transparent ice crystals which form around dust and other small particles. \x0fGet my drift?',
'Social Security':'\x02American program designed to provide income and services in the event of retirement, sickness, disability, death or unemployment.\x0f',
'Socks':'\x02"Black socks, they never get dirty, the longer you wear them the stronger they get." \x0f-Bill Harley',
'South Africa':'\x02Two oceans, rugged mountains, traditional villages, game sanctuaries, wineries... \x0fforget the past and bring on the tourists.',
'South Park':'\x02Highly-rated, highly offensive animated cartoon series. \x0f"Oh my God! We killed Kenny!"',
'Soy Sauce':'\x02A brewed seasoning made from soybeans, wheat, and salt.\x0f',
'Spam':'Mystery meat, or mystery E-mails ...',
'Speeding Tickets':'\x02"No, officer, I don\'t have any idea how fast I was going."\x0f',
'Spiders':'\x02There are more than 34,000 species of spiders. \x0fTry not to think about THAT right before bedtime.',
'Spike Lee':'\x021957-, American film maker and Knicks fan. Best known for Do the Right Thing, Malcolm X, and 4 Little Girls.\x0f',
'Spilled Milk':'\x02Got milk? WHOOPS! Apparently not ...\x0f',
'Spit':'Ladies and gentlemen, straight from the Salivary Glands ...',
'Spontaneous Combustion':'\x02The ignition of substances without application of an external heat source. \x0fA good plot for "The X-Files."',
'Sport Utility Vehicles':'Need new tires?',
'Sports Channels':'Any team, any time.',
'Star Fruit':'Looks like plastic, tastes like lemons.',
'Starry Night':'\x02A sky bright with stars, a classic Van Gogh painting, and a Don McLean song. \x0fThree cards in one!',
'State Fair':'Aw, gee whiz, a blue ribbon for Bessie!',
'Steak And Potatoes':'\x02Hot off the grill!\x0f',
'Stephen King':'\x021947- , American author of horror novels, who\'s sold more than 100 million copies of his books. \x0fTalk about frightening ...',
'Steve Martin':'\x021945- , American comedian, actor, writer, and \x0f"wild and crazy guy."',
'Steven Spielberg':'\x021947-, American movie director and producer, and overachiever. From E.T. to Schindler\'s List... too many to list.\x0f',
'Stonehenge':'\x02Prehistoric stone monument located north of Salisbury, England.\x0f',
'Strawberry Shortcake':'Summertime and the eating is easy ...',
'Stubbed Toes':'\x02It\'ll feel better when it quits hurting.\x0f',
'Stunt People':'When you need someone to take the fall.',
'Summer Camp':'If the bugs don\'t get you, the poison ivy will!',
'Sunday Drivers':'Now available ANY day of the week!',
'Superman':'\x02Fictional comic book superhero loved by Lois Lane and Jerry Seinfeld.\x0f',
'Supermodels':'Long legs = big bucks.',
'Surfing The Net':'www.otb-games.com',
'Sushi':'Who would ever have guessed that raw fish could be so fashionable?',
'Swiss Bank Accounts':'Do you think everyone in Switzerland has one?',
'Swiss Chocolate':'\x02"What use are cartridges in battle? I always carry chocolate instead." \x0f-George Bernard Shaw',
'Swiss Cheese':'Guess it comes from holey cows ...',
'Taking A Bath':'\x02Bathing facilities have been found in excavations in India from before 2000 BC. \x0fSoap-on-a-Rope hasn\'t.',
'Talk Radio':'Talk about air pollution.',
'Teachers':'\x02If you can play this game, thank a teacher.\x0f',
'Telemarketers':'\x02"No, thank you ... No, I\'m not interested ... No, I have to go now ..."\x0f',
'Televangelists':'Not to be confused with Teletubbies.',
'Television':'One-hundred and sixty-four channels, and nothing worth watching.',
'Telling The Truth':'\x02"There are two kinds of truth. There are real truths and there are made-up truths." \x0f-Marion Barry, ex-mayor of Washington, D.C.',
'Terrorist Attack':'\x02We will never negotiate with terrorists.\x0f',
'Thanksgiving Day':'\x02The fourth Thursday of November in the U.S.; the second Monday in October in Canada.\x0f',
'The 1920s':'Pros: the Jazz Age. Cons: Presidents who look like librarians.',
'The 1950s':'Pros: Barbies, barbecues, and bikinis. Cons: McCarthy, the Korean War, television.',
'The 1960s':'Pros: the Moon Lsnding, the music. Cons: hippies who refuse to believe they\'re over.',
'The 1970s':'Pros ... uh ... pros ... uh ... GIVE US A MINUTE, OKAY?',
'The 1980s':'Pros: meant the end of the 1970s. Cons: \'80s nostalgia.',
'The 21st Century':'The future is NOW!',
'The Academy Awards':'\x02The statue known as "Oscar" weighs only eight and a half pounds. \x0fSo why does it carry so much weight?',
'The Beach':'A day at the beach is no day at the beach, ya know?',
'The Beatles':'\x021960s British band. Only the most revolutionary, influential and universally acclaimed group of the 20th century. \x0fThat\'s all.',
'The CIA':'\x02The Central Intelligence Agency is responsible for keeping the U.S. government informed of foreign actions affecting the nation\'s interest.\x0f',
'The Cold War':'\x02The post-World War II struggle between the US and its allies, and the former USSR and its allies. \x0fThings could have gotten hot.',
'The Common Loon':'\x02A spotted, red-eyed diving bird \x0f-or various friends or family.',
'The Dallas Cowboys':'\x02National Football League team known for their cheerleaders and their performance, \x0fboth on and off the field.',
'The Dump':'Just remember to recycle.',
'The Eiffel Tower':'\x02Designed and built by French engineer Alexandre Gustave Eiffel for the Paris World\'s Fair of 1889.\x0f',
'The Electric Chair':'\x02In U.S. prisons, an alternating current of about 2000 volts is used for electrocution.\x0f',
'The End Of The World':'\x02"It\'s the end of the world as we know it, and I feel fine ..." \x0f-REM',
'The Everglades':'\x02A vast marsh covering much of southern Florida. \x0fWatch out for alligators!',
'The Far Left':'They get high Marx from some.',
'The Far Right':'Far right for some and far wrong for others.',
'The FBI':'\x02The Federal Bureau of Investigation: the investigative agency for the U.S. Department of Justice. \x0fThey\'re listening ...',
'The First Day Of School':'\x02"Fear has many eyes." \x0f-Cervantes',
'The French Riviera':'\x02Holiday home of the rich, the famous, \x0fand the half-naked.',
'The Godfather':'\x02The 1972 critically acclaimed Mafia movie that \x0fmade us as offer we couldn\'t refuse.',
'The Grand Canyon':'\x02217 miles long, 4 to 18 miles wide, and more than 1 mile deep. \x0fNow THAT\'S grand.',
'The Grateful Dead':'\x02American rock band, founded in 1965 and best known for their "Dead Head" fans.\x0f',
'The Great Chicago Fire':'\x02The noteworthy fire of 1871 \x0f... a hot time in the old town ...',
'The Great Depression':'Prozac was invented six decades too late.',
'The Green Bay Packers':'\x02Twelve time National Football League world champions, beloved by "Cheeseheads" everywhere. \x0fAre those brats done yet?',
'The Gulf War':'\x02January - February, 1991. This six week conflict with Iraq was also known as "Desert Storm."\x0f',
'The Indy 500':'\x02Contestants must drive the full 500 miles. \x0fBathroom breaks ARE allowed.',
'The Internet':'\x02Computer-based worldwide information network, \x0fand global shopping market.',
'The IRS':'\x02The Internal Revenue Service: agency of the U.S. Department of the Treasury responsible for collecting taxes. \x0fA human audity.',
'The JFK Assassination':'\x02November 22, 1963. The funeral of President Kennedy was watched on television by millions around the world.\x0f',
'The KKK':'If they\'re supposed to be the master race, why do they keep misspelling "Clan"?',
'The Land Of Oz':'\x02"I\'ve a feeling we\'re not in Kansas anymore, Toto." \x0f-Dorothy, "The Wizard Of Oz"',
'The Little Mermaid':'\x02The 1837 story by Hans Christian Anderson or the 1989 animated film by Disney. \x0fGuess which made more money?',
'The Mafia':'\x02A loose association of criminal groups, bound by a blood oath and sworn to secrecy. \x0fOf course, now we have to kill you.',
'The Marx Brothers':'\x02Chico, Groucho, Harpo, amd sometimes Zeppo. Their 1930s films include Duck Soup and Animal Crackers.\x0f',
'The Metric System':'No, thank you. We like our inches and feet!',
'The Midwest':'\x02America\'s central plains states. \x0fThey\'re not like folks \'round here ...',
'The Milky Way':'\x02The galaxy that includes the sun, its solar system, \x0fand a chewy layer of caramel.',
'The Mississippi River':'\x02The Algonquin words "Misi sipi" mean "big river." \x0fWhat\'s Algonquin for "muddy"?',
'The National Enquirer':'\x02American tabloid newspaper. Inquiring minds want to know \x0f... Why the heck does this thing sell?',
'The New York Yankees':'\x02Legendary American baseball team. \x0fWith so much success, it\'s obvious why they\'re reviled.',
'The NRA':'\x02National Rifle Association. \x0fThey\'re gunning for your vote.',
'The Ocean':'\x02How deep is the ocean? 12,000 feet. \x0fIf they\'d known that, maybe they wouldn\'t have written that stupid song.',
'The Old Man And The Sea':'\x02Ernest Hemingway\'s classic novel \x0f- fishing, hunger, fishing, torment, fishing, personal loss ... fishing ...',
'The Olympics':'\x02An international athletic competition held every four years. \x0fThe thrill of victors and the agony of defeat.',
'The Opera':'It ain\'t over \'til the fat lady sings. Unfortunately, sometimes, not even then.',
'The Ozone Layer':'\x02Short for ozonosphere. \x0fTheories about the ozone layer are full of holes.',
'The Pentagon':'\x02The five-sided home of the U.S. Department of Defense.\x0f',
'The Pyramids':'\x02The Egyptian pyramids were built from about 2700 BC to about 1000 BC. \x0fTut, tut, tut ...',
'The Renaissance':'\x02Beginning in the 1300s, started in Italy and spread across Europe. \x0fKind of like Espresso bars ...',
'The Rolling Stones':'\x02British "bad boy" rock band formed in 1962. \x0fStill touring?',
'The San Andreas Fault':'\x02Geological feature in California stretching 600 miles. \x0fLike the state doesn\'t have enough faults already.',
'The South':'\x02Dixie: South of the Mason-Dixon line, that is. \x0fThey\'re not like folks \'round here ...',
'The Statue Of Liberty':'\x02"Give me your tired, your poor/ Your huddled masses yearning to breathe free ..." \x0f-Emma Lazarus',
'The Super Bowl':'Who needs another national holiday?',
'The Supreme Court':'\x02The highest court in the United States. \x0fRobes, but no wigs.',
'The Three Tenors':'\x02Opera stars Placido Domingo, Jose Carreras, and Luciano Pavarotti began recording as The Three Tenors in 1990.\x0f',
'The Titanic':'\x02It sank in 1912. \x0fGet over it!',
'The Universe':'\x02Everything. The big "It." Huge. Massive. \x0fTHAT big.',
'The Vatican':'\x02The Papal State in the middle of Rome. Home of the Pope, Swiss Guards, \x0fand lots of pigeons.',
'The Vietnam Memorial':'\x02"The Wall," built in 1982, was designed by 21-year-old architecture student, Maya Lin.\0f',
'The Williams Sisters':'\x02Venus, 1980-, and Serena, 1981-, Williams, American tennis champs. \x0fOne heck of a sister act.',
'The Wright Brothers':'\x02In 1903, Wilbur and Orville made the first powered airplane flights in history. \x0fAlthough there were delays at the airport.',
'The YMCA':'\x02The Young Men\'s Christian Association has 30 million members in 110 countries. \x0f"It\'s fun to stay at the Y-M-C-A." -The Village People',
'Thomas Edison':'\x021847-1931, American inventor, developed a light bulb, generator, sound-recorder, and motion picture projector. \x0fShow off.',
'Thunder':'\x02"Here it comes again, Thunder and Lightning..." \x0f-ELO.',
'Tibet':'\x02Mountainous region of China and religious enclave for a form of Buddhism called Lamaism. Known as the roof of the world.\x0f',
'Ticks':'\x02All ticks are bloodsucking parasites, \x0fbut not all bloodsucking parasites are ticks.',
'Tidal Waves':'\x02The gigantic ocean waves that strike with tremendous force, and cause considerable damage to life and property. \x0fKind of like Spring Break.',
'Tiger Woods':'\x021975- , American star of the golf circuit. Known for his athletic skill, and youthful, classic style.\x0f',
'Toasted Marshmallows':'\x02How do you like yours - golden brown or flaming?\x0f',
'Toasters':'Wait -don\'t stick that fork in there!',
'Tobacco Companies':'\x02Who says tobacco\'s not addictive? \x0fTHEY can\'t give it up ...',
'Toes':'\x02"This little piggy went to market ..."\x0f',
'Tom Cruise':'\x021962-, American actor. It looked like Ricky Business early on, but by 1986 he was Top Gun. No Mission Impossible for him.\x0f',
'Tom Hanks':'\x021956-, American actor and star of such varied films as Big, Philadelphia, Forrest Gump, Saving Private Ryan and Castaway.\x0f',
'Top Of A Rollercoaster':'Just remember: what goes UP ...',
'Tornadoes':'\x02Funnel-shaped cloud whirling destructively at speeds up to 300 mph. \x0f"Honey, do you hear a freight train ... Honey?"',
'Toys':'They\'re not just for kids, anymore ...',
'Trailer Parks':'\x02Also known as \x0ftornado magnets.',
'Trampolines':'\x02Trampolines have been used in circuses wince the 18th century. \x0fDespite slumps in popularity, they always seem to bounce back!',
'Tree Huggers':'"Environmentalists" to the left. "Wackos" to the right.',
'Truck Stops':'\x02Breakfast 24 hours a day and you\'re on your way.\x0f',
'Tyrannosaurus Rex':'\x02Large carnivorous dinosaur of the latter part of the Mesozoic era. \x0fMy, what big teeth you have!',
'Underwear':'"Let\'s keep this brief."',
'United Nations':'\x02The U.N. was founded in 1945, after World War II ended. Its mission is to maintain world peace. \x0fIf we ever achieve it, that is ...',
'Vacations':'\x02"Vacation, all I ever wanted, Vacation, had to get away ..." \x0f-Go-Go\'s',
'Vampires':'\x02Legendary bloodsucking monsters.\x0f',
'Victorian England':'\x02An era characterized by moral severity and pompous conservatism.\x0f',
'Video Games':'Just how DO you get to the thirteenth level of "Doom"?',
'Vietnam, 1968':'\x02More than 30,000 Americans had been killed in the Vietnam War by the end of 1968.\x0f',
'Vincent Van Gogh':'\x021853-90, Dutch post-impressionist painter known for dramatic sunflowers and self-portraits. Only one of his paintings sold during his lifetime.\x0f',
'Violins':'\x02It\'s a pain in the neck, but keep practicing.\x0f',
'VW Beetles':'\x02The prototype for the original VW Beetle was developed in 1934, and production begin in 1945. \x0fFunctional, yet so fashionable.',
'Waco, Texas':'\x02Texas city near where a 51-day standoff between law-enforcement officials and members of the Branch Davidians occurred in 1993.\x0f',
'Wall Street':'\x02The financial center of the United States. \x0fSee also: roller coaster.',
'Walt Disney':'\x021901-1966, \x0fthe head of some Mickey Mouse company.',
'Warts':'\x02Small, benign, circumscribed tumors of the outer layer of the skin. \x0fWarts and all!',
'Watching Football':'\x02Sheer athletic prowess by players in peak physical condition is a glorious thing to behold. \x0fPass the chips and beer.',
'Water Parks':'You can go down Dead Man\'s Drop and I\'ll take the Lazy River.',
'Waterbeds':'Could serve as a safety precaution for those who smoke in bed.',
'Waterfalls':'\x02"Don\'t go chasing waterfalls..." \x0f-TLC',
'Watermelons':'\x02Pardeeville, WI - home of the Watermelon Seed-Spitting & Speed-Eating Championship. The record is 2.5 lbs. of melon eaten in 3.5 seconds.\x0f',
'Weapons Dealers':'OK, what kind you need? Assault, Automatic, Atomic ...?',
'Weddings':'"Ding, dong, the bells are gonna chime ..." -My Fair Lady',
'Wheat':'\x02Mainly used in flour. World output of wheat is more than 600 million metric tons a year ... \x0fso someone\'s making a lot of dough.',
'Wheel Of Fortune':'\x02American TV game show, \x0fBIG MONEY! BIG MONEY!.',
'Whipped Cream':'\x02Great on strawberry shortcake, banana splits, chocolate pudding ...\x0f',
'Whips':'\x02"Crack that whip ... whip it, whip it good." \x0f-Devo',
'Whoopie Goldberg':'\x021950-, American actor and comedian. Starred in such movies as Ghost, which earned her an Academy Award. \x0fWhoopee!',
'Will Smith':'\x021968- , Successful American rap star, TV star and wildly successful motion picture star. \x0fHe\'s got it all. We hate him.',
'William Shakespeare':'\x021564-1616, The English poet and playwright. \x0fAnd all the world IS a stage ...',
'Wimbledon':'Strawberries ... cream ... temper tantrums ...',
'Windsurfing':'Really just surfing for lazy people.',
'Wine Tasting':'Spit or swallow?',
'Winning The Lottery':'The more you play, the more THEY win.',
'Witch Hunts':'\x02Popular locations: Salem, Massachusetts \x0fand Washington, D.C.',
'Women':'REAL Women.',
'Women\'s Soccer':'\x02The 1999 World Cup finals was the most-watched women\'s sporting event in history.\x0f',
'Wood Chippers':'\x02"I guess that was your accomplice in the wood chipper." \x0f-Marge Gunderson, Fargo',
'Woodstock':'\x02The 1969 love, music and mud festival attended by 400,000. \x0fOr, the little yellow bird.',
'Woody Allen':'\x021935- , American comedian, actor and director, of Bananas, Annie Hall, Hannah and Her Sisters, and lots of New York Stories.\x0f',
'Worms':'\x02"A man may fish with the worm that hath eat of a king, and eat of the fish that has fed of that worm." \x0f-"Hamlet" Shakespeare',
'X-Ray Vision':'\x02Available to Superman \x0f-for emergency use only.',
'X-Rays':'\x02X-Rays were discovered in 1895 by the German physicist Wilhelm Conrad Roentgen. \x0fNow if they could just get those X-ray glasses down.',
'Yellowstone Park':'\x02Home to 3000 geysers and hot springs. \x0fMore gas and hot air than Washington, D.C.',
'Zen':'\x02Japanese form of Buddhism, originated in China. \x0fZen again, maybe not.',
'Zucchini':'\x02A squashed vegetable.\x0f',
}

class ApplesToApples(BasePlugin):
    def __init__(self, bot, options):
        BasePlugin.__init__(self, bot, options)
        self.output = True
        self.resetdata()
        
    def timer_tick(self):
        if self.gamestate == "InProgress":
            self.timer = self.timer + 1
            if self.timer == 60:
                self.timer = 0
                self.cmd_prompt([], self.channel, self.bot.nickname)

    def msg_channel(self, channel, user, message):
        a = string.split(message, ":", 1)
        if len(a) > 1 and a[0].lower() == self.bot.nickname.lower():
            self.do_command(channel, user, string.strip(a[1]))
        elif message[0]=='!' and (len(message) > 1) and message[1]!='!':
            self.do_command(channel, user, string.strip(message[1:]))
            
    def msg_private(self, user, message):
        self.do_command(user, user, message)

    def reply(self, channel, user, text):
        if channel != user:
            self.bot.pubout(channel, "%s: %s" % (user, text))
        else:
            self.bot.noteout(user, text)

    def privreply(self, user, text):
        self.bot.noteout(user, text)

    def resetdata(self):
        self.gamestate = "None"
        self.players = []
        self.live_players = []
        self.greendeck = GREENCARDS.keys()
        random.shuffle(self.greendeck)
        self.reddeck = REDCARDS.keys()
        random.shuffle(self.reddeck)
        self.judgeindex = 0
        self.hands={}
        self.greencard = None
        self.playedcards = []
        self.woncards = {}
        self.cardstowin = 0
        self.channel = None
        self.timer = 0
        self.judging = False

    def startgame(self):
        self.gamestate = "InProgress"
        self.bot.pubout(self.channel, "A new game is starting! Please wait, dealing cards... (use !peek to see card descriptions)")
        self.players = list(self.live_players)
        random.shuffle(self.live_players)
        for user in self.live_players:
            self.woncards[user] = []
            self.hands[user] = []
        for i in range(1, 8):
            for user in self.live_players:
                self.hands[user].append(self.reddeck.pop(0))
        for user in self.live_players:
            self.hands[user].sort()
            hand = []
            for i in range (1, 8):
                hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
            self.privreply(user, "Your hand: %s" % ", ".join(hand))
        if len(self.live_players) >= 8:
            self.cardstowin = 4
        else:
            self.cardstowin = 12 - len(self.live_players)
        self.judgeindex = len(self.live_players) - 1
        self.newround()

    def endgame(self):
        self.bot.pubout(self.channel, "The game is over.")
        greenbuild = []
        for user in self.players:
            if len(self.woncards[user]) != 0:
                greenbuild.append("%s - %i" % (user, len(self.woncards[user])))
        if greenbuild != []:
            self.bot.pubout(self.channel, "Green cards per players: %s" % ", ".join(greenbuild))
        self.resetdata()
        
    def newround(self):
        self.judging = False
        self.timer = 0
        self.cmd_scores([], self.channel, self.bot.nickname)
        
        self.playedcards = []
        if self.judgeindex == len(self.live_players) - 1:
            self.judgeindex = 0
        else:
            self.judgeindex = self.judgeindex + 1
        self.bot.pubout(self.channel, "This round's judge is %s." % self.live_players[self.judgeindex])
        
        self.greencard = self.greendeck.pop(0)
        self.bot.pubout(self.channel, "The new green card is: \x02\x033%s\x0F - %s. Please play cards from your hand using '!play <number>'." % (self.greencard, GREENCARDS[self.greencard]))
        
    def checkroundover(self):
        if len(self.playedcards) == len(self.live_players) - 1:
            self.bot.pubout(self.channel, "All cards have been played.")
            self.judging = True
            self.beginjudging()
            
    def beginjudging(self):
        if self.judging == True:
            self.timer = 0
            self.bot.pubout(self.channel, "Green card is: \x02\x033%s\x0F - %s" % (self.greencard, GREENCARDS[self.greencard]))
            random.shuffle(self.playedcards)
            for i in range (0, len(self.playedcards)):
                self.bot.pubout(self.channel, "%i. \x034%s\x0F: %s" % (i+1, self.playedcards[i][1], REDCARDS[self.playedcards[i][1]]))
            self.bot.pubout(self.channel, "%s: Please make your decision now using the '!pick <number>' command." % self.live_players[self.judgeindex])
        
    def cardwin(self, winningcard):
        winner = self.playedcards[winningcard][0]
        self.bot.pubout(self.channel, "The judge picked \x034%s\x0F! %s played that red card, and gets to keep the green card." % (self.playedcards[winningcard][1], winner))
        self.woncards[winner].append(self.greencard)
        if not self.checkgamewin():
            self.deal()
            self.newround()
        
    def checkgamewin(self):
        for user in self.players:
            if len(self.woncards[user]) >= self.cardstowin:
                self.bot.pubout(self.channel, "%s now has %i green cards. %s wins!" % (user, len(self.woncards[user]), user))
                self.endgame()
                return True
        else:
            return False

    def deal(self):
        for user in self.live_players:
            while len(self.hands[user]) < 7:
                self.hands[user].append(self.reddeck.pop(0))
                self.privreply(user, "You draw: \x034%s\x0F: %s" % (self.hands[user][len(self.hands[user])-1], REDCARDS[self.hands[user][len(self.hands[user])-1]]))
        for user in self.live_players:
            self.hands[user].sort()
            hand = []
            for i in range (1, 8):
                hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
            self.privreply(user, "Your hand: %s" % ", ".join(hand))
        
    def cmd_play(self, args, channel, user):
        if self.gamestate == "InProgress":
            if user in self.live_players and user not in self.playedcards and user != self.live_players[self.judgeindex] and self.judging == False:
                try:
                    if int(args[0]) > 0 and int(args[0]) < 8:
                        cardplayed = False
                        for cards in self.playedcards:
                            if cards[0] == user:
                                cardplayed = True
                        if cardplayed:
                            self.reply(channel, user, "You have already played a card this round.")
                        else:
                            self.playedcards.append([user, self.hands[user].pop(int(args[0])-1)])
                            self.reply(channel, user, "You have played a card.")
                            self.checkroundover()
                    else:
                        self.reply(channel, user, "Please pick a valid card number (1-7).")
                except:
                    self.reply(channel, user, "Please use the card's number.")
            elif user not in self.live_players:
                self.reply(channel, user, "You are not in this game.")
            elif user in self.playedcards:
                self.reply(channel, user, "You have already played a card this round.")
            elif user == self.live_players[self.judgeindex]:
                self.reply(channel, user, "You are judging this round.")
            elif self.judging == True:
                self.reply(channel, user, "Judging has already begun, wait for the next round.")
        else:
            self.reply(channel, user, "There is no game in progress.")

    def cmd_pick(self, args, channel, user):
        if self.gamestate == "InProgress":
            if self.judging == True and user == self.live_players[self.judgeindex]:
                try:
                    if int(args[0]) > 0 and int(args[0]) <= len(self.playedcards):
                        self.reply(channel, user, "You have chosen.")
                        self.cardwin(int(args[0]) - 1)
                    else:
                        self.reply(channel, user, "Please pick a valid card number.")
                except ValueError:
                    self.reply(channel, user, "Please use the card's number.")
            elif user != self.live_players[self.judgeindex]:
                self.reply(channel, user, "You are not the judge this round.")
            elif len(self.playedcards) != len(self.live_players) - 1:
                self.reply(channel, user, "Not everyone has played a card yet.")
            elif user not in self.live_players:
                self.reply(channel, user, "You are not in this game.")
        else:
            self.reply(channel, user, "There is no game in progress.")
            
    def cmd_peek(self, args, channel, user):
        if self.gamestate == "InProgress":
            if user in self.live_players:
                try:
                    if int(args[0]) > 0 and int(args[0]) <= len(self.hands[user]):
                        self.privreply(user, "\x034%s\x0F - %s" % (self.hands[user][int(args[0])-1], REDCARDS[self.hands[user][int(args[0])-1]]))
                    else:
                        self.reply(channel, user, "Please pick a valid card number.")
                except:
                    self.reply(channel, user, "Please use the card's number.")
            else:
                self.reply(channel, user, "You are not in this game.")
        else:
            self.reply(channel, user, "There is no game in progress.")

    def cmd_start(self, args, channel, user):
        if self.gamestate == "None":
            self.gamestate = "Starting"
            self.bot.pubout(channel, "A new game has been started!")
            self.live_players.append(user)
            self.channel = channel
        elif self.gamestate == "Starting":
            if user in self.live_players and len(self.live_players) > 3:
                self.startgame()
            elif user not in self.live_players:
                self.reply(channel, user, "There is a game starting already. Please join instead.")
            else:
                self.reply(channel, user, "Not enough players to start a game. Minimum of 4 required. Currently: %i" % len(self.live_players))
        elif self.gamestate == "InProgress":
            self.reply(channel, user, "There is a game in progress. Please wait for it to end.")

    def cmd_stats(self, args, channel, user):
        if self.gamestate == "None":
            self.reply(channel, user, "No game in progress.")
        elif self.gamestate == "Starting":
            self.reply(channel, user, "A new game is starting. Currently %i players: %s" % (len(self.live_players), ", ".join(self.live_players)))
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
                
    def cmd_status(self, args, channel, user):
        self.cmd_stats(args, channel, user)

    def cmd_scores(self, args, channel, user):
        if self.gamestate == "None" or self.gamestate == "Starting":
            self.reply(channel, user, "No game in progress.")
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

    def cmd_join(self, args, channel, user):
        if self.gamestate == "None":
            self.reply(channel, user, "No game in progress. Please start one.")
        elif self.gamestate == "Starting":
            if user not in self.live_players:
                self.live_players.append(user)
                self.bot.pubout(self.channel, "%s is now in the game." % user)
            else:
                self.reply(channel, user, "You are already in the game.")
        elif self.gamestate == "InProgress":
            if user not in self.live_players:
                self.bot.pubout(self.channel, "%s is now in the game." % user)
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
                    hand = []
                    for i in range (1, 8):
                        hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
                else:
                    while len(self.hands[user]) < 7:
                        self.hands[user].append(self.reddeck.pop(0))
                        self.privreply(user, "You draw: \x034%s\x0F: %s" % (self.hands[user][len(self.hands[user])-1], REDCARDS[self.hands[user][len(self.hands[user])-1]]))
                self.privreply(user, "Your hand: %s" % ", ".join(hand))
            else:
                self.reply(channel, user, "You are already in the game.")

    def cmd_hand(self, args, channel, user):
        if self.gamestate == "InProgress":
            if user in self.live_players:
                hand = []
                for i in range (1, len(self.hands[user]) + 1):
                    hand.append("%i: \x034%s\x0F" % (i, self.hands[user][i-1]))
                self.privreply(user, "Your hand: %s" % ", ".join(hand))
            else:
                self.reply(channel, user, "You are not in this game.")
        else:
            self.reply(channel, user, "There is no game in progress.")
            
    def cmd_greens(self, args, channel, user):
        if self.gamestate == "InProgress":
            if user in self.live_players:
                if len(self.woncards[user]) != 0:
                    hand = []
                    for i in range (1, len(self.woncards[user]) + 1):
                        hand.append("%i: \x02\x033%s\x0F" % (i, self.woncards[user][i-1]))
                    self.privreply(user, "Your green cards: %s" % ", ".join(hand))
                else:
                    self.privreply(user, "You do not have any green cards yet.")
            else:
                self.reply(channel, user, "You are not in this game.")
        else:
            self.reply(channel, user, "There is no game in progress.")
            
    def cmd_prompt(self, args, channel, user):
        if self.gamestate == "InProgress":
            if len(self.playedcards) != len(self.live_players) - 1:
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
                self.bot.pubout(channel, "%s: Please pick a card to win." % self.live_players[self.judgeindex])
        else:
            self.reply(channel, user, "There is no game in progress.")

    def cmd_quit(self, args, channel, user):
        if self.gamestate == "InProgress":
            if user in self.live_players:
                judge = self.live_players[self.judgeindex]
                self.bot.pubout(self.channel, "%s has quit the game." % user)
                self.live_players.remove(user)
                if len(self.live_players) < 3:
                    self.bot.pubout(self.channel, "There are now too few players to continue the game.")
                    self.endgame()
                else:
                    if self.judgeindex == len(self.live_players):
                        self.judgeindex = 0
                    if user == judge:
                        self.bot.pubout(self.channel, "The judge is now %s." % self.live_players[self.judgeindex])
                        judge = self.live_players[self.judgeindex]
                        print self.playedcards
                        print judge
                        for i in range(0, len(self.playedcards)):
                            print self.playedcards[i-1]
                            if self.playedcards[i-1][0] == judge:
                                print "attempting to remove card"
                                self.playedcards.remove(self.playedcards[i-1])
                        print self.playedcards
                    else:
                      self.judgeindex = self.live_players.index(judge)  
                self.checkroundover()
            else:
                self.reply(channel, user, "You are not in this game.")
        elif self.gamestate == "Starting":
            if user in self.live_players:
                self.bot.pubout(self.channel, "%s has quit the game." % user)
                self.live_players.remove(user)
                if len(self.live_players) == 0:
                    self.bot.pubout(self.channel, "Game is now empty.")
                    self.endgame()
            else:
                self.reply(channel, user, "You are not in this game.")
        else:
            self.reply(channel, user, "There is no game in progress.")
            
    def cmd_del(self, args, channel, user):
        auth = self.bot.plugins['system.Auth']
        userlevel = auth.get_userlevel(user)
        if userlevel > 50:
            if self.gamestate == "InProgress":
                try:
                    player = args[0]
                    if player in self.live_players:
                        judge = self.live_players[self.judgeindex]
                        self.bot.pubout(self.channel, "%s has quit the game." % player)
                        self.live_players.remove(player)
                        if len(self.live_players) < 3:
                            self.bot.pubout(self.channel, "There are now too few players to continue the game.")
                            self.endgame()
                        else:
                            if self.judgeindex == len(self.live_players):
                                self.judgeindex = 0
                            if player == judge:
                                self.bot.pubout(self.channel, "The judge is now %s." % self.live_players[self.judgeindex])
                                judge = self.live_players[self.judgeindex]
                                print self.playedcards
                                print judge
                                for i in range(0, len(self.playedcards)):
                                    print self.playedcards[i-1]
                                    if self.playedcards[i][0] == judge:
                                        print "attempting to remove card"
                                        self.playedcards.remove(self.playedcards[i])
                                print self.playedcards
                                self.beginjudging()
                            else:
                              self.judgeindex = self.live_players.index(judge)  
                        self.checkroundover()
                    else:
                        self.reply(channel, user, "That player is not in this game.")
                except IndexError:
                    self.reply(channel, user, "Please specify the player to delete.")
            elif self.gamestate == "Starting":
                try:
                    player = args[0]
                    if user in self.live_players:
                        self.bot.pubout(self.channel, "%s has been deleted from the game." % player)
                        self.live_players.remove(player)
                        if len(self.live_players) == 0:
                            self.bot.pubout(self.channel, "Game is now empty.")
                            self.endgame()
                    else:
                        self.reply(channel, user, "That player is not in this game.")
                except IndexError:
                    self.reply(channel, user, "Please specify the player to delete.")
            else:
                self.reply(channel, user, "There is no game in progress.")
        else:
            self.reply(channel, user, "You need to be at least a botmod to use that command.")
            
    def cmd_end(self, args, channel, user):
        auth = self.bot.plugins['system.Auth']
        userlevel = auth.get_userlevel(user)
        if userlevel > 50:
            if self.gamestate is not "None":
                self.endgame()
            else:
                self.reply(channel, user, "There is no game in progress.")
        else:
            self.reply(channel, user, "You need to be at least a botmod to use that command during a game.")

    def cmd_help(self, args, channel, user):
        cmds = [i[4:] for i in dir(self) if i.startswith('cmd_')]
        self.reply(channel, user, "Valid commands: '%s'" % "', '".join(cmds))

    def cmd_rules(self, args, channel, user):
        self.reply(channel, user, "Apples to Apples is a very simple, yet surprisingly fun, party game. Playing is easy! Just say !join to join a game, or !start to begin one if there are none starting. Every player gets 7 cards, replenished at the start of each round. A green card is also selected at the start of each round.")
        self.reply(channel, user, "If you are not judging, use !play [number from your hand] to play a card, preferably related to the green card. If you are judging, wait for everyone to play. You can use !prompt to see who has not yet played a card. If you forget your hand, use !hand to see it again. If you want to read a card, use !peek [number from your hand]. To see the green cards you have one, say !greens.")
        self.reply(channel, user, "After all players have put down a card, the Judge gets to choose the winner, with !pick [number]. There is no set criteria to determine the 'best' card. The judge simpy picks the card they like the most! It could be the one that fits the green card best, or the one they find the funniest. It's up to the judge! Players can only learn what the judges like, and use that to their advantage.")

    def do_command(self, channel, user, cmd):
        if cmd=='': return
        cmds = cmd.strip().split(" ")
        cmds[0]=cmds[0].lower()

        try:
            cmd_handler = getattr(self, "cmd_" + cmds[0])
        except AttributeError:
            cmd_handler = None

        if cmd_handler:
            cmd_handler(cmds[1:], channel, user)
            return
