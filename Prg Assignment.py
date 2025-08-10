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
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
prices = {'copper': (1, 3), 'silver': (5, 8), 'gold': (10, 18)}

def save_game(filename="savefile.json"): 
    # Save the current game state (player info, fog map, and mine map) into a JSON file
    # Input: filename (string, optional) - file name to save game
    # Output: None
    data = {
        "player": player,
        "fog": fog,
        "game_map": game_map # Save the map state too
    }
    with open(filename, 'w') as f:
        json.dump(data, f)
    print("Game saved.")

def load_game(filename="savefile.json"):
    # Load a previously saved game state from a JSON file
    # Restores player data, fog of war, and mine map
    # Returns True if loaded successfully, False if file not found
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        player.update(data["player"])
        fog.clear()
        fog.extend(data["fog"])
        game_map.clear()
        game_map.extend(data["game_map"])
    # Load the saved map state
 
        print("Game loaded.")
        return True
    except FileNotFoundError:
        print("No save file found.")
        return False

def load_map(filename, map_struct):
    # Load the mine layout from a text file into the game map structure
    # Updates global MAP_WIDTH and MAP_HEIGHT values
    global MAP_WIDTH, MAP_HEIGHT
    with open(filename, 'r') as f:
        lines = f.readlines()
    map_struct.clear()
    for line in lines:
        map_struct.append(list(line.rstrip('\n')))
    MAP_HEIGHT = len(map_struct)
    MAP_WIDTH = len(map_struct[0]) if MAP_HEIGHT > 0 else 0
    # Ensure town is marked at (0,0)
    if MAP_HEIGHT > 0 and MAP_WIDTH > 0:
        game_map[0][0] = 'T'

def clear_fog(fog, player):
    # Reveal tiles around the player's current position (3x3 area)
    # This removes the fog in that area
    px, py = player['x'], player['y']
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            x, y = px + dx, py + dy
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                fog[y][x] = False

def initialize_game(game_map, fog, player):
    # Start a new game by loading the map, clearing fog, and setting initial player stats
    load_map("level1.txt", game_map)
    fog.clear()
    for row in game_map:
        fog.append([True] * len(row))
    player.clear()
    print("Greetings, miner! What is your name? ", end="")
    player['name'] = input().strip()
    print(f"Pleased to meet you, {player['name']}. Welcome to Sundrop Town!")
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
    # Display the main menu options to the player
    print("\n--- Main Menu ----")
    print("(N)ew Game")
    print("(L)oad Saved Game")
    print("(T)op Scores")
    print("(Q)uit")
    print("------------------")

def show_town_menu():
     # Display the town menu options for actions in Sundrop Town
    print(f"\nDAY {player['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy Stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter Mine")
    print("Sa(V)e Game")
    print("(Q)uit to Main Menu")
    print("------------------------")

def buy_stuff(player):
    # Allow the player to buy upgrades (backpack capacity or pickaxe)
    # Loops until player chooses to leave shop
    while True:
        print("\n----------------------- Shop Menu -------------------------")
        level = player.get('pickaxe', 1)
        if level < 3:
            upgrade_cost = 50 if level == 1 else 150
            next_level_name = get_pickaxe_level_name(level + 1)
            print(f"(P)ickaxe upgrade to Level {level + 1} to mine {next_level_name} ore for {upgrade_cost} GP")
        
        # Improved backpack upgrade message
        current_capacity = player['capacity']
        upgrade_cost = current_capacity * 2
        new_capacity = current_capacity + 2
        print(f"(B)ackpack upgrade to carry {new_capacity} items for {upgrade_cost} GP")
        
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
                print(f"Congratulations! You can now carry {player['capacity']} items!")
            else:
                print(f"Not enough GP. You need {cost} GP but only have {player['GP']} GP.")
        elif choice == 'p':
            upgrade_pickaxe(player)
        elif choice == 'l':
            break

def show_information(player):
     # Display the current player's information (stats, position, inventory)
    print("\n--- Player Information ---")
    print(f"Name: {player['name']}")
    print(f"Current position: ({player['x']}, {player['y']})")
    
    # Pickaxe level display
    pickaxe_level = player.get('pickaxe', 1)
    if pickaxe_level == 1:
        print("Pickaxe level: 1 (copper)")
    elif pickaxe_level == 2:
        print("Pickaxe level: 2 (silver)")
    elif pickaxe_level == 3:
        print("Pickaxe level: 3 (gold)")
    
    # Mineral counts
    print(f"Gold: {player['gold']}")
    print(f"Silver: {player['silver']}")
    print(f"Copper: {player['copper']}")
    print("------------------------------")
    print(f"Load: {player['load']} / {player['capacity']}")
    print("------------------------------")
    print(f"GP: {player['GP']}")
    print(f"Steps taken: {player['steps']}")
    print("------------------------------")
    

def draw_map(game_map, fog, player):
      # Display the entire mine map with fog of war applied
    # Shows player (M), town (T), portal (P), minerals, and fog (?)
    print()
    print("+" + "-" * MAP_WIDTH + "+")
    for y in range(MAP_HEIGHT):
        print("|", end="")
        for x in range(MAP_WIDTH):
            if x == player['x'] and y == player['y']:
                print("M", end="")
            elif (x, y) == (0,0):
                print("T", end="")
            elif (x, y) == player['portal']:
                print("P", end="")
            elif fog[y][x]:
                print("?", end="")
            else:
                print(game_map[y][x], end="")
        print("|")
    print("+" + "-" * MAP_WIDTH + "+")
    print()


def enter_mine(game_map, fog, player):
     # Main loop for when the player is inside the mine
    # Handles movement, mining, turn countdown, exhaustion, and portal use
    print("\nEntering the mine...")
    if player['portal'] != (0, 0):
        player['x'], player['y'] = player['portal']
    else:
        player['x'], player['y'] = 0, 0

    while player['turns'] > 0:
        # Draw the viewport with border
        print("+" + "-" * 3 + "+")
        for dy in range(-1, 2):
            y = player['y'] + dy
            print("|", end="")
            for dx in range(-1, 2):
                x = player['x'] + dx
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    if dx == 0 and dy == 0:
                        print("M", end="")
                    elif (x, y) == player['portal']:
                        print("P", end="")
                    elif not fog[y][x]:
                        print(game_map[y][x], end="")
                    else:
                        print("#", end="")  # Use # for fogged areas in viewport
                else:
                    print("#", end="")  # Use # for out of bounds areas
            print("|")
        print("+" + "-" * 3 + "+")
        
        print(f"Turns left: {player['turns']} | Load: {player['load']}/{player['capacity']} | Steps: {player['steps']}")
        print("(WASD) to move")
        print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")
        action = get_valid_input("Action? ", ['w','a','s','d','m','i','p','q'])

        if action in ['w','a','s','d']:
            dx, dy = 0, 0
            if action == 'w': dy = -1
            elif action == 's': dy = 1
            elif action == 'a': dx = -1
            elif action == 'd': dx = 1
            
            nx, ny = player['x'] + dx, player['y'] + dy
            
            # Check if new position is within bounds
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                tile = game_map[ny][nx]
                
                # Check if stepping onto town tile
                if tile == 'T' and nx == 0 and ny == 0:
                    print("Returned to town.")
                    sell_ore()
                    player['turns'] = TURNS_PER_DAY
                    player['day'] += 1
                    return
                
                # Mining logic
                can_mine = mineral_names.get(tile, '') in minerals[:player.get('pickaxe', 1)]
                if tile in mineral_names:
                    if not can_mine:
                        print("Your pickaxe is not strong enough to mine this ore!")
                        player['turns'] -= 1
                        continue
                    if player['load'] >= player['capacity']:
                        print()
                        print("---------------------------------------------------")
                        print("You can't carry any more, so you can't go that way.")
                        player['turns'] -= 1
                        if player['turns'] <= 0:
                            print("You are exhausted.")
                            print("You place your portal stone here and zap back to town.")
                            player['portal'] = (player['x'], player['y'])
                            sell_ore()
                            player['turns'] = TURNS_PER_DAY
                            player['day'] += 1
                            return
                        continue
                        
                    ore = mineral_names[tile]
                    amount = randint(1, 5 if ore == 'copper' else (3 if ore == 'silver' else 2))
                    actual = min(amount, player['capacity'] - player['load'])
                    if actual < amount:
                        print(f"You mined {amount} piece(s) of {ore}.")
                        print(f"...but you can only carry {actual} more piece(s)!")
                    else:
                        print(f"You mined {actual} piece(s) of {ore}.")
                    player[ore] += actual
                    player['load'] += actual
                    game_map[ny][nx] = ' '
                
                # Move the player
                player['x'], player['y'] = nx, ny
                player['turns'] -= 1
                player['steps'] += 1
                clear_fog(fog, player)
                
                # Check if turns ran out
                if player['turns'] <= 0:
                    print("You are exhausted.")
                    print("You place your portal stone here and zap back to town.")
                    player['portal'] = (player['x'], player['y'])
                    sell_ore()
                    player['turns'] = TURNS_PER_DAY
                    player['day'] += 1
                    return
            else:
                print("You can't move outside the mine!")
                player['turns'] -= 1
        
        elif action == 'p':
            print()
            print("-----------------------------------------------------")
            print("You place your portal stone here and zap back to town.")
            player['portal'] = (player['x'], player['y'])
            sell_ore()
            player['turns'] = TURNS_PER_DAY
            player['day'] += 1
            return
        
        elif action == 'm':
            draw_map(game_map, fog, player)
        elif action == 'i':
            show_information(player)
        elif action == 'q':
            return

    # If turns run out (defensive check)
    if player['turns'] <= 0:
        print("You collapsed from exhaustion! Returning to town.")
        player['portal'] = (player['x'], player['y'])
        sell_ore()
        player['turns'] = TURNS_PER_DAY
        player['day'] += 1
        
    elif action == 'p':
             print("You place your portal stone here and zap back to town.")
             player['portal'] = (player['x'], player['y'])
             if game_map[player['y']][player['x']] == 'M':  
                game_map[player['y']][player['x']] = 'P'
             sell_ore()
             player['turns'] = TURNS_PER_DAY
             player['day'] += 1
             return
    
    elif action == 'm':
            draw_map(game_map, fog, player)

    if player['turns'] <= 0:
        print("You collapsed from exhaustion! Returning to town.")
        player['portal'] = (player['x'], player['y'])
    total = sell_ore()
    player['turns'] = TURNS_PER_DAY
    player['day'] += 1

def sell_ore():
     # Sell all minerals in the player's inventory for GP at random prices
    # Resets load and ore counts after selling
    total = 0
    for ore in minerals:
        qty = player[ore]
        if qty > 0:
            price = randint(*prices[ore])
            earned = qty * price
            print(f"You sell {qty} {ore} ore for {earned} GP.")
            player['GP'] += earned
            total += earned
            player[ore] = 0
    if total > 0:
        print(f"You now have {player['GP']} GP!")
    player['load'] = 0
    return total

def main():
    # Main entry point for the game
    # Handles switching between menus and managing game state
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
                    print("-------------------------------------------------------------")
                    print(f"Woo-hoo! Well done, {player['name']}, you have {player['GP']} GP!")
                    print("You now have enough to retire and play video games every day.")
                    print(f"And it only took you {player['day']} days and {player['steps']} steps! You win!")
                    print("-------------------------------------------------------------")
                    save_score()
                    game_state = 'main'
            elif choice == 'v':
                save_game()
            elif choice == 'q':
                game_state = 'main'

# Advanced Feature 1: Input Validation (10 marks)
def get_valid_input(prompt, valid_options):
    # Get input from the player and ensure it is one of the valid options
    # Keeps prompting until valid input is entered
    while True:
        choice = input(prompt).lower()
        if choice in valid_options:
            return choice
        else:
            print(f"Invalid option. Choose from {', '.join(valid_options).upper()}.")

# Advanced Feature 2: Pickaxe Upgrade (10 marks)
def get_pickaxe_level_name(level):
     # Return the mineral type that a given pickaxe level can mine
    return ['None', 'copper', 'silver', 'gold'][level]

def upgrade_pickaxe(player):
    # Upgrade the player's pickaxe to the next level if enough GP is available
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
        print(f"Not enough GP. You need {cost} GP but only have {player['GP']} GP.")

# Advanced Feature 3: Top Scores (5 marks)
def save_score():
     # Save the player's score (name, days, steps, GP) into top 5 scores list
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
       # Display the top 5 scores from the scores.json file
    try:
        with open("scores.json", "r") as f:
            scores = json.load(f)
        print("\nTop 5 Scores:")
        print("-----------------------------")
        for idx, s in enumerate(scores, 1):
            print(f"{idx}. {s['name']} - {s['days']} days, {s['steps']} steps, {s['GP']} GP")
    except FileNotFoundError:
        print("No scores yet.")

if __name__ == "__main__":
    main()









        
           











    




    