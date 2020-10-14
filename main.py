import random
import pandas as pd
import numpy as np
from words import word_list
from time import perf_counter
from datetime import datetime, date

lb = pd.read_excel('leaderboard.xlsx')
db = pd.read_excel('database.xlsx')


def get_word():
    word = random.choice(word_list)
    return word.upper()


def play(word):
    word_completion = "_" * len(word)
    guessed = False
    guessed_letters = []
    guessed_words = []
    tries = 6
    print("Let's play Hangman!")
    print(display_hangman(tries))
    print(word_completion)
    print("\n")
    t1_start = perf_counter()
    while not guessed and tries > 0:
        guess = input("Please guess a letter or word: ").upper()
        if len(guess) == 1 and guess.isalpha():
            if guess in guessed_letters:
                print("You already guessed the letter", guess)
            elif guess not in word:
                print(guess, "is not in the word.")
                tries -= 1
                guessed_letters.append(guess)
            else:
                print("Good job,", guess, "is in the word!")
                guessed_letters.append(guess)
                word_as_list = list(word_completion)
                indices = [i for i, letter in enumerate(word) if letter == guess]
                for index in indices:
                    word_as_list[index] = guess
                word_completion = "".join(word_as_list)
                if "_" not in word_completion:
                    guessed = True
        elif len(guess) == len(word) and guess.isalpha():
            if guess in guessed_words:
                print("You already guessed the word", guess)
            elif guess != word:
                print(guess, "is not the word.")
                tries -= 1
                guessed_words.append(guess)
            else:
                guessed = True
                word_completion = word
        else:
            print("Not a valid guess.")
        print(display_hangman(tries))
        print(word_completion)
        print("\n")
    if guessed:
        print("Congrats, you guessed the word! You win!")
        score = tries
        t1_stop = perf_counter()
        ttt = t1_stop - t1_start
        score_time = [score, ttt]
        return score_time
    else:
        print("Sorry, you ran out of tries. The word was " + word + ". Maybe next time!")
        t1_stop = perf_counter()
        ttt = t1_stop - t1_start
        score = 0
        score_time = [score, ttt]
        return score_time


def display_hangman(tries):
    stages = [  # final state: head, torso, both arms, and both legs
        """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / \\
                   -
                """,
        # head, torso, both arms, and one leg
        """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / 
                   -
                """,
        # head, torso, and both arms
        """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |      
                   -
                """,
        # head, torso, and one arm
        """
                   --------
                   |      |
                   |      O
                   |     \\|
                   |      |
                   |     
                   -
                """,
        # head and torso
        """
                   --------
                   |      |
                   |      O
                   |      |
                   |      |
                   |     
                   -
                """,
        # head
        """
                   --------
                   |      |
                   |      O
                   |    
                   |      
                   |     
                   -
                """,
        # initial empty state
        """
                   --------
                   |      |
                   |      
                   |    
                   |      
                   |     
                   -
                """
    ]
    return stages[tries]


def check_user(s):
    for x in lb["Player Name"]:
        if x == s:
            return True
    else:
        return False


def write_to_excel(o, p):
    writer = pd.ExcelWriter(p, engine='xlsxwriter')
    o.to_excel(writer, index=False)
    writer.save()


def main():
    row_count = 0
    word = get_word()
    username = input("Enter your name:")
    name = username.upper()
    if lb.shape[0] == db.shape[0]:
        row_count = lb.shape[0]
    else:
        print("Database-Leaderboard not synced")
    score, ttt = play(word)
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

    if check_user(name):  # existing user
        m = db[db['Player Name'] == name].index.values  # get index
        tgp = db.at[int(m), 'Total Games Played'] + 1  # total games played
        st = db.at[int(m), 'Start Time']  # retain values of start time
        sd = db.at[int(m), 'Start Date']  # and date
        if score > 0:
            gw = db.at[int(m), 'Games Won'] + 1  # games won
        else:
            gw = db.at[int(m), 'Games Won']
        db.loc[m] = [m, name, tgp, gw, st, sd]
        print(db)
        wp = (gw * 100) / tgp  # win percentage
        updated_score = lb.at[int(m), 'Score'] + score
        updated_ttt = lb.at[int(m), 'Total Time Taken for completion'] + ttt
        lb.loc[m] = [m, name, wp, updated_score, updated_ttt]
        lb.sort_values(['Win Percentage', 'Score', 'Total Time Taken for completion'],
                       ascending=[False, False, True], inplace=True)
        print(lb)
        write_to_excel(lb, "leaderboard.xlsx")
        write_to_excel(db, "database.xlsx")
    else:  # new user
        if score > 0:
            wp = 100  # win percent
            gw = 1  # games won
        else:
            wp = 0
            gw = 0
        start_date = date.today()
        start_time = datetime.now().time()
        lb2 = pd.DataFrame([[row_count, name, wp, score, ttt]],  # new entry in the db
                           columns=['Sl No', 'Player Name', 'Win Percentage',
                                    'Score', 'Total Time Taken for completion'])
        db2 = pd.DataFrame([[row_count, name, 1, gw, start_time, start_date]],  # new entry in the db
                           columns=['Sl No', 'Player Name', 'Total Games Played', 'Games Won', 'Start Time',
                                    'Start Date'])
        df = lb.append(lb2, ignore_index=True)
        df2 = db.append(db2, ignore_index=True)
        df.sort_values(['Win Percentage', 'Score', 'Total Time Taken for completion'],
                       ascending=[False, False, True], inplace=True)
        print(df)
        print(df2)
        write_to_excel(df, "leaderboard.xlsx")
        write_to_excel(df2, "database.xlsx")

    """
    while input("Play Again? (Y/N) ").upper() == "Y":
        word = get_word()
        result = play(word)
        print(result)
    """


if __name__ == "__main__":
    main()
