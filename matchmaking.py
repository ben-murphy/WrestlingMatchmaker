import sys
import re

from typing import List

# The indices of the columns that contain certain values
SKILL_LEVEL = 10
FIRST_NAME = 2
LAST_NAME = 3
WEIGHT = 6
SCHOOL = 18

# Weight multiplier to account for skill levels
SKILL_LEVEL_TO_WEIGHT_RATIO = {"beginner": 1.0, "intermediate": 1.03, "experienced": 1.05}

# For safety, wrestlers shouldn't wrestle an opponent more than 105% of their body weight
MAX_WEIGHT_TO_GIVE = 0.05


class Wrestler:

    def __init__(self, name: str, weight: float, school: str, skill_level: str):
        self.weight = weight
        self.school = school.strip()
        self.skill_level = skill_level.strip()
        self.name = name.strip()

    def is_safe_match_for(self, opponent):
        # We don't want wrestlers getting paired with themselves
        if self == opponent:
            return False
        return MAX_WEIGHT_TO_GIVE > abs(self.weight - opponent.weight) / min(self.weight, opponent.weight)

    def __lt__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __str__(self):
        return "{name} {weight} lbs {school} {skill_level}".format(name=self.name, weight=self.weight,
                                                                      school=self.school, skill_level=self.skill_level)


class Match:
    def __init__(self, w1: Wrestler, w2: Wrestler):
        self.w1 = w1
        self.w2 = w2

    def __str__(self):
        return "{name1} ({school1} {weight1} lbs),{name2} ({school2} {weight2} lbs)".format(name1=self.w1.name, school1=self.w1.school, weight1=self.w1.weight,
                                                                    name2=self.w2.name, school2=self.w2.school, weight2=self.w2.weight)


def main():
    wrestlers = initialize_wrestlers()
    matches, wrestlers_no_first_round = find_first_round(wrestlers)
    second_round_matches, no_matches = find_second_round(wrestlers, wrestlers_no_first_round)
    matches += second_round_matches
    write_matches_to_file(matches, no_matches)


def find_first_round(wrestlers: List[Wrestler]):
    wrestlers_no_matches = wrestlers.copy()
    matches = []
    start = 0
    end = 1

    while start < end < len(wrestlers_no_matches):
        start_wrestler = wrestlers_no_matches[start]
        end_wrestler = wrestlers_no_matches[end]
        if start_wrestler.is_safe_match_for(end_wrestler) and start_wrestler.school != end_wrestler.school:
            matches.append(Match(start_wrestler, end_wrestler))
            wrestlers_no_matches.pop(end)
            wrestlers_no_matches.pop(start)
        else:
            # skip this wrestler because they're either too big or from the same school
            end += 1

        # if we're at the end of the list or the current wrestler is too small for any possible matches,
        # then the current wrestler just won't have a first round match
        if not end < len(wrestlers) or not end_wrestler.is_safe_match_for(start_wrestler):
            start += 1
            end = start + 1

    return matches, wrestlers_no_matches


def find_second_round(wrestlers, wrestlers_no_matches) -> (List[Match], List[Wrestler]):
    second_round_matches = []
    no_matches = []
    for wrestler in wrestlers_no_matches:
        start = 0
        while start < len(wrestlers) and not wrestler.is_safe_match_for(wrestlers[start]):
            start += 1

        if start < len(wrestlers):
            second_round_matches.append(Match(wrestler, wrestlers[start]))
            wrestlers.pop(start)
        else:
            no_matches.append(wrestler)
    return second_round_matches, no_matches


def initialize_wrestlers():
    input_filename = sys.argv[1]

    input_file = open(input_filename, "r")
    input_lines = input_file.readlines()

    wrestlers = []

    for line in input_lines:
        non_numeric_characters = "[^0-9.]"
        line = line.split(",")
        line[WEIGHT] = re.sub(non_numeric_characters, "", line[WEIGHT])
        current_wrestler = Wrestler(line[FIRST_NAME] + " " + line[LAST_NAME], float(line[WEIGHT]), line[SCHOOL],
                                    line[SKILL_LEVEL])
        if not current_wrestler.skill_level:
            current_wrestler.skill_level = "beginner"

        current_wrestler.weight *= SKILL_LEVEL_TO_WEIGHT_RATIO[current_wrestler.skill_level]
        wrestlers.append(current_wrestler)

    wrestlers.sort()
    return wrestlers


def write_matches_to_file(matches, no_matches):
    output_filename = sys.argv[2]
    output_file = open(output_filename, "w+")
    output_file.writelines("Wrestler 1, Wrestler 2, Mat\n")
    for match in matches:
        output_file.writelines(str(match) + "," + "\n")

    output_file.write("WRESTLERS WITHOUT MATCHES:\n")
    for wrestler in no_matches:
        output_file.writelines(str(wrestler) + "\n")


if __name__ == "__main__":
    main()
