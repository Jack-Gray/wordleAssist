import re
import string

import enchant.checker


def string_logical_or(first_string, second_string, null_char=''):
    char_results = []
    overlap = False
    if len(first_string) != len(second_string):
        raise ValueError("input strings cannot have different lengths")
    if len(null_char) > 1:
        raise ValueError("null_char must be of length 1 or 0")
    for first_value, second_value in zip(first_string, second_string):
        if first_value == null_char:
            char_results.append(second_value)
        else:
            if not (first_value == second_value or second_value == null_char):
                overlap = True
            char_results.append(first_value)
    return ''.join(char_results), overlap


def findOccurrences(input_string, character):
    return {i for i, letter in enumerate(input_string) if letter == character}


# TODO: Allow a choice between standard input and regex
def get_patterns():
    cont = True
    patterns = []
    print("Enter a pattern for each known letter below, one at a time. Use underscores for unknown letters.")
    while cont:
        pattern = input("Enter a pattern or hit enter to finish: ")
        if pattern == "":
            cont = False
        else:
            patterns.append(pattern)
    return patterns


# TODO: Refactor to reduce complexity
def optimize_patterns(constraints):
    optimized_patterns = []
    unknown_letter_patterns = []
    new_pattern = "_____"

    # split constraints into knowns and unknowns
    knowns = {}
    unknowns = {}
    for letter in constraints:
        if len(constraints[letter]) == 1:
            knowns[letter] = constraints[letter]
        else:
            unknowns[letter] = constraints[letter]

    # set known letters
    for letter in knowns:
        index = knowns[letter][0]
        new_pattern = new_pattern[:index] + letter + new_pattern[index + 1:]

    # populate with unknown position letters
    for letter in unknowns:
        single_unknown_letter_patterns = []
        for index in unknowns[letter]:
            if new_pattern[index] == "_":
                single_unknown_letter_patterns.append(new_pattern[:index] + letter + new_pattern[index + 1:])
        optimized_patterns += single_unknown_letter_patterns
        unknown_letter_patterns.append(single_unknown_letter_patterns)

    # if more than one unknown was used, make new_patterns representing all possible combinations
    if len(unknowns) > 1:
        optimized_patterns.clear()
        detailed_unknown_letter_patterns = []
        while len(unknown_letter_patterns) >= 2:
            detailed_unknown_letter_patterns.clear()
            first_list = unknown_letter_patterns.pop()
            second_list = unknown_letter_patterns.pop()
            for first_pattern in first_list:
                for second_pattern in second_list:
                    pattern = string_logical_or(first_pattern, second_pattern, '_')
                    if not pattern[1]:
                        detailed_unknown_letter_patterns.append(pattern[0])
            unknown_letter_patterns.append(detailed_unknown_letter_patterns.copy())
        optimized_patterns += detailed_unknown_letter_patterns

    # check if a new pattern has been appended (won't have been if only knowns were used)
    if len(optimized_patterns) == 0:
        optimized_patterns.append(new_pattern)

    return optimized_patterns


def get_constraints(patterns):
    constraints = {}
    for pattern in patterns:
        for i in range(len(pattern)):
            char = pattern[i]
            if char != "_":
                if char not in constraints:
                    constraints[char] = {i}
                else:
                    constraints[char].add(i)
    return constraints


def create_words():
    file = None
    if filename is not None:
        file = open(filename, "w")

    checker = enchant.checker.SpellChecker("en_US")
    patterns = get_patterns()

    # return a dict of every required letter mapped to its possible locations
    constraints = get_constraints(patterns)
    patterns = optimize_patterns(constraints)
    print("Optimized patterns created: " + ', '.join(patterns))
    all_letters = string.ascii_lowercase
    bad_letters = input("Enter all the letters that cannot be used: ")
    good_letters = list(set(all_letters).symmetric_difference(bad_letters))
    good_letters.sort()
    words = []
    for pattern in patterns:
        working_words = [pattern]
        while len(working_words) > 0:
            working_word = working_words.pop(0)
            created_words = []
            index = working_word.find("_")
            if index != -1:
                for letter in good_letters:
                    new_word = working_word[:index] + letter + working_word[index + 1:]
                    created_words.append(new_word)
            for word in created_words:
                if "_" not in word:
                    if checker.check(word):
                        satisfies_constraints = True
                        for letter in constraints:
                            pos = []
                            for iteration in re.finditer(letter, word):
                                pos.append(iteration.regs[0][0])
                            if len(set(constraints[letter]).intersection(pos)) == 0:
                                satisfies_constraints = False
                        if satisfies_constraints:
                            print("word found: " + word)
                            if file is not None:
                                file.write(word + "\n")
                            words.append(word)
                else:
                    working_words.append(word)
    return words


if __name__ == '__main__':
    print("Welcome to the wordle assist tool!")
    print("This tool will not solve the word for you, it will only help to visualize letter patterns")
    finished = False
    while not finished:
        if input("Would you like to receive results in a file? (y/n) ").lower() == "y":
            filename = input("Enter the name of the file you would like the results in: ")
            create_words()
        else:
            filename = None
            print(create_words())
        finished = True if input("Continue (y/n): ").lower() == "n" else False
