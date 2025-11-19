import os.path
import random
import sys
from os import name, system, environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # This line hides the pygame prompt when the program start
from words import words
import ascii
try:    # If the user don't have these modules installed, a prompt in their terminal will tell them what's happening
    from pygame import mixer
except ImportError:
    sys.exit("You need pygame!\nInstall it from https://pypi.org/project/pygame/ or run 'pip install pygame'.")
try:
    from prettytable import PrettyTable
except ImportError:
    sys.exit("You need prettytable!\nInstall it from https://pypi.org/project/prettytable/ or run 'pip install prettytable'.")


def clear():
    '''Clear the terminal'''
    if name == "nt":
        return system("cls")
    return system("clear")


def main_menu():
    '''Main menu showed when program start'''
    clear()
    print(ascii.logo)
    print("\n\033[103;34;1m  Welcome to the Hangman game.  \033[0m\n")
    mixer.music.load("music/8bit_touhou_8_love-colored_master_spark.ogg")
    mixer.music.set_volume(0.3)
    if music_on:
        mixer.music.play(loops=-1)
    print("Menu:\n","1. Play","2. Leaderboard","3. Change secret word language","4. Music toggle On/Off","5. Quit", sep="\n", end="\n\n")
    menu = {1: main, 2: leaderboard, 3: set_language, 4: toggle_music, 5: quit}
    menu_option = input("Choose an option from the menu (1-5): ")
    valid_options = [str(i) for i in range(1, len(menu)+1)]
    while menu_option not in valid_options:
        main_menu()
    toggle_music(menu_option) # Toggle music if input is "4"
    if menu_option == "1": # Change track, then play it if music is not toggled off
        mixer.music.load("music/8bit_welcome_space_traveler.ogg")
        mixer.music.set_volume(0.6)
        if music_on:
            mixer.music.play(loops=-1)
    else:
        mixer.music.stop() # Stop music before changing mode, so it won't play outside the menu
    return menu[int(menu_option)]()


def toggle_music(menu_option):
    global music_on
    #If music is off
    if menu_option == "4" and not mixer.music.get_busy() or menu_option == "togglem" and not mixer.music.get_busy():
        mixer.music.play(loops=-1)
        music_on = True
        if menu_option == "4":
            main_menu()
    #Else if music is on
    elif menu_option == "4" and mixer.music.get_busy() or menu_option == "togglem" and mixer.music.get_busy():
        mixer.music.stop()
        music_on = False
        if menu_option == "4":
            main_menu()


def game_interface(player_lives, blank, guessed):
    '''Take the game session information and print them in the terminal in a way to show the player all the data he need'''
    print("\033[107;31mType 'menu' to return to main menu or 'togglem' to toggle the music.\033[0m\n\n")
    print(f"\033[103;34m  Lives left: {player_lives}  \033[0m", f"\033[103;34m  Word Language: {language}  \033[0m\n", sep="\t")
    print(ascii.stages[player_lives])
    print("   ","\033[32;1m", *blank, "\033[0m") # Print the list of underscores/guessed letters
    print(f"\nGuessed letters: ", *guessed) # Print the list of guessed letters


def quit_or_menu():
    '''After a game over, check if user want to replay, go back to main menu or quit the program'''
    check_quit = input("\033[107;31mType 'r' to play again, 'm' to return to main menu or 'q' to quit the game:\033[0m ").lower()
    option = {"r": main, "m": main_menu, "q": quit}
    while check_quit not in option:
        check_quit = input("\n\033[107;31mIncorrect input.\nType 'r' to play again, 'm' to return to main menu or 'q' to quit the game:\033[0m ").lower()
    return option[check_quit]()


def check_input():
    '''Asks for an input then check if it's a valid one.'''
    player_guess = input(f"\nGuess a letter: ").lower()
    # player_guess = input(f"\nGuess a letter ({word}): ").lower() # Enable this line for debugging purpouse, it shows the secret word in the prompt
    while len(player_guess) > 1 and player_guess != "menu" and len(player_guess) > 1 and player_guess != "togglem" or not player_guess.isalpha():
        clear()
        game_interface(player_lives, blank, guessed)
        player_guess = input("\n\nIncorrect input. Guess a letter: ").lower()
    if player_guess == "menu":
        main_menu()
    return player_guess


def main():
    clear()
    global word, blank, player_lives, guessed, wins, losses, matches
    word = random.choice(words[init_language]["words"])
    blank = ["_" for i in word]
    player_lives = 6
    guessed = []
    game_interface(player_lives, blank, guessed)
    print()
    while True:
        player_guess = check_input()
        while player_guess in guessed:
            clear()
            game_interface(player_lives, blank, guessed)
            if player_guess in word:
                print(f"You already guessed the letter '{player_guess.lower()}'")
                player_guess = check_input()
            else:
                print(f"You already guessed the letter '{player_guess.lower()}', also it's wrong.")
                player_guess = check_input()
        if player_guess == "togglem":
            toggle_music(player_guess)
            clear()
            game_interface(player_lives, blank, guessed)
            print()
        else:
            guessed.append(player_guess) # The valid input can now be appended to the guessed list

            if player_guess not in word:
                player_lives -= 1
                if player_lives < 1:
                    clear()
                    game_interface(player_lives, blank, guessed)
                    print("\n\033[101;97mGame over, you lost.\033[0m")
                    losses += 1
                    matches += 1
                    leaderboard_update()
                    quit_or_menu()
                else:
                    clear()
                    game_interface(player_lives, blank, guessed)
                    print("\033[101;97mWrong. You lose a life.\033[0m")
            else:
                for i in range(len(word)):
                    if player_guess == word[i]:
                        blank[i] = player_guess
                    clear()
                    game_interface(player_lives, blank, guessed)
                    print("\033[102;90mCorrect.\033[0m")
                if "_" not in blank: # If every letter of the word is correctly guessed
                    clear()
                    game_interface(player_lives, blank, guessed)
                    print("\n\033[102;90mGame over, you win!\033[0m")
                    wins += 1
                    matches += 1
                    leaderboard_update()
                    quit_or_menu()


# Leaderboard Section
def leaderboard_load():
    global player, wins, losses, matches, win_ratio, language
    if os.path.exists("leaderboard.txt"):
        f = open("leaderboard.txt")
    else:
        f = leaderboard_init()
    lines = f.readlines()
    player = lines[1]
    wins = int(lines[2])
    losses = int(lines[3])
    matches = int(lines[4])
    language = words[lines[5]]["lang"]
    win_ratio = f"{round(wins*100/matches, 2) if matches else 0}%"


def leaderboard_init():
    '''Reset "leaderboard.txt" to its initial state and create it if not present'''
    f = open("leaderboard.txt", "w")
    f.write(f"#Don't modify this file or the leaderboard wouldn't work how supposed to. If the program crashes because of this file, delete it and it will reset.\n{'Player1'}\n{0}\n{0}\n{0}\n{'eng'}")
    f.close()
    leaderboard_load()
    return open("leaderboard.txt")


def leaderboard():
    clear()
    leaderboard_load()
    table = PrettyTable()
    table.field_names = ["Player", "Win", "Loss", "Match Played", "Win Ratio"]
    table.add_row([player, wins, losses, matches, win_ratio])
    print(table)
    if input("\nPress Enter to go back to main menu, or type 'res' to reset the leaderboard: ") == "res".lower():
        leaderboard_init()
        leaderboard()
    main_menu()


def leaderboard_update():
    with open("leaderboard.txt", "w") as update:
        update.write(f"#Don't modify this file or the leaderboard wouldn't work how supposed to. If the program crashes because of this file, delete it and it will reset.\nPlayer1\n{wins}\n{losses}\n{matches}\n{init_language}")
        update.close()


# Language Section
def set_language():
    global language, init_language
    clear()
    init_language = input("Which language do you want the secret word to be? Type 'eng' or 'ita': ").lower()
    allowed_input = ["ita", "eng"]
    while init_language not in allowed_input:
        set_language()
    language = words[init_language]["lang"]
    print(language)
    input("\nChanges applied. Press Enter.")
    leaderboard_update()
    main_menu()


# Main Program
wins: int
losses: int
matches: int
leaderboard_load()
mixer.init()
mixer.music.set_volume(0.3)
music_on = True
with open("leaderboard.txt") as lang:
    lines = lang.readlines()
    init_language = lines[5]
language = words[init_language]["lang"]
main_menu()
