import string
import numpy as np
from repositories.trie import trie as default_trie
from repositories.db_utilities import english_dictionary as default_english_dictionary


class SpellCheck:
    """Class provides core functionalities for spellchecking using different algorithms:
    suggesting words generated with a one Damerau-Levenshtein distance, and by
    choosing between different words by calculating Levenshtein distance,
    optimal string alignment distance, and full Damerau-Levenshtein distance.
    """

    def __init__(self, trie=default_trie, dictionary=default_english_dictionary):
        """Method initializes the spell checker, the related trie
            data structure, and the English dictionary

            Args:
                trie (Class, optional): Trie data structure populated with English
                words. Defaults to default_trie.
                dictionary (Class, optional): Class opens data file with English
                dictionary and populates the trie structure. Defaults to default_english_dictionary.
        """

#        print("initializing spell checker")
        self.trie = trie
        self.dictionary = dictionary

    def convert_user_input_as_list(self, user_input):
        """Method converts given user input into a list.

        Args:
             user_input (string): Input is one or multiple words in string format.
        """
        # Need to add separation of commas and points here or somewhere else
        #        print(f"starting to convert user inputs to a list {user_input}")
        user_input_as_list = list(user_input.lower().split())
#        print(user_input_as_list)
        return user_input_as_list

    def is_word_english(self, test_word):
        """Method returns whether the given word is English or not.

           Args:
                test_word (string): Word input by user (string).
            Returns:
                Boolean: Method returns whether the given word is English (True) or not (False).
        """

        return self.trie.search_if_word_in_trie(test_word)

    def alternative_words_with_one_distance(self, test_word):
        """For a given input_word, the method generates all the alternative words that
        are one Damerau-Levenhstein distance away.

        Args:
            input_word (string): A word written by the user (string).
        """

#        print(f"starting to generate alternative words. given word was: {test_word}")
        alternative_words_generated = ""
        alternative_letters = "abcdefghijklmnopqrstuvwxyz"
        split_test_word = [(test_word[:i], test_word[i:])
                           for i in range(len(test_word) + 1)]
#        print(split_test_word)
        deleting_characters = [split_left + split_right[1:]
                               for split_left, split_right in split_test_word if split_right]
#        print(deleting_characters)
        transposing_characters_in_split_words = [split_left + split_right[1] + split_right[0] +
                                                 split_right[2:] for split_left,
                                                 split_right in split_test_word
                                                 if len(split_right) > 1]
#        print(transposing_characters_in_split_words)
        replacing_characters_in_split_words = [split_left + character + split_right[1:]
                                               for split_left, split_right
                                               in split_test_word
                                               if split_right for character in alternative_letters]
#        print(replacing_characters_in_split_words)
        insert_characters_in_split_words = [split_left + character + split_right for split_left,
                                            split_right in split_test_word for character
                                            in alternative_letters]
#        print(insert_characters_in_split_words)

#        print(set(deleting_characters + transposing_characters_in_split_words +
#               replacing_characters_in_split_words + insert_characters_in_split_words))
        alternative_words_generated = set(deleting_characters +
                                          transposing_characters_in_split_words +
                                          replacing_characters_in_split_words +
                                          insert_characters_in_split_words)
#        print(alternative_words_generated)
#        print(len(alternative_words_generated))
        return alternative_words_generated

    def alternative_words_in_english(self, test_word):
        """Method generates alternative words, and returns which ones of them are English.

            Args:
                test_word (string): A word written by the user (string).

            Returns:
                List: Method returns a list of alternative English words
        """
        all_alternative_words = self.alternative_words_with_one_distance(
            test_word)
        alternative_english_words = []

        for word in all_alternative_words:
            if self.trie.search_if_word_in_trie(word) is True:
                alternative_english_words.append(word)

        return alternative_english_words

    def generate_matrix(self, user_word_length, dictionary_word_length):
        """Method generates a distance matrix used when calculating Levenshtein
        distance and optimal string alignment distance

        Args:
            user_word_length (int): Length of the word typed by user
            dictionary_word_length (int): Length of the word taken from dictionary
        """
        baseline_matrix = np.full(
            (user_word_length, dictionary_word_length), user_word_length+dictionary_word_length)
        first_column = np.arange(1, user_word_length+1, 1)
        first_column = first_column.reshape(-1, 1)
        first_row = np.arange(0, dictionary_word_length+1, 1)
        first_row = first_row.reshape(-1, 1)
        first_row = first_row.T
        matrix = np.append(first_column, baseline_matrix, axis=1)
        matrix = np.append(first_row, matrix, axis=0)
    #    print(matrix)
        return matrix

    def generate_damerau_leven_matrix(self, user_word_length, dictionary_word_length):
        """Method generates a distance matrix used when calculating Damerau-Levenshtein
        distance

        Args:
            user_word_length (int): Length of the word typed by user
            dictionary_word_length (int): Length of the word taken from dictionary
        """
    #    print("generating dl matric")

        baseline_matrix = np.full(
            (user_word_length+2, dictionary_word_length+2), user_word_length+dictionary_word_length)
    #    print(baseline_matrix)
        for i in range(1, user_word_length+2):
            baseline_matrix[i][1] = i-1
        for j in range(1, dictionary_word_length+2):
            baseline_matrix[1][j] = j-1
    #    print(baseline_matrix)

        return baseline_matrix

    def cost_heuristic_for_characters(self, character_1, character_2):
        """Method returns heuristic to estimate the distance between
        two characters. At the moment a simplistic approach is used.

        Args:
            character_1 (string): One character
            character_2 (string): One character
        """
    #    print(character_1, character_2)
        if character_1 == character_2:
            return 0
        else:
            return 1

    def calculate_levenshtein_distance(self, user_word, dictionary_word):
        """Method calculates Levenshtein distance between two words, which allows
        insertions, deletions, and symbol substitutions to transform from
        user word to dictionary word. Full matrix is used for illustrative purposes.

        Args:
            user_word (string): Word typed by user
            dictionary_word (string): Word taken from dictionary
        """
    #    print("calculating levenshtein distance, full matrix")
        distance_matrix = self.generate_matrix(
            len(user_word), len(dictionary_word))
    #    print(distance_matrix)

        for i in range(1, len(user_word)+1):
            #        print(f"i is {i}")
            #        print(distance_matrix[i])
            for j in range(1, len(dictionary_word)+1):
                #            print(f"j is {j}")
                #            print(distance_matrix[i][j])
                #            print(user_word[i-1], dictionary_word[j-1])
                distance = self.cost_heuristic_for_characters(
                    user_word[i-1], dictionary_word[j-1])
    #            print(distance)
                distance_matrix[i][j] = min((distance_matrix[i-1][j]+1),
                                            (distance_matrix[i][j-1]+1),
                                            (distance_matrix[i-1][j-1]+distance))

    #    print(distance_matrix)
        shortest_distance = distance_matrix[len(
            user_word), len(dictionary_word)]
    #    print(shortest_distance)
        return shortest_distance

    def calculate_optimal_string_alignment_distance(self, user_word, dictionary_word):
        """Method calculates optimal string alignment distance between two words, which allows
        insertions, deletions, and symbol substitutions to transform from
        user word to dictionary word as well as transposition.
        It does not allow for multiple transformation on the same substring.
        Full matrix is used for illustrative purposes.

        Args:
            user_word (string): Word typed by user
            dictionary_word (string): Word taken from dictionary
        """
    #    print("calculating optimal string alignment distance, full matrix")
        distance_matrix = self.generate_matrix(
            len(user_word), len(dictionary_word))
    #    print(distance_matrix)

        for i in range(1, len(user_word)+1):  # ottaa riveittäin
            #        print(f"i is {i}")
            #        print(distance_matrix[i])
            for j in range(1, len(dictionary_word)+1):
                #            print(f"j is {j}")
                #            print(distance_matrix[i][j])
                #            print(user_word[i-1], dictionary_word[j-1])
                distance = self.cost_heuristic_for_characters(
                    user_word[i-1], dictionary_word[j-1])
    #            print(distance)
                distance_matrix[i][j] = min((distance_matrix[i-1][j]+1),
                                            (distance_matrix[i][j-1]+1),
                                            (distance_matrix[i-1][j-1]+distance))
    #            print(distance_matrix)

                if (i > 1) and (j > 1) and (user_word[i-1] == dictionary_word[j-2]) and (user_word[i-2] == dictionary_word[j-1]):
                    #                print("--transposition identified")
                    distance_matrix[i, j] = min(
                        distance_matrix[i][j], distance_matrix[i-2][j-2]+1)
    #                print(distance_matrix)

    #    print(distance_matrix)
        shortest_distance = distance_matrix[len(
            user_word), len(dictionary_word)]
    #    print(shortest_distance)
        return shortest_distance

    def generate_baseline_row_for_characters(self):
        """Method generates a dictionary that shows for each English character,
        and one symbol ("_") what was the last row in the Damerau-Levenhstein distance
        matrix where it was present.
        """
        baseline_row_for_characters = {}
        characters = string.ascii_lowercase
    #    print(characters)
        for char in characters:
            baseline_row_for_characters[char] = 0
        baseline_row_for_characters["_"] = 0

        return baseline_row_for_characters

    def calculate_damerau_levenshtein_distance(self, user_word, dictionary_word):
        """Method calculates Damerau-Levenshtein distance between two words, which allows
        insertions, deletions, and symbol substitutions to transform from
        user word to dictionary word as well as transposition.
        It also allows for multiple transformation on the same substring.
        Full matrix is used for illustrative purposes.

        Args:
            user_word (string): Word typed by user
            dictionary_word (string): Word taken from dictionary
        """
        distance_matrix = self.generate_damerau_leven_matrix(
            len(user_word), len(dictionary_word))
    #    print(distance_matrix)
        latest_row_for_character = self.generate_baseline_row_for_characters()
    #    for key, value in latest_row_for_character.items():
    #        print(f"{key}: {value}")

        for i in range(2, len(user_word)+2):
            #        print(user_word[i-2])
            latest_column_for_character = 0
            for j in range(2, len(dictionary_word)+2):
                #            print(f"Verrataan kirjaimia: {user_word[i-2]} ja {dictionary_word[j-2]}")
                #            print(user_word[i-2])
                #            print(dictionary_word[j-2])
                last_matching_row = latest_row_for_character[dictionary_word[j-2]]
    #            print(f"last matching row on: {last_matching_row}")
                last_matching_column = latest_column_for_character
    #            print(f"last matching column on: {last_matching_column}")

                if user_word[i-2] == dictionary_word[j-2]:
                    #                print("same character")
                    distance_cost = 0
                    latest_column_for_character = j
                else:
                    distance_cost = 1
    #            print(i, j)

                distance_matrix[i][j] = min(distance_matrix[i-1][j-1]+distance_cost,
                                            distance_matrix[i][j-1]+1,
                                            distance_matrix[i-1][j]+1,
                                            (distance_matrix[last_matching_row-1][last_matching_column-1]
                                            + (i-last_matching_row-1)+(j-last_matching_column-1)+1)
                                            )
    #            print(distance_matrix)

            latest_row_for_character[user_word[i-2]] = i

    #        print(distance_matrix)

        return distance_matrix[-1][-1]
