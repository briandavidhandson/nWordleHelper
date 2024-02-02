from collections import Counter
import sys
import numpy as np
import random

class ValidWordlist:
    def __init__(self, n_letters=5):
        self.word_length = n_letters
        # Initialize class with list of all valid Wordle answers
        self.valid_words_list = ValidWordlist.load_valid_word_answers()
        
        # list of remaining wordlist size after idx number of guesses
        self.size_wordlist_by_turn = [len(self.valid_words_list)]
        self.game_solved = False

    @staticmethod
    def load_valid_word_guesses():
        
        # load list of valid guesses
        nyt_wordle_guess_filepath = 'wordle_permitted_guesses.txt'
        return ValidWordlist.load_wordlist(nyt_wordle_guess_filepath)

    @staticmethod
    def load_valid_word_answers():
        
        # load list of valid words
        nyt_wordle_answers_filepath = 'NYT_wordle_possibles.txt'
        return ValidWordlist.load_wordlist(nyt_wordle_answers_filepath)
        
        
    @staticmethod
    def load_wordlist(wordlist_filepath):
        # Open and read appropriate wordlist file
        with open(wordlist_filepath, "r", encoding='latin1') as reader:
            wordlist = reader.readlines()
        
        # remove trailing space and linebreak characters from words
        valid_wordlist = [word.strip() for word in wordlist]     
        return valid_wordlist

        
    def filter_wordlist_by_guess_results(self, guess, guess_results):
        # take a guess and its results and filter remaining valid answers
        
        # Mark game as won if every letter is correct
        if guess_results == '22222':
            self.game_solved = True
        # Disregard guess if the game has already been won (default result of guess on a previously won game is '-----')
        if guess_results == '-----':
            guess_letter_idx_results = {}
            
        else:
            
            guess_letter_idx_results = {letter: {score:[] for score in range(3)}
                                                    for letter in set(guess)}
        
            for index, score in enumerate(guess_results):
                guess_letter_idx_results[guess[index]][int(score)].append(index)

        for letter, score_indexes in guess_letter_idx_results.items():

            # the secret_word must contain at least _1 + _2 copies of letter
            letter_count_min = len(score_indexes[1]) + len(score_indexes[2])

            # if _0 is not an empty list
            if score_indexes[0]:
                # secret_word cannot contain more than _1 + _2 copies of letter
                letter_count_max = len(score_indexes[1]) + len(score_indexes[2])
            else:
                # no information on upper bound to letter_count
                letter_count_max = self.word_length

            letter_at_index = score_indexes[2]
            letter_not_at_index = score_indexes[1] + score_indexes[0]

            # pass letter and number-index requirements to filter function
            self.filter_wordlist_by_letter(letter, letter_count_min, letter_count_max,
                                                      letter_at_index, letter_not_at_index)
        
        # Now the wordlist has been filtered by every letter in the guess, add the current size of the wordlist to the turn-by-turn list
        self.size_wordlist_by_turn.append(len(self.valid_words_list))
        
    def filter_wordlist_by_letter(self, letter, count_min, count_max, letter_at_index, letter_not_at_index):
        current_wordlist = [word for word in self.valid_words_list]

        # filter letter minimum
        if count_min != 0:
            current_wordlist = [word for word in current_wordlist
                                if Counter(word)[letter] >= count_min]

        # filter letter maximum
        if count_max != self.word_length:
            current_wordlist = [word for word in current_wordlist
                                if Counter(word)[letter] <= count_max]

        # if at_index isnt emptylist filter at_index
        if letter_at_index:
            for index in letter_at_index:
                current_wordlist = [word for word in current_wordlist
                                    if word[index] == letter]

        # if not_at_index isnt emptylist filter not_at_index
        if letter_not_at_index:
            for index in letter_not_at_index:
                current_wordlist = [word for word in current_wordlist
                                    if word[index] != letter]

        self.valid_words_list = current_wordlist

    def entropy_of_guess(self, guess):
        if self.game_solved:
            return {}
        guess_result_possibilities = {}
        for _word in self.valid_words_list:
            guess_result = score_a_guess(_word ,guess)
            if guess_result_possibilities.get(guess_result):
                guess_result_possibilities[guess_result].append(_word)
            else:
                guess_result_possibilities[guess_result] = [_word]

        return guess_result_possibilities
    

    
class WordHelper:
    def __init__(self, letters=5, parallel_games=4, host_game=False):
        self.parallel_games_dict = {n_game: ValidWordlist(letters)
                                    for n_game in range(parallel_games)}
        if host_game:
            self.secret_words = random.sample(self.parallel_games_dict[0], k=parallel_games)
        else:
            self.secret_words = None
        
        self.valid_guesses = ValidWordlist.load_valid_word_guesses()
        self.guesses_results = {}
        self.update_parallel_wordlist_sizes()
        self.play_game()
        
    def update_parallel_wordlist_sizes(self):
        self.parallel_wordlist_sizes = {n_game: game.size_wordlist_by_turn
                                        for n_game, game in self.parallel_games_dict.items()}
        
    def play_game(self):
        turns = 0
        max_turns = 5 + len(self.parallel_games_dict.keys())
        while any(game.game_solved == False for game in self.parallel_games_dict.values()) and turns < max_turns:
            self.guess_turn(turns)
            turns +=1

        if turns >= max_turns:
            print("You ran out of turns!")
        else:
            print(f"You won in {turns} turns!!")
    
    def guess_turn(self, turn):
        self.display_gamestates()
        guess = input(f'Turn {turn+1}... Input guess: ')
        while guess not in self.valid_guesses:
            guess = input(f'Turn {turn+1}... Please input valid guess: ')
        list_of_results = []
        for n_game, game in self.parallel_games_dict.items():
            if game.game_solved:
                list_of_results.append('-----')
            elif self.secret_words:
                guess_result = score_a_guess(guess,self.secret_words[n_game])
                print(f'Game {n_game} Results:\n{guess.upper()}\n{guess_result}\n')
                list_of_results.append(guess_result)
            else:
                list_of_results.append(input(f"Input results of {guess} in game {n_game}: "))
        self.guesses_results[guess] = tuple(list_of_results)
        self.update_game_guess_and_results()
        
        
        
    def update_game_guess_and_results(self):

        guess, list_of_results = list(self.guesses_results.items())[-1]

        for game, results in zip(self.parallel_games_dict.values(), list_of_results):
            game.filter_wordlist_by_guess_results(guess, results)

        self.update_parallel_wordlist_sizes()

    def display_gamestates(self):

        print('\n')
        known_answers = {n_game: game.valid_words_list[0] for n_game, game in self.parallel_games_dict.items()
                         if (len(game.valid_words_list) == 1) and (not game.game_solved)}
        solved_games = [n_game for n_game, game in self.parallel_games_dict.items()
                         if game.game_solved]

        for n_game in self.parallel_wordlist_sizes.keys():
            print(f'|Game_{n_game}\t words\t bits', end='\t')
        print('')

        for n_game in self.parallel_wordlist_sizes.keys():
            print(f'|------\t-------\t-------', end='\t')
        print('')
        starting_entropy = np.log2(self.parallel_wordlist_sizes[n_game][0])+1

        for n_game in self.parallel_wordlist_sizes.keys():

            print(f'|\t{self.parallel_wordlist_sizes[n_game][0]}',
                  f'{np.round(starting_entropy,2)}',sep='\t', end='\t')
        print('')

        for guess_number, guess in enumerate(self.guesses_results.keys()):
            for n_game in self.parallel_wordlist_sizes.keys():
                guess_entropy = np.log2(
                        self.parallel_wordlist_sizes[n_game][guess_number+1]/self.parallel_wordlist_sizes[n_game][
                            guess_number])


                print(f'| {guess}',
                      f'{self.parallel_wordlist_sizes[n_game][guess_number+1]}',
                      f'{np.round(guess_entropy,2)}',
                      sep='\t',end='\t')
            print('')
        if len(self.guesses_results.keys())> 0:
            for n_game in self.parallel_wordlist_sizes.keys():

                if n_game not in solved_games:
                    remaining_info = np.log2(self.parallel_wordlist_sizes[n_game][-1])+1
                    print(f'|   remaining: \t {np.round(remaining_info,2)}',sep='\t', end='\t')
                else:
                    print(f'|   Solved!\t Yay!', sep='\t', end='\t')
            print('')

            combined_entropy = self.suggest_guess()

            remaining_words = [word for game in self.parallel_games_dict.values()
                                    for word in game.valid_words_list if game.game_solved == False]
            
            top_entropies = [(word,entrop_list) for word,entrop_list in combined_entropy.items()
                             if word not in remaining_words][:6]
            
            candidate_entropy = [(k,v) for k, v in combined_entropy.items() if k in remaining_words][:6]

            priority_entropy = [(k,v) for k, v in combined_entropy.items() if k in known_answers.values()]

            for suggestion, entrop_list in priority_entropy:
                for n_game in self.parallel_wordlist_sizes.keys():
                    if self.parallel_games_dict[n_game].game_solved:
                        print(f'| \t',
                              # f'  ',
                              f'  ',
                              sep='\t', end='\t')
                    else:
                        print(f'|*{suggestion}*',
                            #f'  ',
                            f' ({np.round(entrop_list[n_game], 2)})',
                              sep='\t', end='\t')

                print('')
                
                
            for suggestion, entrop_list in candidate_entropy:
                for n_game in self.parallel_wordlist_sizes.keys():
                    if (self.parallel_games_dict[n_game].game_solved) or (self.parallel_wordlist_sizes[n_game][-1] < 2):
                        print(f'| \t',
                              # f'  ',
                              f'  ',
                              sep='\t', end='\t')
                    else:
                        print(f'|.{suggestion}.',
                            #f'  ',
                            f' ({np.round(entrop_list[n_game], 2)})',
                              sep='\t', end='\t')

                print('')                
                

            for suggestion, entrop_list in top_entropies:
                for n_game in self.parallel_wordlist_sizes.keys():

                    if (not self.parallel_games_dict[n_game].game_solved) and (entrop_list[n_game] > 0):
                        print(f'|({suggestion})',
                              #f'  ',
                              f' ({np.round(entrop_list[n_game], 2)})',
                              sep='\t', end='\t')
                    else:
                        print(f'| \t',
                              #f'  ',
                              f'  ',
                              sep='\t', end='\t')
                print('')

                
    def suggest_guess(self):
        game_entropy_guesses = []

        for game_n, wordlist_n in self.parallel_games_dict.items():
            size_wordlist_n = wordlist_n.size_wordlist_by_turn[-1]
            entropy_dict = {}
            for word in self.valid_guesses:
                if word not in self.guesses_results.keys():
                    word_guess = wordlist_n.entropy_of_guess(word)

                    guess_outcome_dists = {k:len(v) for k,v in word_guess.items()}

                    if word == wordlist_n.valid_words_list[0] and len(wordlist_n.valid_words_list) == 1:
                        guess_entropy = 1
                    elif wordlist_n.game_solved:
                        guess_entropy = 0
                    else:
                        guess_entropy = sum([outcome_count/size_wordlist_n * -np.log2(outcome_count/size_wordlist_n)
                                     for outcome_count in guess_outcome_dists.values()])
                    entropy_dict[word] = np.round(guess_entropy,2)

            game_entropy_guesses.append(dict(sorted(entropy_dict.items(), key=lambda x: x[1], reverse=True)))

        combined_entropy = {}
        for word in game_entropy_guesses[0].keys():
            combined_entropy[word] = tuple(game_ent[word] for game_ent in game_entropy_guesses)
        combined_entropy = dict(sorted(combined_entropy.items(), \
                                       key=lambda x: sum(x[1]), \
                                       reverse=True))
        return combined_entropy


            
def score_a_guess(guess,_word):

    
    # Create a guest score with 2 at index if correct letter and 0 at index if incorrect letter
    guess_score = [2 if guess[i]==_word[i] else 0 for i in range(len(_word))]

    # which guess indexes do not equal 2
    incorrect_indexes = [idx for idx,score in enumerate(guess_score) if score != 2]
    
    # collect the count of letters at incorrect indexes of the guess
    dict_missing_letter_counts = dict(Counter([_word[i] for i in incorrect_indexes]))

    
    for idx in incorrect_indexes:
        if guess[idx] in dict_missing_letter_counts.keys():
            if dict_missing_letter_counts[guess[idx]]>0:
                guess_score[idx]=1
                dict_missing_letter_counts[guess[idx]] -= 1


    guess_score = "".join([str(i) for i in guess_score])
    return guess_score


def main():
    if len(sys.argv) > 1:
        n_games = int(sys.argv[1])
    else:
        n_games = 4
    if 'host' in sys.argv:
        host_game = True
    else:
        host_game = False
    WordHelper(parallel_games=n_games, host_game=host_game)



if __name__ == '__main__':
    main()