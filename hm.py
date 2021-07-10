#!/usr/bin/python -tt

import sys
from sage.all import *
import random


#################
### Constants ###
#################


EPS = 10**(-10)


############
### Main ###
############


def main():
    pass


#################
### Functions ###
#################
# find_nash_equilibrium(word_set)
# prob_guesser_wins(guesser_strategy, picker_strategy, num_guesses, word_set=None)


def find_nash_equilibrium(word_set):
    pass


def prob_guesser_wins(guesser_strategy, picker_strategy, num_guesses, word_set=None):
    if word_set is None:
        word_set = set(picker_strategy) # this is a set of the keys

    mixed_gamestate = MixedGamestate({PureGamestate(word_set=word_set, secret_word=word, guesses_remaining=num_guesses):picker_strategy[word] for word in picker_strategy})
    EV = 0.0
    while mixed_gamestate:
        # update the remaining branches
        mixed_gamestate.apply_guesser_strategy(guesser_strategy)
        mixed_gamestate.clean()

        # prune the branches that have concluded
        for pure_gamestate in mixed_gamestate:
            if pure_gamestate.winner() == 'guesser':
                EV += mixed_gamestate[pure_gamestate]
        mixed_gamestate.remove_finished_games()
        # Important to not normalize

    return EV


def get_possible_subwords(word):
    '''
    returns a set of strings with '_' denoting unknown letters, and never only some copies of a given letter known,
    e.g. get_possible_subwords('jazz') = {'____', 'j___', '_a__', '__zz', 'ja__', '_azz', 'j_zz', 'jazz'}
    '''
    letters_in_word = frozenset(word)
    to_ret = {word}
    to_check = {(word,letters_in_word)}
    while to_check:
        (subword, letters_in_subword) = to_check.pop()
        for letter in letters_in_subword:
            if letter != '_':
                new_subword = subword.replace(letter,'_')
                letters_in_new_subword = set(letters_in_subword)
                letters_in_new_subword.remove(letter)
                to_ret.add(new_subword)
                to_check.add((new_subword,frozenset(letters_in_new_subword)))
    return to_ret


def get_most_common_words(filename='10kmostcommonwords'):
    most_common_word_dict = {}
    f = open(filename,'r')
    for line in f:
        line = line.replace('\n','')
        word_len = len(line)
        if word_len not in most_common_word_dict:
            most_common_word_dict[word_len] = []
        most_common_word_dict[word_len].append(line)
    f.close()
    return most_common_word_dict



###############
### Classes ###
###############
# PDF(dict)
# GuesserStrategy(dict)
# PickerStrategy(PDF)
# PureGamestate(word_set=set(), secret_word='', guesses_remaining=0)
# MixedGamestate(PDF)


class PDF(dict):
    #def __init__(self, probabilities={}):
    #    for key in probabilities:
    #        self[key] = probabilities[key]


    def __repr__(self):
        to_ret = str(self)
        return to_ret


    def copy(self):
        new_pdf = PDF(self)
        return new_pdf


    def set_dict(self, new_dict):
        to_del = set(self)
        for key in self:
            del self[key]

        for key in new_dict:
            self[key] = new_dict[key]

    
    def is_valid(self):
        prob_sum = self.probability_sum()
        prob_sum_condition = (abs(prob_sum - 1) < EPS)
        to_ret = prob_sum_condition
        return prob_sum_condition


    def make_valid(self, in_place=True):
        return self.normalize(in_place=in_place)
    
    
    def normalize(self, in_place=True):
        if not in_place:
            new_pdf = self.copy()
            new_pdf.normalize()
            return new_pdf
        else:
            prob_sum = self.probability_sum()
            if prob_sum < EPS:
                raise ValueError
            for key in self:
                self[key] /= prob_sum
            #return None # I don't know if I need this


    def clean(self, in_place=True):
        '''
        remove entries which have prob 0
        '''
        if not in_place:
            new_pdf = self.copy()
            new_pdf.clean()
            return new_pdf
        else:
            to_del = set()
            for key in self:
                prob = self[key]
                if prob < EPS:
                    to_del.add(key)
            for key in to_del:
                del self[key]
        

    def probability_sum(self):
        prob_sum = 0.0
        for key in self:
            prob_sum += self[key]
        return prob_sum

    

class GuesserStrategy(dict):
    '''
    dict of {possible_gamestates.visible_only(): PDF with letters as keys}
    '''
    
    #def __init__(self, strategy={}):
    #    for key in strategy:
    #        self[key] = strategy[key]


    def __repr__(self):
        return str(self)


    def copy(self):
        new_guesser_strategy = GuesserStrategy(self)
        return new_guesser_strategy


    def is_valid(self, word_set=None):
        key_condition = True
        if word_set is not None:
            # possible_gamestates = get_possible_gamestates(word_set)
            # key_condition = possible_gamestates.issubset(self)
            pass
        val_condition = True
        for key in self:
            pdf_condition = self[key].is_valid()
            if not pdf_condition:
                val_condition = False
                break
        to_ret = key_condition and val_condition
        return to_ret

        
    def EV_vs_picker_strategy(self, picker_strategy, num_guesses, word_set=None):
        EV = prob_guesser_wins(self, picker_strategy, num_guesses, word_set=word_set)
        return EV
        


class WordSet(set):
    def copy(self):
        new_word_set = WordSet(self)
        return new_word_set


    def is_valid(self):
        length_condition = (len({len(word) for word in self}) <= 1)
        return length_condition
    
    
    def remove_letter(self, letter, in_place=True):
        '''
        Removes all words in self which contain letter
        '''
        if not in_place:
            new_word_set = self.copy()
            new_word_set.remove_letter(letter)
            return new_word_set
        else:
            to_del = set()
            for word in self:
                if letter in word:
                    to_del.add(word)
            self.difference_update(to_del)
    
    
    def require_letter(self, letter, positions, exact=True, in_place=True):
        '''
        Removes all words in self which don't contain letter at all positions.
        If exact, also removes words that have letter at a position not in positions.
        '''
        if not in_place:
            new_word_set = self.copy()
            new_word_set.require_letter(letter, positions)
            return new_word_set
        else:
            to_del = set()
            for word in self:
                if not exact:
                    for pos in positions:
                        if word[pos] != letter:
                            to_del.add(word)
                            break
                else:
                    for pos in range(len(word)):
                        if pos in positions:
                            if word[pos] != letter:
                                to_del.add(word)
                                break
                        else:
                            if word[pos] == letter:
                                to_del.add(word)
                                break
            self.difference_update(to_del)
        
    
    def get_possible_guesses(self):
        '''
        Returns all letters which are at a position in one word of self and not at that same position in another word of self.
        For example,
        WordSet(['ab','cd']).get_possible_guesses() == {'a', 'b', 'c', 'd'}
        WordSet(['ab','ac']).get_possible_guesses() == {'b', 'c'}
        WordSet(['ab','ca']).get_possible_guesses() == {'a', 'b', 'c'}
        '''
        # this can probably be made way faster
        letters_by_position = {}
        possible_guesses = set()
        for word in self:
            for pos in range(len(word)):
                letter = word[pos]
                # this try -> except is probably faster than checking each time
                try:
                    if letter not in letters_by_position[pos]:
                        letters_by_position[pos].add(letter)
                        possible_guesses.update(letters_by_position[pos])
                except KeyError:
                    letters_by_position[pos] = {letter}
        return possible_guesses
    
    
    def get_possible_visible_wordsets(self, nontrivial_only=True, validate=True):
        '''
        Returns all subsets of self which are consistent with some sequence of hangman guesses.
        If nontrivial_only, returns only subsets of size 2 or more.
        '''
        # inefficient
        if validate:
            all_same_length = self.is_valid()
            if not all_same_length:
                raise ValueError
        
        possible_subwords = set()
        for word in self:
            possible_subwords.update(get_possible_subwords(word))
        
        frozen_word_sets = set()
        for subword in possible_subwords:
            new_wordset = self.copy()
            for letter in set(subword):
                if letter != '_':
                    positions = {i for i in range(len(subword)) if subword[i] == letter}
                    new_wordset.require_letter(letter, positions)
            if (len(new_wordset) > 1) or (not nontrivial_only):
                frozen_word_sets.add(frozenset(new_wordset))

        to_ret = [] # WordSet is unhashable
        for frozen_ws in frozen_word_sets:
            to_ret.append(WordSet(frozen_ws))
        
        return to_ret
        

        

    
class PickerStrategy(PDF):
    '''
    PDF with word_set keys
    '''

    def is_valid(self, word_set=None):
        pdf_condition = super(PickerStrategy, self).is_valid()
        if word_set is not None:
            all_words_in_strategy = True
            for word in word_set:
                if word not in self:
                    all_words_in_strategy = False
                    break
        to_ret = pdf_condition and all_words_in_strategy
        return to_ret

    
    def EV_vs_guesser_strategy(self, guesser_strategy, num_guesses, word_set=None):
        EV = 1.0 - prob_guesser_wins(guesser_strategy, self, num_guesses, word_set=word_set)
        return EV
    


class PureGamestate:
    # Should PureGamestate extend WordSet instead?
    # remove_letter, require_letter, and get_possible_guesses just call the WordSet methods, so it'd make sense to me to just inherit those methods, but
    # 1. this class "doesn't feel like" it's just WordSet with extra stuff, and
    # 2. __init__ is kind of confusing for me if I extent WordSet, since I wouldn't be sure how to pass the set of words properly.
    
    def __init__(self, word_set=WordSet(), secret_word='', guesses_remaining=0):
        self.word_set = word_set
        self.secret_word = secret_word
        self.guesses_remaining = guesses_remaining

        
    def __repr__(self):
        word_set_str = 'word_set: '+str(self.word_set)
        secret_word_str = 'secret_word: '+str(self.secret_word)
        guesses_remaining_str = 'guesses_remaining: '+str(self.guesses_remaining)
        to_ret = word_set_str + '\n' + secret_word_str + '\n' + guesses_remaining_str
        return to_ret


    def copy(self):
        new_gamestate = Gamestate(self.word_set, self.secret_word, self.guesses_remaining)
        return new_gamestate


    def is_valid(self):
        word_condition = (self.secret_word in self.word_set)
        guess_condition = (self.guesses_remaining >= 0)
        length_condition = self.word_set.is_valid()
        to_ret = word_condition and guess_condition and length_condition
        return to_ret
    
        
    def make_guess(self, letter, in_place=True):
        if not in_place:
            new_gamestate = self.copy()
            new_gamestate.make_guess(letter)
            return new_gamestate
        else:
            if letter not in self.secret_word:
                self.guesses_remaining -= 1
                self.remove_letter(letter)
            else:
                positions = set()
                for pos in range(len(self.secret_word)):
                    if self.secret_word[pos] == letter:
                        positions.add(pos)
                self.require_letter(letter, positions)        

    
    def remove_letter(self, letter, in_place=True):
        if not in_place:
            new_pure_gamestate = self.copy()
            new_pure_gamestate.remove_letter(letter)
            return new_pure_gamestate
        else:
            self.word_set.remove_letter(letter)

    
    def require_letter(self, letter, positions, in_place=True):
        if not in_place:
            new_pure_gamestate = self.copy()
            new_pure_gamestate.require_letter(letter, posiitons)
            return new_pure_gamestate
        else:
            self.word_set.require_letter(letter, positions)
        

    def get_possible_guesses(self):
        to_ret = self.word_set.get_possible_guesses()
        return to_ret

    
    def winner(self):
        '''
        returns either 'picker', 'guesser', or None
        '''
        no_guesses = (self.guesses_remaining < 1)
        found_word = (len(self.word_set) <= 1)
        if no_guesses and found_word:
            raise ValueError
        if no_guesses:
            return 'picker'
        elif found_word:
            return 'guesser'
        else:
            return None


    def visible_only(self):
        return (self.word_set, self.guesses_remaining)


    def get_possible_visible_gamestates(self, nontrivial_only=True, validate=True):
        possible_visible_wordsets = self.word_set.get_possible_visible_wordsets(nontrivial_only=nontrivial_only, validate=validate)
        if nontrivial_only:
            possible_guesses_remaining = list(range(1,self.guesses_remaining+1))
        else:
            possible_guesses_remaining = list(range(self.guesses_remaining+1))
        to_ret = [(pws, pg) for pws in possible_visible_wordsets for pg in possible_guesses_remaining]
        return to_ret



class MixedGamestate(PDF):
    '''
    PDF + PureGamestate methods
    '''

    def is_valid(self):
        pdf_condition = super(MixedGamestate, self).is_valid()
        key_condition = True
        for key in self:
            tmp_instance_condition = isinstance(key, PureGamestate)
            if not tmp_instance_condition:
                key_condition = False
                break
            else:
                if not key.is_valid():
                    key_condition = False
                    break
        to_ret = pdf_condition and key_condition
        return to_ret
    
        
    def make_guess(self, letter, clean_dict=False, in_place=True):
        if not in_place:
            new_mixed_gamestate = self.copy()
            new_mixed_gamestate.make_guess(letter, clean_dict=clean_dict)
            return new_mixed_gamestate
        else:
            if clean_dict:
                self.clean()
            for pure_gamestate in self.gamestate_dict:
                pure_gamestate.make_guess(letter)


    def remove_finished_games(self, in_place=True):
        if not in_place:
            new_mixed_gamestate = self.copy()
            new_mixed_gamestate.remove_finished_games()
            return new_mixed_gamestate
        else:
            to_del = set()
            for pure_gamestate in self:
                if pure_gamestate.winner:
                    to_del.add(pure_gamestate)
            for pure_gamestate in to_del:
                del self[pure_gamestate]


    def apply_guesser_strategy(self, guesser_strategy, in_place=True):
        if not in_place:
            new_mixed_gamestate = self.copy()
            new_mixed_gamestate.apply_guesser_strategy(guesser_strategy)
            return new_mixed_gamestate
        else:
            new_gamestate = {}
            for pure_gamestate in self:
                pure_gamestate_prob = self[pure_gamestate]
                letter_guess_probs = guesser_strategy[pure_gamestate.visible_only()]
                for letter in letter_guess_probs:
                    letter_prob = letter_guess_probs[letter]
                    pure_gamestate_after_guess = pure_gamestate.make_guess(letter, in_place=False)
                    if pure_gamestate_after_guess in new_gamestate:
                        new_gamestate[pure_gamestate_after_guess] += pure_gamestate_prob * letter_prob
                    else:
                        new_gamestate[pure_gamestate_after_guess] = pure_gamestate_prob * letter_prob
            self.set_dict(new_gamestate)


        

    
#This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    if '-profile' in sys.argv:
        cProfile.run('main()')
    else:
        main()
