"""Hash Code 2015 Loon

Strategy:
- Calculate number of targets per row #T(r)
- Assign each balloon B to a target row r->B such that #B(r) ~ #T(r)
- Choose change of altitude by checking recursively which change puts
  the balloon closest to the target row x steps in the future

More Ideas:
- Change scoring function such that balloons slow down in populated arreas
  and speed up over the oceans
"""

from collections import Counter
import csv
import os
import random

import numpy as np

# global variabels
C = -1  # Columns
A = -1  # Altitudes
R = -1  # Rows


class Balloon(object):
    """
    Each Balloon is represented by one object.
    """

    def __init__(self, pos, height=0, target=None, radius=1):
        assert isinstance(pos, Vector)
        self.pos = pos
        self.height = height
        self.target = target
        self.radius = radius
        self.lost = False

    def covers(self, pos):
        """
        Returns True if "pos" is covered by the balloon
        """
        return ((self.pos.r - pos.r) * 2 + (self._columndist(self.pos.c, pos.c) * 2)) < self.radius * 2

    def _columndist(self, c_1, c_2):
        """
        Utility function for "covers"
        """
        return min(abs(c_1 - c_2), C - abs(c_1 - c_2))


class Vector(object):
    """
    Vector can be added and printed
    """

    def __init__(self, r, c):
        self.r = int(r)
        self.c = int(c)

    def __add__(self, other):
        return Vector(self.r + other.r, (self.c + other.c) % C)

    def __str__(self):
        return "({}, {})".format(self.r, self.c)


def play(balloons, wind):
    """
    play represents one turn in the game
    """
    started_balloons = set()
    moves = []
    for balloon in balloons:
        this_move = move(balloon, wind, started_balloons)
        moves.append(this_move)
    return moves


def move(balloon, wind, started_balloons):
    """
    move returns the next altitude change for "balloon" based on the wind pattern and its
    assigned target row.
    """
    # Balloons on the ground
    threshold = 0.025
    if balloon.height == 0:
        # (1) Spread out balloons by randomzing launch time
        # (2) Make sure two balloons with the same target do not start at the same time
        if random.random() <= threshold and not balloon.target in started_balloons:
            balloon.pos += wind[balloon.pos.r - 1][balloon.pos.c - 1][1]
            balloon.height = 1
            started_balloons.add(balloon.target)
            return 1  # balloon starts
        return 0  # balloon stays on the ground

    # Flying balloons:
    if balloon.lost:
        return 0

    # Check which altitude change leads to best results "total_steps" steps in the future
    choice = time_travel(
        starting_pos=balloon.pos,
        current_pos=balloon.pos,
        current_alt=balloon.height,
        current_step=0,
        total_steps=2,
        target_row=balloon.target,
        wind=wind,
    )

    # Update balloon position based on choice
    balloon.pos += get_vector_for_alt_change(
        balloon.pos, balloon.height, choice, wind)
    if out_of_bounds(balloon.pos):
        balloon.lost = True
        print "balloon lost"
    balloon.height += choice

    return choice


def time_travel(starting_pos, current_pos, current_alt,
                current_step, total_steps, target_row, wind):
    """
    Recursive search for the best path from current_pos for total_steps in the future
    """
    def get_options(altitude):
        """
        determine possible options to change altitude depending on the current altitude
        """
        opts = [0]
        if altitude != A:
            opts.append(1)
        if altitude > 1:
            opts.append(-1)
        return opts

    if current_step == total_steps:
        # scoring
        return score(starting_pos, current_pos, target_row)

    opts = get_options(current_alt)
    distances = []
    # For each option (-1, 0, +1) travel further in time
    for opt in opts:
        vec_for_opt = get_vector_for_alt_change(
            current_pos, current_alt, opt, wind)
        new_pos = current_pos + vec_for_opt
        new_height = current_alt + opt
        dist = time_travel(
            starting_pos=starting_pos,
            current_pos=new_pos,
            current_alt=new_height,
            current_step=current_step + 1,
            total_steps=total_steps,
            target_row=target_row,
            wind=wind
        )
        distances.append(dist)

    if current_step > 0:
        return min(distances)
    return opts[distances.index(min(distances))]


def score(starting_pos, current_pos, target_row):
    """
    Return a scare based on starting position, current position and the assigned target row
    The lower the score the better.
    """
    return abs(current_pos.r - target_row)


def get_vector_for_alt_change(pos, altitude, alt_change, wind):
    """
    Return wind vector for altitude changes depending on the current position and altitude
    """
    return wind[pos.r - 1][(pos.c - 1) % C][altitude + alt_change]


def out_of_bounds(pos):
    """
    Return "True" if balloon is still on the map, "False" otherwise
    """
    return not 0 < pos.r <= R


def convert_to_vector(coordinates):
    """
    "7 3" -> Cell(7,3)
    """
    return Vector(*[int(item) for item in coordinates.split()])


def convert_row_to_vectors(row):
    """
    "1 3 1 3 1 3" > [Cell(1, 3), Cell(1, 3), Cell(1, 3)]
    """
    split_row = row.split()
    return [Vector(*split_row[i:i + 2]) for i in range(0, len(split_row), 2)]


def create_wind_grid(data):
    """
    0-indexed 3D list containing a wind vector for each postion and altitude
    """
    wind = [[[0] * A] * C] * R
    for alt in range(A):
        for row in range(R):
            row_wind = convert_row_to_vectors(data[(alt * R) + row])
            for col in range(C):
                wind[row][col][alt] = row_wind[col]
    return wind


def load(loon_input_file):
    """
    Loads the input data from disk according to the specifications in the documentation
    """
    global R, C, A
    with open(loon_input_file, 'rb') as handle:
        data = handle.readlines()

    # First row: rows, columns, altitudes
    R, C, A = [int(item) for item in data[0].split()]

    # Second row: targets, radius, balloons, time
    itargets, radius, B, total_time = [
        int(item) for item in data[1].split()]

    # Third row: starting cell for all balloons
    starting_cell = convert_to_vector(data[2])

    # Targets
    target_cells = [{"pos": convert_to_vector(cString), "coverage": 0}
                    for cString in data[3:(3 + itargets)]]

    # Wind
    wind = create_wind_grid(data[(3 + itargets):((3 + itargets) + (A * R))])

    return radius, B, total_time, starting_cell, target_cells, wind


def check_coverage(target_cells, balloons):
    """
    Updates the coverage for each target cell based on the current position of all balloons
    """
    for target in target_cells:
        for balloon in balloons:
            if balloon.covers(target["pos"]):
                target["coverage"] += 1
                break


def count_points(target_cells):
    """
    Return the sum of all coverage times
    """
    points = 0
    for target_cell in target_cells:
        points += target_cell["coverage"]
    return points


def create_balloons(number_of_balloons, starting_cell, radius):
    """
    Create list of B balloons
    """
    return [Balloon(pos=starting_cell, height=0, radius=radius) for _ in range(number_of_balloons)]


def assign_target_row_to_balloons(balloons, target_cells, radius):
    """
    Balloons are assigned to target rows proportionally to the population density per row.
    """
    use_bands = True
    upper_limit = (R - radius) - 1
    lower_limit = radius
    if use_bands:
        bands = range(radius, 70, 14)
        cnt = Counter([min(bands, key=lambda x: abs(x - target_cell["pos"].r))
                       for target_cell in target_cells])
    else:
        cnt = Counter([targetCell["pos"].r for targetCell in target_cells])

    choices_deep = [[item] * cnt[item] for item in cnt]
    choices_flat = [item for sublist in choices_deep for item in sublist]
    choices_cut = [lower_limit if item < lower_limit else min(item, upper_limit)
                   for item in choices_flat]
    for balloon in balloons:
        balloon.target = random.choice(choices_cut)


def save_moves_to_disk(fle, moves):
    """
    Appends lines like "0 1 0 0 0 -1 0 0 ..... 0" to file "fle"
    """
    with open(fle, "a") as handle:
        writer = csv.writer(handle, delimiter=" ", lineterminator="\n")
        writer.writerow(moves)


def main():
    global R, C, A
    reps = 80  # run the simulation several times
    points = []
    for _ in range(reps):
        # load data
        radius, B, T, starting_cell, target_cells, wind = load(
            "loon_r70_c300_a8_radius7_saturation_250.in")
        balloons = create_balloons(B, starting_cell, radius)
        assign_target_row_to_balloons(balloons, target_cells, radius)
        try:
            os.remove("./loon.out")
        except OSError:
            pass

        # start simulation
        for _ in range(T):
            moves = play(balloons, wind)
            check_coverage(target_cells, balloons)
            save_moves_to_disk("./loon.out", moves)

        this_rounds_points = count_points(target_cells)
        os.rename("./loon.out", "{}.out".format(this_rounds_points))
        points.append(this_rounds_points)

    print "mean:", np.mean(points)
    print "max:", np.max(points)


if __name__ == "__main__":
    main()
