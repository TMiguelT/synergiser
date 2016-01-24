import mtgjson
import networkx as nx
from collections import defaultdict

__types = set(['artifact', 'conspiracy', 'creature', 'enchantment', 'instant', 'land', 'phenomenon', 'plane', 'planeswalker',
    'scheme', 'sorcery', 'tribal', 'vanguard'])
__supertypes = set(['basic', 'legendary', 'ongoing', 'snow', 'world'])
__subtypes = set(['Arcane', 'Trap', 'Advisor', 'Ally', 'Angel', 'Antelope', 'Ape', 'Archer', 'Archon', 'Artificer',
    'Assassin', 'Assembly-Worker', 'Atog', 'Aurochs', 'Avatar', 'Badger', 'Barbarian', 'Basilisk', 'Bat', 'Bear',
    'Beast', 'Beeble', 'Berserker', 'Bird', 'Blinkmoth', 'Boar', 'Bringer', 'Brushwagg', 'Camarid', 'Camel', 'Caribou',
    'Carrier', 'Cat', 'Centaur', 'Cephalid', 'Chimera', 'Citizen', 'Cleric', 'Cockatrice', 'Construct', 'Coward',
    'Crab', 'Crocodile', 'Cyclops', 'Dauthi', 'Demon', 'Deserter', 'Devil', 'Djinn', 'Dragon', 'Drake', 'Dreadnought',
    'Drone', 'Druid', 'Dryad', 'Dwarf', 'Efreet', 'Elder', 'Eldrazi', 'Elemental', 'Elephant', 'Elf', 'Elk', 'Eye',
    'Faerie', 'Ferret', 'Fish', 'Flagbearer', 'Fox', 'Frog', 'Fungus', 'Gargoyle', 'Germ', 'Giant', 'Gnome', 'Goat',
    'Goblin', 'God', 'Golem', 'Gorgon', 'Graveborn', 'Gremlin', 'Griffin', 'Hag', 'Harpy', 'Hellion', 'Hippo',
    'Hippogriff', 'Homarid', 'Homunculus', 'Horror', 'Horse', 'Hound', 'Human', 'Hydra', 'Hyena', 'Illusion', 'Imp',
    'Incarnation', 'Insect', 'Jellyfish', 'Juggernaut', 'Kavu', 'Kirin', 'Kithkin', 'Knight', 'Kobold', 'Kor', 'Kraken',
    'Lamia', 'Lammasu', 'Leech', 'Leviathan', 'Lhurgoyf', 'Licid', 'Lizard', 'Manticore', 'Masticore', 'Mercenary',
    'Merfolk', 'Metathran', 'Minion', 'Minotaur', 'Monger', 'Mongoose', 'Monk', 'Moonfolk', 'Mutant', 'Myr', 'Mystic',
    'Naga', 'Nautilus', 'Nephilim', 'Nightmare', 'Nightstalker', 'Ninja', 'Noggle', 'Nomad', 'Nymph', 'Octopus', 'Ogre',
    'Ooze', 'Orb', 'Orc', 'Orgg', 'Ouphe', 'Ox', 'Oyster', 'Pegasus', 'Pentavite', 'Pest', 'Phelddagrif', 'Phoenix',
    'Pincher', 'Pirate', 'Plant', 'Praetor', 'Prism', 'Processor', 'Rabbit', 'Rat', 'Rebel', 'Reflection', 'Rhino',
    'Rigger', 'Rogue', 'Sable', 'Salamander', 'Samurai', 'Sand', 'Saproling', 'Satyr', 'Scarecrow', 'Scion', 'Scorpion',
    'Scout', 'Serf', 'Serpent', 'Shade', 'Shaman', 'Shapeshifter', 'Sheep', 'Siren', 'Skeleton', 'Slith', 'Sliver',
    'Slug', 'Snake', 'Soldier', 'Soltari', 'Spawn', 'Specter', 'Spellshaper', 'Sphinx', 'Spider', 'Spike', 'Spirit',
    'Splinter', 'Sponge', 'Squid', 'Squirrel', 'Starfish', 'Surrakar', 'Survivor', 'Tetravite', 'Thalakos', 'Thopter',
    'Thrull', 'Treefolk', 'Triskelavite', 'Troll', 'Turtle', 'Unicorn', 'Vampire', 'Vedalken', 'Viashino', 'Volver',
    'Wall', 'Warrior', 'Weird', 'Werewolf', 'Whale', 'Wizard', 'Wolf', 'Wolverine', 'Wombat', 'Worm', 'Wraith', 'Wurm',
    'Yeti', 'Zombie', 'Zubera', 'Desert', 'Forest', 'Gate', 'Island', 'Lair', 'Locus', 'Mine', 'Mountain', 'Plains',
    'Power-Plant', 'Swamp', 'Tower', 'Urza’s', 'Aura', 'Curse', 'Shrine', 'Contraption', 'Equipment', 'Fortification'])
__keywords = __types | __subtypes | __supertypes
__keyword_types = ['types', 'supertypes', 'subtypes']
__db = mtgjson.CardDb.from_file('AllSets.json')


class MtgAnalysis:

    @classmethod
    def from_sets(cls, setnames):
        """An analysis based on a list of MtG sets

        :param setnames: A list of MtG three-letter set codes
        """
        sets = [__db.sets[name] for name in setnames]
        cards = [set.cards for set in sets]
        flattened = [card for sublist in cards for card in sublist]
        return cls(flattened)

    @classmethod
    def from_cards(cls, cards):
        """An analysis based on a list of MtG cards

        :param cards: A list of MtG card names as strings
        """
        return cls(cards)

    def __init__(self, cards):
        self.cards = cards
        self.synergies = defaultdict(list)
        self.graph = nx.MultiDiGraph()

    def analyse(self, cards):
        g = self.graph

        # Create nodes
        for i, card in enumerate(cards):
            g.add_node(i, {"card": card})

        # Create edges
        for i, card in enumerate(cards):

            # If the card has no text it can't synergise with anything
            if not 'text' in card:
                continue

            # Work out what cards this card affects
            words = set(card.text.split())
            card_keywords = __keywords & words

            # Join it to any card that it targets
            for j, target_card in enumerate(cards):

                # Make a set of all the types, subtypes and supertypes the target has
                target_keywords = set()
                for keyword_type in __keyword_types:
                    if keyword_type in target_card:
                        target_keywords |= set(target_card[keyword_type])

                # If there's any overlap, draw an edge
                for edge in target_keywords & card_keywords:
                    self.synergies[edge].append((i, j))
                    g.add_edge(i, j, attr_dict={'link': edge})

    def to_arrays(self):
        return (self.graph.edges(data=True), self.graph.nodes(data=True))

    analyse_sets(('ZEN', 'PLC', 'EVE'))
