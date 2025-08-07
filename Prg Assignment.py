# PRG1 Assignment 
# Name: Huang Enyu
# Student ID: S10274277E 

import json
from random import randint

player = {}
game_map = []
fog = []

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 1000

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
prices = {'copper': (1, 3), 'silver': (5, 8), 'gold': (10, 18)}

def save_game(filename="savefile.json"):
    data = {
        "player": player,
        "fog": fog
    }
    with open(filename, 'w') as f:
        json.dump(data, f)
    print("Game saved.")

def load_game(filename="savefile.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        player.update(data["player"])
        fog.clear()
        fog.extend(data["fog"])
        load_map("level1.txt", game_map)
        print("Game loaded.")
        return True
    except FileNotFoundError:
        print("No save file found.")
        return False


def load_map(filename, map_struct):
    global MAP_WIDTH, MAP_HEIGHT
    with open(filename, 'r') as f:
        lines = f.readlines()
    map_struct.clear()
    for line in lines:
        map_struct.append(list(line.rstrip('\n')))
    MAP_HEIGHT = len(map_struct)
    MAP_WIDTH = len(map_struct[0]) if MAP_HEIGHT > 0 else 0

def clear_fog(fog, player):
    px, py = player['x'], player['y']
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            x, y = px + dx, py + dy
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                fog[y][x] = False

def initialize_game(game_map, fog, player):
    load_map("level1.txt", game_map)
    fog.clear()
    for row in game_map:
        fog.append([True] * len(row))
    player.clear()
    player['name'] = input("Enter your name: ")
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 1
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY
    player['capacity'] = 10
    player['load'] = 0
    player['portal'] = (0, 0)
    clear_fog(fog, player)

def show_main_menu():
    print("\n--- Main Menu ----")
    print("(N)ew Game")
    print("(L)oad Saved Game")
    print("(Q)uit Game")
    print("------------------")

def show_town_menu():
    print(f"\nDAY {player['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy Stuff")
    print("(I)nformation")
    print("(M)ap")
    print("(E)nter Mine")
    print("Sa(V)e Game")
    print("(Q)uit to Main Menu")
    print("------------------------")

def buy_stuff(player):
    while True:
        print("\nShop:")
        print("(B)ackpack Upgrade")
        print("(L)eave Shop")
        print(f"GP: {player['GP']}")
        choice = input("Your choice? ").lower()
        if choice == 'b':
            cost = player['capacity'] * 2
            if player['GP'] >= cost:
                player['GP'] -= cost
                player['capacity'] += 2
                print(f"Upgraded! New capacity: {player['capacity']}")
            else:
                print("Not enough GP.")
        elif choice == 'l':
            break

def show_information(player):
    print("\n--- Player Info ---")
    for ore in minerals:
        print(f"{ore.title()}: {player[ore]}")
    print(f"GP: {player['GP']}")
    print(f"Steps: {player['steps']}, Load: {player['load']}/{player['capacity']}")
    print(f"Location: ({player['x']}, {player['y']})")

def draw_map(game_map, fog, player):
    print("+" + "-" * MAP_WIDTH + "+")
    for y in range(MAP_HEIGHT):
        print("|", end="")
        for x in range(MAP_WIDTH):
            if x == player['x'] and y == player['y']:
                print("M", end="")
            elif (x, y) == player['portal']:
                print("P", end="")
            elif fog[y][x]:
                print("?", end="")
            else:
                print(game_map[y][x], end="")
        print("|")
    print("+" + "-" * MAP_WIDTH + "+")

def enter_mine(game_map, fog, player):
    print("\nEntering the mine...")
    while player['turns'] > 0:
        draw_map(game_map, fog, player)
        print(f"Turns: {player['turns']}  Load: {player['load']}/{player['capacity']}  Steps: {player['steps']}")
        action = input("(W/A/S/D) Move, (M)ap, (I)nfo, (P)ortal, (Q)uit: ").lower()
        if action in ['w','a','s','d']:
            dx, dy = 0, 0
            if action == 'w': dy = -1
            if action == 's': dy = 1
            if action == 'a': dx = -1
            if action == 'd': dx = 1
            nx, ny = player['x'] + dx, player['y'] + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                tile = game_map[ny][nx]
                if tile in mineral_names:
                    if player['load'] < player['capacity']:
                        ore = mineral_names[tile]
                        amount = randint(1, 3)
                        actual = min(amount, player['capacity'] - player['load'])
                        print(f"Mined {actual} {ore}.")
                        player[ore] += actual
                        player['load'] += actual
                    else:
                        print("You are over-encumbered!")
                elif tile == 'T':
                    print("Returned to town.")
                    break
                player['x'], player['y'] = nx, ny
                player['turns'] -= 1
                player['steps'] += 1
                clear_fog(fog, player)
        elif action == 'm':
            draw_map(game_map, fog, player)
        elif action == 'i':
            show_information(player)
        elif action == 'p':
            print("Using portal to return to town.")
            player['portal'] = (player['x'], player['y'])
            break
        elif action == 'q':
            return

    if player['turns'] <= 0:
        print("You collapsed from exhaustion! Returning to town.")
        player['portal'] = (player['x'], player['y'])
    total = sell_ore()
    if total:
        print(f"Sold ore for {total} GP. Total GP: {player['GP']}")
    player['turns'] = TURNS_PER_DAY
    player['day'] += 1

def sell_ore():
    total = 0
    for ore in minerals:
        qty = player[ore]
        if qty > 0:
            price = randint(*prices[ore])
            earned = qty * price
            print(f"Sold {qty} {ore} for {earned} GP")
            player['GP'] += earned
            total += earned
            player[ore] = 0
    player['load'] = 0
    return total

def main():
    global player, game_map, fog
    print("---------------- Welcome to Sundrop Caves! ----------------")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.")
    print("\nHow quickly can you get the 500 GP you need to retire")
    print("  and live happily ever after?")
    print("------------------------------------------------------------")

    game_state = 'main'
    while True:
        if game_state == 'main':
            show_main_menu()
            choice = input("Your choice? ").lower()
            if choice == 'n':
                initialize_game(game_map, fog, player)
                game_state = 'town'
            elif choice == 'l':
                if load_game():
                    game_state = 'town'
            elif choice == 'q':
                print("Goodbye!")
                break
        elif game_state == 'town':
            show_town_menu()
            choice = input("Your choice? ").lower()
            if choice == 'b':
                buy_stuff(player)
            elif choice == 'i':
                show_information(player)
            elif choice == 'm':
                draw_map(game_map, fog, player)
            elif choice == 'e':
                enter_mine(game_map, fog, player)
                if player['GP'] >= WIN_GP:
                    print(f"\nYou earned {player['GP']} GP and retired in {player['day']} days!")
                    game_state = 'main'
            elif choice == 'v':
                save_game()
            elif choice == 'q':
                game_state = 'main'

main()

# Advanced Feature 1: Input Validation (10 marks)
def get_valid_input(prompt, valid_options):
    while True:
        choice = input(prompt).lower()
        if choice in valid_options:
            return choice
        else:
            print(f"Invalid option. Choose from {', '.join(valid_options).upper()}.")

# Advanced Feature 2: Pickaxe Upgrade (10 marks)
def get_pickaxe_level_name(level):
    return ['None', 'copper', 'silver', 'gold'][level]

def upgrade_pickaxe(player):
    level = player.get('pickaxe', 1)
    if level >= 3:
        print("Your pickaxe is already at max level!")
        return

    cost = 50 if level == 1 else 150
    next_level_name = get_pickaxe_level_name(level + 1)
    if player['GP'] >= cost:
        player['GP'] -= cost
        player['pickaxe'] = level + 1
        print(f"Congratulations! You can now mine {next_level_name}!")
    else:
        print("Not enough GP to upgrade your pickaxe.")

# Modify buy_stuff function to include Pickaxe Upgrade

def buy_stuff(player):
    while True:
        print("\n----------------------- Shop Menu -------------------------")
        level = player.get('pickaxe', 1)
        if level < 3:
            upgrade_cost = 50 if level == 1 else 150
            next_level_name = get_pickaxe_level_name(level + 1)
            print(f"(P)ickaxe upgrade to Level {level + 1} to mine {next_level_name} ore for {upgrade_cost} GP")
        print(f"(B)ackpack upgrade to carry {player['capacity'] + 2} items for {player['capacity'] * 2} GP")
        print("(L)eave shop")
        print("-----------------------------------------------------------")
        print(f"GP: {player['GP']}")
        print("-----------------------------------------------------------")

        choice = get_valid_input("Your choice? ", ['b', 'p', 'l'])

        if choice == 'b':
            cost = player['capacity'] * 2
            if player['GP'] >= cost:
                player['GP'] -= cost
                player['capacity'] += 2
                print(f"Upgraded! New capacity: {player['capacity']}")
            else:
                print("Not enough GP.")

        elif choice == 'p':
            upgrade_pickaxe(player)

        elif choice == 'l':
            break

# Modify enter_mine to use pickaxe level restrictions

def enter_mine(game_map, fog, player):
    print("\nEntering the mine...")
    while player['turns'] > 0:
        draw_map(game_map, fog, player)
        print(f"Turns: {player['turns']}  Load: {player['load']}/{player['capacity']}  Steps: {player['steps']}")
        action = get_valid_input("(W/A/S/D) Move, (M)ap, (I)nfo, (P)ortal, (Q)uit: ", ['w','a','s','d','m','i','p','q'])

        if action in ['w','a','s','d']:
            dx, dy = 0, 0
            if action == 'w': dy = -1
            if action == 's': dy = 1
            if action == 'a': dx = -1
            if action == 'd': dx = 1
            nx, ny = player['x'] + dx, player['y'] + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                tile = game_map[ny][nx]
                can_mine = mineral_names.get(tile, '') in minerals[:player.get('pickaxe', 1)]
                if tile in mineral_names:
                    if not can_mine:
                        print("Your pickaxe is not strong enough to mine this ore!")
                        continue
                    if player['load'] < player['capacity']:
                        ore = mineral_names[tile]
                        amount = randint(1, 3)
                        actual = min(amount, player['capacity'] - player['load'])
                        print(f"Mined {actual} {ore}.")
                        player[ore] += actual
                        player['load'] += actual
                    else:
                        print("Your backpack is full!")
                        continue
                elif tile == 'T':
                    print("Returned to town.")
                    break
                player['x'], player['y'] = nx, ny
                player['turns'] -= 1
                player['steps'] += 1
                clear_fog(fog, player)

        elif action == 'm':
            draw_map(game_map, fog, player)
        elif action == 'i':
            show_information(player)
        elif action == 'p':
            print("Using portal to return to town.")
            player['portal'] = (player['x'], player['y'])
            break
        elif action == 'q':
            return

    if player['turns'] <= 0:
        print("You collapsed from exhaustion! Returning to town.")
        player['portal'] = (player['x'], player['y'])

    total = sell_ore()
    if total:
        print(f"Sold ore for {total} GP. Total GP: {player['GP']}")
    player['turns'] = TURNS_PER_DAY
    player['day'] += 1

# Advanced Feature 3: Top Scores (5 marks)
def save_score():
    scores = []
    try:
        with open("scores.json", "r") as f:
            scores = json.load(f)
    except FileNotFoundError:
        pass

    scores.append({
        'name': player['name'],
        'days': player['day'],
        'steps': player['steps'],
        'GP': player['GP']
    })

    scores = sorted(scores, key=lambda x: (x['days'], x['steps'], -x['GP']))[:5]

    with open("scores.json", "w") as f:
        json.dump(scores, f)

def view_top_scores():
    try:
        with open("scores.json", "r") as f:
            scores = json.load(f)
        print("\nTop 5 Scores:")
        print("-----------------------------")
        for idx, s in enumerate(scores, 1):
            print(f"{idx}. {s['name']} - {s['days']} days, {s['steps']} steps, {s['GP']} GP")
    except FileNotFoundError:
        print("No scores yet.")

# Modify main menu to include top scores

def show_main_menu():
    print("\n--- Main Menu ----")
    print("(N)ew Game")
    print("(L)oad Saved Game")
    print("(T)op Scores")
    print("(Q)uit Game")
    print("------------------")

# Update main game loop to handle top score

def main():
    global player, game_map, fog
    print("---------------- Welcome to Sundrop Caves! ----------------")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.")
    print("\nHow quickly can you get the 500 GP you need to retire")
    print("  and live happily ever after?")
    print("------------------------------------------------------------")

    game_state = 'main'
    while True:
        if game_state == 'main':
            show_main_menu()
            choice = get_valid_input("Your choice? ", ['n', 'l', 't', 'q'])
            if choice == 'n':
                initialize_game(game_map, fog, player)
                player['pickaxe'] = 1
                game_state = 'town'
            elif choice == 'l':
                if load_game():
                    game_state = 'town'
            elif choice == 't':
                view_top_scores()
            elif choice == 'q':
                print("Goodbye!")
                break

        elif game_state == 'town':
            show_town_menu()
            choice = get_valid_input("Your choice? ", ['b', 'i', 'm', 'e', 'v', 'q'])
            if choice == 'b':
                buy_stuff(player)
            elif choice == 'i':
                show_information(player)
            elif choice == 'm':
                draw_map(game_map, fog, player)
            elif choice == 'e':
                enter_mine(game_map, fog, player)
                if player['GP'] >= WIN_GP:
                    print(f"\nYou earned {player['GP']} GP and retired in {player['day']} days!")
                    save_score()
                    game_state = 'main'
            elif choice == 'v':
                save_game()
            elif choice == 'q':
                game_state = 'main'
