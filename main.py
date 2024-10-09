import os
import time
import random
import math

clear_terminal = lambda : os.system('cls' if os.name == 'nt' else 'clear')

#
#   UI variables
#
RED = "\033[31m"  # Red text
GREEN = "\033[32m"  # Green text
YELLOW = "\033[33m"  # Yellow text
BLUE = "\033[34m"   # Blue text
BRIGHT_BLUE = "\033[94m"
RESET = "\033[0m"  # Reset to default color

TIME_INTERVAL = 0.6

# Define the total width of the line
total_width = 75

left_width = 20
right_width = total_width - left_width 

NAMED = ["Fear", "Regret", "Fulfillment", "Pain"]

story = {
    "intro": [
        "The journey to the afterlife is difficult with many trials to overcome.\n" +
        "Life and death is connected by a bridge across the world of Oblivion.",
        "Those that stray from the path get consumed by the forgotten.",
        "And you...",
        "You fell from the bridge into the darkness.",
        "As you awake, you are greeted by the entrance of a desolate castle.",
        "There is a large door built into the cliff face of a rocky mountain.\n" +
        "The door is slightly ajar and a dim light can be seen from within.",
    ],
    "throne_room_intro": [
        "Past the door was immediately the throne room.\n" +
        "The light had been a small firepit at the center of the room.\n" +
        "Behind, you can see a figure sitting at the throne. Unmoving.",
        '"Ah, another lost soul seems to have joined us," a deep voice announced.\n' +
        "Startled, you stay silent.",
        '"My my, you have most of your soul intact.\n' +
        'Not many visitors are as fortunate," the figure spoke, book in hand.',
        '"Where am I?" You ask.',
        "Without looking up from its book the figure speaks:\n" +
        '"This is Oblivion: the land of those that are forgotten. If you are here,\n' +
        'then you have been forgotten by the world."',
        "Your heart feels heavy... Though, do you even have a heart anymore?\n" +
        '"Can I leave?" you ask.',
        '"Those that leave a mark on the world seem to find a way out," the figure\n' +
        'replied. "But it will be difficult to leave a mark in the land of the\n ' + 
        'forgotten."',
        'The figure closed its book and stood up to reveal a towering height.\n' +
        'The room felt like it had gotten smaller.\n' +
        '"Though, it is not impossible."',
        "The figure leans down towards you. You make out a tarnished crown on its\n" +
        "head. Its magnificence is apparent despite having a couple missing jewels \n" +
        '"I will be able to help you once you pass three trials."',
        '"You may take them at your own pace, but I can only save you three times.\n' +
        'Once you overcome them, I may be able to create a path back to the bridge"',
        "The figure points up towards the ceiling and you realize that the black\n" +
        "ceiling was the sky. Briefly, a flash lights up the atmosphere and the shadow\n" +
        "of a bridge can be seen in the distance.",
        '"The three doors are on the right lead to each trial," the figure says as it\n' +
        "points to three hallways to the right of the throne.\n" +
        '"You must be prepared to take each trial."',
        '"You may find use in my library to prepare for the trials," the figure said.\n' +
        "It pointed towards the first hallway out of three to the left of the throne.",
        'The figure sat back down on the throne to read its book again\n' +
        '"Good luck," the figure said.'
    ]
}

endings = {
    "leave_castle": [
        "You look around to see a vast grey landscape void of life.\n" +
        "You walk away from the door, towards the bottom of the hill that the\n" +
        "castle stood on.",
        "Suddenly a shadow looms over your shoulders...",
        "Without warning, everything seemed to disappear.",
    ]
}


class Action:
    def __init__(self, name, action_type, value, action_func=None) -> None:
        self.name = name
        self.action_type = action_type
        self.value = value
        self.action_func = action_func
        self.rarity = "common"
    
    def run_action(self, source, target, multiplier=1):
        if (self.action_func):
            self.action_func(source, target, int(self.value * multiplier))
    
    def get_color(self):
        match(self.action_type):
            case "attack":
                return RED
            case "defend":
                return YELLOW
            case "buff":
                return BLUE
        return RESET
    
    def get_name(self):
        color = self.get_color()
        return f"{color}{self.name}{RESET}"
    
    def __str__(self):
        color = self.get_color()
        return f"{color}{self.name : <{15}} |    Power: {self.value : < {3}}{RESET}"

    def __eq__(self, other):
        if isinstance(other, Action):
            return str(self) == str(other)
        return False
    
    def __hash__(self):
        return hash(self.name)


class Character:
    def __init__(self, name) -> None:
        self.name = name
        self.souls = 5

        # Battle Vars
        self.defense = 0
        self.buff = 0
        self.deck = []
        self.hand = []
        self.discards = []
        self.hand_count = 5
        self.action_count = 3

    def remove_card(self, card, count):
        num = 0
        try:
            for _ in range(count):
                self.deck.remove(card)
                num +=1
        except ValueError:
            pass
        return num

    def draw_hand(self):
        self.clean_up_hand()
        while(len(self.hand) < self.hand_count):
            if (len(self.deck) < 1):
                self.shuffle_discard_to_deck()
            self.hand.append(self.deck.pop(0))

    def shuffle_discard_to_deck(self):
        random.shuffle(self.discards)
        self.deck.extend(self.discards)
        self.discards.clear()

    def play_cards(self, card_indices):
        if len(card_indices) > self.action_count:
            return None
        played_cards = []
        check_set = set()
        for i in card_indices:
            if i < len(self.hand):
                played_cards.append(self.hand[i])
                if i in check_set:
                    return None
                check_set.add(i)
            else:
                return None
        for i in card_indices:
            self.discards.append(self.hand[i])
            self.hand[i] = None

        return played_cards
    
    def heal(self, value):
        if value < 1:
            print(format_grammar(f"{self.name} do(es) not accept any souls", self))
            return
        self.souls += value
        print(format_grammar(f"{GREEN}{self.name} (has) absorbed {value} souls.{RESET}", self))

    def take_damage(self, value):
        if value < 1:
            print(format_grammar(f"{self.name} take(s) no damage.", self))
            return
        self.defense -= value
        if self.defense < 0:
            self.souls += self.defense
            self.defense = 0
        print(format_grammar(f"{RED + self.name} took {value} damage.{RESET}", self))

    def defend(self, value):
        if value < 1:
            print(random.choice(FAILURES).format(self.name))
            return
        self.defense += value
        print(format_grammar(f"{YELLOW + self.name} boosted {value} defense.{RESET}", self))
    
    def clean_up_hand(self):
        self.hand = list(filter(lambda c : c != None, self.hand))

    def reset_turn(self):
        self.buff = 0
    
    def end_battle(self):
        self.clean_up_hand()
        self.shuffle_discard_to_deck()
        self.deck.extend(self.hand)
        self.hand.clear()
        self.buff = 0
        self.defense = 0
    
    def is_dead(self):
        return self.souls <= 0
    
    def get_deck_map(self):
        deck_map = {}
        for c in self.deck:
            if c in deck_map:
                deck_map[c] += 1
            else:
                deck_map[c] = 1
        return deck_map


class Book:
    def __init__(self, name: str, action: Action, cost: int):
        self.name = name
        self.action = action
        self.cost = cost


# INIT VARS


#
#   Progression Information
#
books_bought = 0
current_books = []

#
#   Player Information
#
MIN_DECK = 9
lives = 3
player = None


###### Text Mod #####
def format_grammar(text: str, source: Character=None, target: Character=None):
    n1 = source.name if source != None else ""
    n2 = target.name if target != None else ""
    modded = text
    modded = modded.replace("()", "{}")
    if source != None and source.name in NAMED:
        modded = modded.replace("(the) ", "")
    else:
        modded = modded.replace("(the)", "the")
    if source == player:
        modded = modded.replace("(has)", "have")
        modded = modded.replace("('s)", "r")
        modded = modded.replace("(>'s)", "'s")
        modded = modded.replace("(es)", "")
        modded = modded.replace("(s)", "")
        modded = modded.replace("(pronoun)", "your")
        modded = modded.replace("(pronoun2)", "you")
    else:
        modded = modded.replace("(has)", "has")
        modded = modded.replace("('s)", "'s")
        modded = modded.replace("(>'s)", "r")
        modded = modded.replace("(es)", "es")
        modded = modded.replace("(s)", "s")
        modded = modded.replace("(pronoun)", "their")
        modded = modded.replace("(pronoun2)", "them")
    return modded.format(n1, n2)


###### SKILLS ######
def attack(source: Character, target: Character, value: int):
    print("\t", end="")
    target.take_damage(value + source.buff)

def defend(source: Character, target: Character, value: int):
    print("\t", end="")
    source.defend(value + source.buff)

def buff(source: Character, target: Character, value: int):
    if value < 1:
        print("\t" + random.choice(FAILURES).format(source.name))
        return
    source.buff += value
    print(format_grammar(f"\t{BLUE + source.name} got buffed by {value}.{RESET}", source, target))

def intimidate(source: Character, target: Character, value: int):
    if value < 1:
        print("\t" + random.choice(FAILURES).format(source.name))
        return
    target.buff -= int(value * 1.5)
    print(format_grammar(f"\t{RED + target.name} lost {value} buff.{RESET}", source, target))

def lifesteal(source: Character, target: Character, value: int):
    print("\t", end="")
    target.take_damage(int(math.ceil((value + source.buff ) / 2.0)))
    print("\t", end="")
    source.heal(int(math.ceil((value + source.buff ) / 2.0 )))

def decimate(source: Character, target: Character, value: int):
    value = 1 if value == 0 else value
    amount = int(value * 1.5)
    if amount < 0:
        print(format_grammar(f"\t{RED + source.name} explode(s) all the negative energy at {target.name}.{RESET}", source, target))
        print(format_grammar(f"\t{RED + target.name} get(s) (pronoun) soul ripped away. (-{amount} souls){RESET}"))
        target.souls -= amount
    else:
        print(format_grammar(f"\t{RED + source.name} burst(s) all (pronoun) energy at {target.name}. {RESET}", source, target))
        print(format_grammar(f"\t{RED + target.name} get(s) (pronoun) soul ripped away. (-{amount} souls){RESET}"))
        target.souls -= int(amount * 1.5)
    source.buff = 0

def shield_bash(source: Character, target: Character, value: int):
    max = value * 2
    source.defense -= max
    if source.defense < 0:
        max += source.defense
        source.defense = 0
    print(format_grammar(f"\t{YELLOW}{source.name} consume(s) {max} defense.{RESET}", source, target))
    print("\t", end="")
    target.take_damage(max)

def taunt(source: Character, target: Character, value: int):
    amount = value * 2
    if amount < 1:
        print("\t" + random.choice(FAILURES).format(source.name))
        return
    print(format_grammar(f"\t{YELLOW}{source.name} increased (pronoun) defense by {amount}.{RESET}", source))
    print(format_grammar(f"\t{YELLOW}{target.name}('s) energy dissipates. (-{value} buff){RESET}", target))
    source.defense += amount
    target.buff -= amount

def overcome(source: Character, target: Character, value: int):
    value = 1 if value == 0 else value
    amount = value * 3
    if amount < 0:
        print(format_grammar(f"\t{YELLOW}{source.name} broke through (pronoun) struggles. (+{-amount} defense){RESET}", source))
        print(format_grammar(f"\t{YELLOW}{source.name}('s) energy returns.{RESET}", source))
        source.defense += amount
        source.buff = 0 if source.buff < 0 else source.buff
    else:
        print(format_grammar(f"\t{YELLOW}{source.name} increased (pronoun) defense by {amount}.{RESET}", source))
        source.defense += int(amount * 1.5)

def curse(source: Character, target: Character, value: int):
    amount = value * 3
    if amount < 1:
        print("\t" + random.choice(FAILURES).format(source.name))
        return
    print(format_grammar(f"\t{BLUE}{target.name}('s) defense is decreased by {amount}.{RESET}", target))
    target.defense -= amount
    if target.defense < 0:
        target.defense = 0

def focus(source: Character, target: Character, value: int):
    if value < 1:
        print("\t" + random.choice(FAILURES).format(source.name))
        return
    source.buff += value
    source.defense += int(value / 2)
    print(format_grammar(f"\t{BLUE + source.name} got buffed by {value} and raised (pronoun) defense by {int(value / 2)}.{RESET}", source, target))

def enlightenment(source: Character, target: Character, value: int):
    value = 1 if value == 0 else value
    amount = value * 3
    if amount < 0:
        print(format_grammar(f"\t{BLUE + source.name} energy becomes cleansed.{RESET}", source))
        source.buff = abs(source.buff)
    print("\t", end="")
    source.heal(abs(amount))


#####################

MOVE_SET = {
    "attack":       {"name": "Attack",      "type": "attack",   "effect": attack},
    "defend":       {"name": "Defend",      "type": "defend",   "effect": defend},
    "buff":         {"name": "Buff",        "type": "buff",     "effect": buff},
    "life_steal":   {"name": "Life Steal",  "type": "attack",   "effect": lifesteal},
    "intimidate":   {"name": "Intimidate",  "type": "attack",   "effect": intimidate},
    "decimate":     {"name": "Decimate",    "type": "attack",   "effect": decimate},
    "shield_bash":  {"name": "Shield Bash", "type": "defend",   "effect": shield_bash},
    "taunt":        {"name": "Taunt",       "type": "defend",   "effect": taunt},
    "overcome":     {"name": "Overcome",    "type": "defend",   "effect": overcome},
    "curse":        {"name": "Curse",       "type": "buff",     "effect": curse},
    "focus":        {"name": "Focus",       "type": "buff",     "effect": focus},
    "enlighten":    {"name": "Enlighten",   "type": "buff",     "effect": enlightenment},
}

NULL_ACTION = Action("None", "none", 0)

RARITY = {
    "common": ["attack", "defend", "buff"],
    "uncommon": ["life_steal", "focus", "intimidate", "shield_bash", "taunt", "curse"],
    "rare": ["overcome", "decimate", "enlighten"]
}

DESCRIPTIONS = {
    "Attack": [
        "{} throw(s) a punch at {}."
    ],
    "Defend": ["{} harden(s) (pronoun) mental."],
    "Buff": ["{} gather(s) energy."],
    "Life Steal": ["{} drain(s) {}(>'s) soul."],
    "Shield Bash": ["{} use(s) willpower to bash {}."],
    "Focus": ["{} start(s) to close (pronoun) eyes."],
    "Intimidate": ["{} stare(s) deeply into {}(>'s) eyes."],
    "Taunt": ["{} smirk(s) at {} and gesture(s) to come."],
    "Curse": ["{} curse(s) {}."],
    "Overcome": ["{} overcome(s) one of (pronoun) mental barriers."],
    "Decimate": ["{} take(s) a deep breath."],
    "Enlighten": ["{} start(s) to pull fragments of existence towards (pronoun2)"],
    "None": [
        "{} wait(s) for something to happen.",
        "{} stand(s) around."
    ]
}

FAILURES = [
    "{} failed.",
    "{} stumbled",
    "{} flinched"
]

# Book descriptions
b_colors = ['red', 'green', 'blue', 'yellow', 'black', 'white', 'purple', 'orange']
b_sizes = ['pocket-sized', 'small', 'medium-sized', 'large', 'oversized']
b_age = ['worn', 'new', 'antique', 'rare', 'tattered']
b_material = ['leather-bound ', 'paperback ', '']                   #indicates the respected quality of the book based on the base power (ordered high to low)


# Enemy Data
ENEMIES = {
    "Small Soul": {
        "moves": [
            "attack", "attack", "attack",
            "defend", "defend", "defend",
            "buff", "buff", "buff"
            ],
        "values": [1, 1, 1, 1, 1, 1, 2, 2, 3],
        "souls": 5
    },
    "Cloaked Figure": {
        "moves": [
            "attack", "life_steal", "life_steal",
            "defend", "defend", "curse",
            "buff", "buff", "curse"
            ],
        "values": [1, 1, 1, 1, 1, 1, 2, 2, 3],
        "souls": 10
    },
    "Mineral Humanoid": {
        "moves": [
            "attack", "intimidate", "shield_bash",
            "defend", "defend", "shield_bash",
            "buff", "focus", "focus"
            ],
        "values": [1, 1, 1, 1, 1, 2, 2, 2, 2],
        "souls": 20
    },
    "Shrieking Soul": {
        "moves": [
            "attack", "life_steal", "life_steal",
            "intimidate", "life_steal", "defend",
            "buff", "curse", "curse"
            ],
        "values": [1, 1, 2, 2, 2, 2, 2, 3, 3],
        "souls": 5
    }
}

def construct_action(name, power):
    data = MOVE_SET[name]

    if "effect" in data: 
        return Action(data["name"], data["type"], power, data["effect"])
    else:
        return Action(data["name"], data["type"], power)

def generate_book(base_power: int):
    temp = int(random.randint(1, 63))
    eq = int(math.log(temp, 4))
    desc = "rare" if eq < 1 else "uncommon" if eq < 2 else "common"

    p_temp = int(random.randint(1, 63))
    p_eq = int(math.log(p_temp, 4))
    base_power += (3 - p_eq)

    if desc == "rare":
        base_power = int(base_power / 2)
    elif desc == "uncommon":
        base_power -= 1
    base_power = 1 if base_power < 1 else base_power

    rand_action = random.choice(RARITY[desc])
    card = construct_action(rand_action, base_power)
    card.rarity = desc
    
    name = (
        f"{card.get_color()}{random.choice(b_sizes)} " 
        f"{random.choice(b_age)} {random.choice(b_colors)} "
        f"{b_material[p_eq]}book ({desc})"
        f"{RESET}"
    )
    
    cost = get_base_cost(card)
    book = Book(name, card, cost)
    return book

def get_base_cost(action: Action):
    cost = 5 * action.value
    if action.rarity == "rare":
        cost *= cost * cost
    elif action.rarity == "uncommon":
        cost *= 3

    return cost

# Get Upgrade Cost

# Get Sell Cost


def initialize_character():
    player = Character("You")
    
    for n in RARITY["common"]:
        for i in range(3):
            player.deck.append(construct_action(n, 1))

    return player


# Enemies
def generate_enemy(name, enemy_level: int):
    enemy = Character(name)
    
    data = ENEMIES[name]
    random.shuffle(data["moves"])
    random.shuffle(data["values"])
    for i in range(len(data["moves"])):
        a = construct_action(data['moves'][i], enemy_level - 1 + data["values"][i])
        enemy.deck.append(a)
    enemy.souls = data["souls"] * enemy_level

    return enemy


def get_loot(enemy: Character):
    clear_terminal()
    print("===========================================================================")
    temp = int(random.randint(1, 63))
    eq = 2 - int(math.log(temp, 4))

    enemy.clean_up_hand()
    if eq > 0:
        card_loot = random.choices(enemy.deck,k=eq)
        for c in card_loot:
            player.deck.append(c)
            time.sleep(TIME_INTERVAL)
            print(f"A shard of a soul is presented to you...")
            time.sleep(TIME_INTERVAL)
            print(f"You have obtained {c.get_color() + c.name} {c.value}{RESET}.")
    
    soul_count = int(sum([ x.value for x in enemy.deck] ) / 2) + random.randint(0, 10)
    time.sleep(TIME_INTERVAL)
    player.heal(soul_count)
    print("===========================================================================")
    input()


def play_scene(scene_contents):
    for text in scene_contents:
        clear_terminal()
        print("===========================================================================")
        print(text)
        print("===========================================================================")
        print("-- Press enter to continue --")
        input()

def type_statement(statement):
    clear_terminal()
    print("===========================================================================")
    print(statement)
    print("===========================================================================")
    print("-- Press enter to continue --")
    input()

def intro():
    play_scene(story["intro"])
    if decision_one():
        play_scene(story["throne_room_intro"])
    else:
        play_scene(endings["leave_castle"])
        game_over()


#   Player UI
def print_player_stats():
    print("===========================================================================")
    print("Souls: " + str(player.souls) + "                                               Saves " + (" <3 " * lives) + ("    " * (3 - lives)))


def print_player_deck():
    print("===========================================================================")
    print("Deck: ")
    deck_map = player.get_deck_map()
    for i in deck_map:
        print(f"\t{str(i)} x {deck_map[i]} cards")
    print("===========================================================================")


#
#   How should combat work?
#   - Randomness
#   - Choice
#   
#   The user should be able to make decisions in how to defeat the enemy
#   and make a choice based on the flow of the game
#   - I don't like pokemon style battles
#   - the user will have text based choices
#   - the main resource in the game will be their soul
#   - most actions that do not take souls
#   - the user may sacrifice their own soul for battles?
#   - different styles of 
#   - Single Event of figuring out a way to get extra souls
#   - You put your hand on the statue and a soul is consumed
#       - Puzzle for getting more souls
#       - Can either give you 1, 2, 3, or immediately fail

# You are provided with a set of moves that you can queue up
# Decide on 3 moves that you can do

# Three Trials
# Fear, Regrets, Fulfillment, (Pain)


def start_battle(enemy: Character):
    abandon_fight = False
    while(not enemy.is_dead() and not player.is_dead()):
        enemy.reset_turn()
        player.reset_turn()
        enemy.draw_hand()
        player.draw_hand()
        enemy_moves = AI.get_enemy_turn(enemy=enemy)
        your_moves = None
        card_order = None
        while(your_moves == None):
            clear_terminal()
            print("===========================================================================")
            print_battle_stats(player, enemy)
            print("===========================================================================")
            print("The enemy is planning to: ", end="\n\t")
            for i in range(len(enemy_moves)):
                if i >= len(enemy_moves) - 1:
                    print("??????", end="   ")
                else:
                    print(enemy_moves[i].get_name(), end="   ")
            print()
            if card_order != None:
                print("You cannot play: " + card_order)
            print("Choose your cards to play in order:          Actions Available: " + str(player.action_count))
            print("Your hand: ")
            print_hand(player)
            escape_cost = 10 if player.souls > 11 else int(player.souls / 2)
            if escape_cost > 0:
                print(f"\tE: Sacrifice your soul to escape. ({escape_cost} souls)")
            else:
                print("\tE: You cannot currently escape!")

            card_order = input()
            if card_order == "e" and escape_cost > 0:
                player.souls -= escape_cost
                abandon_fight = True
                clear_terminal()
                type_statement(
                    format_grammar(f"You rip away {escape_cost} souls and throw it towards (the) {enemy.name}.", enemy)
                )
                break
            try:
                num_list = [int(i) - 1 for i in card_order.split()]
                your_moves = player.play_cards(num_list)
            except:
                pass
        if abandon_fight:
            break
        run_battle_simulation(player, your_moves, enemy, enemy_moves)
    player.end_battle()
    enemy.end_battle()


def enemy_death(enemy: Character):
    type_statement(f"{enemy.name} has been completely forgotten...")


def print_battle_stats(c1: Character, c2: Character):
    print(f"{c1.name:<{left_width}}{c2.name:>{right_width}}")
    print(f"{'Souls: ' + str(c1.souls):<{left_width}}{'Souls: ' + str(c2.souls):>{right_width}}")
    print(f"{'Defense: ' + str(c1.defense):<{left_width}}{'Defense: ' + str(c2.defense):>{right_width}}")
    print(f"{'Buff: ' + str(c1.buff):<{left_width}}{'Buff: ' + str(c2.buff):>{right_width}}")


def print_hand(c: Character):
    for i in range(len(c.hand)):
        print("\t" + str(i + 1) + ": " + str(c.hand[i]))


def run_battle_simulation(c1: Character, c1_moves: list, c2: Character, c2_moves):
    num_turns = max(len(c1_moves), len(c2_moves))
    clear_terminal()
    print("===========================================================================")
    for i in range(num_turns):
        action_1 = NULL_ACTION
        action_2 = NULL_ACTION
        if i < len(c1_moves):
            action_1 = c1_moves[i]
        if i < len(c2_moves):
            action_2 = c2_moves[i]
        run_action(c1, action_1, c2, action_2)
        if c1.is_dead() or c2.is_dead():
            break
    print("===========================================================================")
    print_battle_stats(c1, c2)
    print("===========================================================================")
    print("-- Press enter to continue --")
    input()


def run_action(c1: Character, a1: Action, c2: Character, a2: Action):
    winner = check_win(a1, a2)
    if winner == "a1":
        apply_action(c1, c2, a1, 2)
        apply_action(c2, c1, a2, 0.5)   
    elif winner == "a2":
        apply_action(c2, c1, a2, 2)
        apply_action(c1, c2, a1, 0.5)
    else:
        apply_action(c1, c2, a1, 1)
        apply_action(c2, c1, a2, 1)   


def apply_action(source: Character, target: Character, action: Action, multiplier: float):
    time.sleep(TIME_INTERVAL)
    print(format_grammar(f"{action.get_color()}" + random.choice(DESCRIPTIONS[action.name]) + RESET, source, target))
    time.sleep(TIME_INTERVAL)
    action.run_action(source, target, multiplier)


def check_win(a1: Action, a2: Action):
    if a1.action_type == a2.action_type:
        return "draw"
    if (
        a1.action_type == "defend" and a2.action_type == "attack" or
        a1.action_type == "attack" and a2.action_type == "buff" or
        a1.action_type == "buff" and a2.action_type == "defend"
    ):
        return "a1"
    return "a2"


#
#   Throne Room!
#
def throne_room():
    response = None
    while (True):
        if player.is_dead():
            if lives > 0:
                player_gets_saved()
                player.souls = 5
            else:
                game_over()
                return
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print(f"{BRIGHT_BLUE}The Throne Room{RESET}".center(total_width, ' '))
        print("The fireplace flickers warmly at the center of the throne room.")
        print()
        print("What would you like to do?")
        print("\t1: Challenge the trials")
        print("\t2: Enter the first hallway to the left")         # The Library               (Exchanging Souls for Perks and getting information)
        print("\t3: Enter the second hallway to the left")        # The Well of Forgiveness   (Removing Perks?)
        print("\t4: Enter the third hallway to the left")         # The Grand Hallway         (Fighting smaller mobs to gather resources)
        print("\t5: Talk to the figure")
        print("\tE: Exit")
        print("===========================================================================")
        if response != None and response not in ['1', '2', '3', '4', '5', 'e']:
            print(response + " is not a valid choice")
        response = input("->").lower()
        match response:
            case "1":
                pass
            case "2":
                library()
            case "3":
                the_study()
            case "4":
                the_lost_souls()
            case "5":
                pass
            case "e":
                return


#
#   Library
#
def library():
    response = None
    while (True):
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print(f"{BRIGHT_BLUE}The Library{RESET}".center(total_width, ' '))
        print("The walls are surrounded by bookshelves and the smell of old books pervade")
        print("the room. There is a mirror at the entrance and a figure is seen organizing")
        print("books on the side. A pile of books lay near the back.")
        print()
        print("What would you like to do?")
        print("\t1: Look into the mirror")                              # Check Stats
        print("\t2: Browse through the shelves of books")               # Buy Cards in the shop
        print("\t3: Walk towards the pile of books")                    # Gacha Cards
        print("\t4: ")                                                  # Perks?
        print("\t5: Talk to the figure")
        print("\tE: Return to the throne room")
        print("===========================================================================")
        if response not in ['1', '2', '3', '4', '5', 'e'] and response != None:
            print(str(response) + " is not a valid choice")
        response = input("->").lower()
        match response:
            case "1":
                clear_terminal()
                print_player_stats()
                print_player_deck()
                print("-- Press enter to continue --")
                input()
            case "2":
                shop()
            case "3":
                pass
            case "4":
                pass
            case "5":
                pass
            case "e" | "E":
                return


def fill_shop():
    while len(current_books) < 5:
        current_books.append(generate_book(int(books_bought / 5) + 1))


def shop():
    response = None
    while (True):
        fill_shop()
        archive_cost = int(int(sum([x.cost for x in current_books]) * 0.9) / 10) * 10
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print("You walk towards a shelf filled with unorganized books of varying colors")
        print("and sizes.")
        print(f"The section is labeled as: Section {int(books_bought / 5) + 1}")
        print()
        print("You see a collection of books:")
        for i in range(len(current_books)):
            book = current_books[i]
            print(f"    {str(i+1) + ': A ' + book.name :<{70}} {'cost: ' + str(book.cost) : >{total_width - 74}}")
        print(f"    6: Archive books for {archive_cost} souls.")
        print(f"    E: Stop looking.")
        print("===========================================================================")
        if response not in ['1', '2', '3', '4', '5', '6', 'e'] and response != None:
            print(str(response) + " is not a valid choice")
        response = input("->").lower()
        if response == "e":
            return
        elif response == "6":
            archive_books(archive_cost)
        elif response in ['1', '2', '3', '4', '5']:
            book_index = int(response) - 1
            buy_book(book_index)


def archive_books(cost):
    global books_bought
    if player.souls > cost + 1:
        response = None
        while(True):
            clear_terminal()
            print_player_stats()
            print("===========================================================================")
            print(f"You are about to archive all of the available books...")
            print("Are you sure? y/n")
            print("===========================================================================")
            response = input("->").lower()
            if response == "n":
                return
            elif response == "y":
                player.souls -= cost
                books_bought += 5
                current_books.clear()
                type_statement("The books have been archived...")
                return
    else:
        type_statement("You are unable to archive the books...")


def buy_book(book_index):
    global books_bought
    if book_index > len(current_books) - 1:
        print("Cannot find the book...")
        return
    book: Book = current_books[book_index]
    if player.souls > book.cost + 1:
        response = None
        while(True):
            clear_terminal()
            print_player_stats()
            print("===========================================================================")
            print(f"You are trying to open this book...           Cost: {book.cost} souls")
            print("Are you sure? y/n")
            print("===========================================================================")
            response = input("->").lower()
            if response == "n":
                return
            elif response == "y":
                player.souls -= book.cost
                current_books.pop(book_index)
                books_bought += 1
                player.deck.append(book.action)
                type_statement(
                    f"You have read: {book.name}\n"
                    f"You learned {book.action.get_color()}{book.action.name} {book.action.value}.{RESET}"
                )
                return
    else:
        type_statement("You are unable to handle the books contents...")


def gacha_books():
    response = None
    while(True):
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print("The pile of books seems to allure you...")
        print("Would you offer your soul to the books?")
        print("===========================================================================")
        response = input("->")
        if response == "n":
            return
        elif response == "y":
            return


#
#   The Study
#
def the_study():
    response = None
    while (True):
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print(f"{BRIGHT_BLUE}The Study{RESET}".center(total_width, ' '))
        print("You enter a small room with a large desk and chair. There is a pile of ")
        print("clean parchment paper with a quill and ink on top of the desk.")
        print()
        print("What would you like to do?")
        print("\t1: Write out your thoughts.")                   # Sell Cards
        print("\t2: ")
        print("\tE: Return to the throne room.")
        print("===========================================================================")
        if response not in ['1', '2', '3', '4', '5', 'e'] and response != None:
            print(str(response) + " is not a valid choice")
        response = input("->").lower()
        match response:
            case "1":
                discard_cards()
            case "2":
                pass
            case "3":
                pass
            case "4":
                pass
            case "5":
                pass
            case "e":
                break


def discard_cards():
    response = None
    page_index = 0
    while (True):
        deck_map = player.get_deck_map()
        card_keys = list(deck_map.keys())
        discard_count = len(player.deck) - MIN_DECK
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print("A blank sheet of paper is laid in front of you.")
        print("Quill in hand, you ponder what to write onto the paper...")
        print()
        print(f"Select the cards to discard. You may discard up to {discard_count} cards")
        for i in range(5):
            d = page_index * 5 + i
            if d < len(card_keys):
                card = card_keys[d]
                print(f"\t{i + 1}: {str(card)} x {deck_map[card]} cards ")
        if page_index > 0:
            print("\tB: Go back one page")
        if (page_index + 1) * 5 < len(card_keys):
            print("\tF: Go forward one page.")
        print("\tE. Return to the throne room.")
        print("===========================================================================")
        if response not in ['1', '2', '3', '4', '5', 'e', 'b', 'f'] and response != None:
            print(str(response) + " is not a valid choice")
        response = input("->").lower()
        if response in ['1', '2', '3', '4', '5']:
            if discard_count < 1:
                type_statement("You are unable to discard any more cards.")
                continue
            else:
                card = card_keys[page_index * 5 + (int(response) - 1)]
                discard_card_count(card, deck_map[card], discard_count)
        else:
            match response:
                case "b":
                    if page_index > 0:
                        page_index -= 1
                case "f":
                    if (page_index + 1) * 5 < len(card_keys):
                        page_index += 1
                case "e":
                    return


def discard_card_count(card, curr_count, max_count):
    user_input = None
    while (True):
        clear_terminal()
        print("===========================================================================")
        print(f"How many cards would you like to discard? ( ? / {curr_count} )")
        print("===========================================================================")
        if user_input != None:
            print(user_input + " is not a valid input.")
        user_input = input("->")
        if can_convert_to_int(user_input):
            if int(user_input) > max_count:
                type_statement("Unable to discard that many cards.")
            elif int(user_input) > curr_count:
                type_statement("There are not that many cards.")
            else:
                removed = player.remove_card(card, int(user_input))
                dt = (TIME_INTERVAL * 1.5) / (1 if removed < 1 else removed)
                dt = min(TIME_INTERVAL, dt)
                clear_terminal()
                print("===========================================================================")
                if removed == 0:
                    print("You leave the sheet of parchment paper blank.")
                for i in range(removed):
                    time.sleep(dt)
                    print(f"You write away a thought... (\"{card.name} {card.value}\" has been removed)")
                    time.sleep(dt)
                    player.heal(card.value * 5)
                print("===========================================================================")
                print("-- Press enter to continue --")
                input()
            break   


#
#
#
def the_lost_souls():
    global lives
    response = None
    while (True):
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print(f"{BRIGHT_BLUE}The Castle Dungeons{RESET}".center(total_width, ' '))
        print("A grand hallway stands before you.")
        print("As your eyes follow the floor towards the end, the light seems to fade")
        print("until only darkness is left.")
        print()
        print("What would you like to do?")
        print("\t1: Explore.")                                           # Dungeon
        print("\t2. Step into the room at the side... (DANGER)")         # Hard Mode
        print("\tE: Return to the throne room.")
        print("===========================================================================")
        if response not in ['1', '2', '3', '4', '5', 'e'] and response != None:
            print(str(response) + " is not a valid choice")
        response = input("->").lower()
        match response:
            case "1":
                dungeon()
            case "2":
                pass
            case "e":
                return
        if player.is_dead():
            lives -= 1
            return


def dungeon():
    response = None
    while (True):
        clear_terminal()
        print_player_stats()
        print("===========================================================================")
        print("How far are you exploring?")
        print("\t1: Not too far.")
        print("\t2: A casual distance.")
        print("\t3: Into the darkness")
        print("\tE: Return to the entrance.")
        print("===========================================================================")
        if response not in ['1', '2', '3', '4', '5', 'e'] and response != None:
            print(str(response) + " is not a valid choice")
        response = input("->").lower()
        if response == 'e':
            return
        elif response in ['1', '2', '3']:
            explore(int(response))
            if player.is_dead():
                return


LEVEL_VALS = [0, 1, 3, 10, 20]
LEVEL_ENEMY = {
    1: ["Small Soul", "Cloaked Figure", "Mineral Humanoid", "Shrieking Soul"],
    2: ["Small Soul", "Cloaked Figure", "Mineral Humanoid", "Shrieking Soul"],
    3: ["Small Soul", "Cloaked Figure", "Mineral Humanoid", "Shrieking Soul"]
}
def explore(level):
    diff = LEVEL_VALS[level + 1] - LEVEL_VALS[level]
    temp = random.randint(1, pow(2, diff) - 1)
    eq = int(math.log(temp, 2))
    level_scale = LEVEL_VALS[level] + eq

    enemy = generate_enemy(random.choice(LEVEL_ENEMY[level]), level_scale)

    print_player_stats()
    type_statement(
        f"You have encountered a lvl. {level_scale} {enemy.name}.\n" +
        "You prepare yourself..."
    )
    
    start_battle(enemy)
    if enemy.is_dead():
        enemy_death(enemy)
        get_loot(enemy)
    elif not player.is_dead():
        type_statement("You managed to get away with most of your soul intact...")



#
#   Endings
#
def player_gets_saved():
    type_statement(
        "Your vision starts to blur as you try to keep your conciousness in the \n" +
        "present...\n" + 
        "Everything starts to disappears into complete oblivion..."
    )
    type_statement(
        "A cold hand suddenly jerks you towards the sky and you wake up gasping\n" +
        "for air."
    )
    type_statement(
        '"You were almost returned to the essence of oblivion... Welcome back,"\n' +
        "a voice said.\n" +
        "Looking around, you were back at the throne room and see the figure \n" + 
        "back at its throne.\n" +
        f'"I can only save you {lives} more time' + ("s" if lives > 1 else "") + '.' +
        'You will need to proceed with caution."'
    )
    type_statement("The figure picks up its usual book and starts to read again.")



def game_over():
    pass


def decision_one():
    response = None
    while (response not in ["1", "2"]):
        clear_terminal()
        print("==========================================================================")
        print("Will you go through the door?")
        print("\t1. Yes")
        print("\t2. No")
        print("==========================================================================")
        if response != None:
            print("Enter '1' or '2'")
        response = input("->")
        if response == "1":
            return True
        elif response == "2":
            return False

#
#
#

class AI:
    @staticmethod
    def get_enemy_turn(enemy: Character):
        enemy.draw_hand()
        action_i = list(range(enemy.action_count))
        return enemy.play_cards(action_i)
        

def test_battle():
    enemy = Character("Fear")
    for i in MOVE_SET:
        for j in range(2):
            enemy.deck.append(construct_action(i, 1))
    random.shuffle(enemy.deck)
    random.shuffle(player.deck)

    start_battle(enemy)


def can_convert_to_int(s):
    try:
        int(s)  # Try converting the string to an integer
        return True  # Conversion successful
    except ValueError:
        return False

if __name__ == "__main__":
    player = initialize_character()
    #test_battle()

    intro()
    throne_room()
    