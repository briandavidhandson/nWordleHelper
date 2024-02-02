# nWordleHelper
An assistant for solving N parallel simultaneous Wordle games

Wordle is a popular online word game (Run by the New York Times) which involves guessing a secret 5-letter word. 
https://www.nytimes.com/2023/08/01/crosswords/how-to-talk-about-wordle.html

Each turn the player guesses a 5-letter word and the results of the guess are revealed to the player.

Each letter in the guess is given a score of 2, 1, or 0 (or a color of green, yellow, or gray in fancy web applications)

For example the guess ATONE for the secret word CRATE will give a result '11002':
A - 1 (Yellow)   (There is an A in CRATE, but not at the first letter)
T - 1 (Yellow)   (There is a T in CRATE, but not at the second letter)
O - 0 (Grey)     (There is no O in CRATE)
N - 0 (Grey)     (There is no N in CRATE)
E - 2 (Green)    (There is an E in CRATE at the fifth letter)

There are numerous spinoffs of Wordle that feature N parallel games of Wordle.
N     Name        URL
1     Wordle      https://www.nytimes.com/games/wordle/index.html
2     Dordle      https://zaratustra.itch.io/dordle
3     Trordle     https://diablomono.itch.io/trordle
4     Quordle     https://www.quordle.com/#/
6     Hexordle    https://hexordle.com/
8     Octordle    https://octordle.com/
10    Decordle    https://www.opensourcefeed.org/puzzles/decordle/
16    Sedecordle  http://www.sedecordle.com/

Each Parallel game has a different secret word.

Each turn the player has one guess to try with every parallel game.

The player receives a different result for the guess from each parallel game.

# Dependencies

Numpy

# Commands

```python

# Start game with N=4 (defaults to Quordle)
python3 nWordleHelper

# Start game with N=6
python3 nWordleHelper 6

# Start game with N=1
python3 nWordleHelper 1

# Start game with N=4, program picks secret letters
python3 nWordleHelper host

```


# Interface

Each parallel game will appear in a column.
Each column will list the guesses made so far, how many valid answers remain after each guess, the entropy remaining (log-base2 of  valid answer count + 1). 
Guesses will also list how much entropy they removed from each parallel game (more is better, an entropy of 0 means you have won the sub-game)

Suggested guesses are listed beneath, ordered by how much total entropy they are expected to decrease across all parallel sub-games.

Suggested guesses are surrounded by three types of punctuation:
asterisks mean the suggested guess must be the secret word of one of the parallel sub-games
periods mean the suggested guess may still be a secred word of one of the parallel sub-games
parentheses mean the suggested guess is not any of the secret words, but still has a large expected entropy decrease.

The User Interface for hosted games (where the program picks the secret letters) is not developed and is not as easy to play as free web applications available. It is recommended to use this program as an assistant while playing a web application and manually entering the results of each guess.

# Acknowledgements

This algorithm was inspired by the 3Blue1Brown analysis of Wordle (https://www.youtube.com/watch?v=v68zYyaEmEA). 
