"""Hash Code 2015 Loon
"""
from __future__ import division
import csv
import math
import os

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
        return ((self.pos.r - pos.r) ** 2 + (columndist(self.pos.c, pos.c) ** 2)) < self.radius ** 2


def columndist(c_1, c_2):
    """
    Utility function for "covers"
    """
    return min(abs(c_1 - c_2), C - abs(c_1 - c_2))


class Vector(object):
    """
    Vectors have a length, can be added, substracted, and printed
    """

    def __init__(self, r, c):
        self.r = int(r)
        self.c = int(c)

    def __add__(self, other):
        return Vector(self.r + other.r, (self.c + other.c) % C)

    def __str__(self):
        return "({}, {})".format(self.r, self.c)

    def __len__(self):
        return math.sqrt(self.r**2 + self.c**2)

    def __sub__(self, other):
        return Vector(self.r - other.r, columndist(self.c, other.c))


def play(balloons, wind, last_started_balloons):
    """
    play represents one turn in the game
    """
    moves = []
    for balloon in balloons:
        this_move = move(balloon, wind, last_started_balloons)
        moves.append(this_move)
    return moves


def move(balloon, wind, last_started_balloons):
    """
    move returns the next altitude change for "balloon" based on the wind pattern and its
    assigned target row.
    """
    # Balloons on the ground
    if balloon.height == 0:
        # (1) Spread out balloons by randomzing launch time
        # (2) Make sure two balloons with the same target do not start at the same time
        try:
            last_balloon = last_started_balloons[balloon.target]
            if len(last_balloon.pos - balloon.pos) > 2 * balloon.radius:
                balloon.pos += wind[balloon.pos.r - 1][balloon.pos.c - 1][1]
                balloon.height = 1
                last_started_balloons[balloon.target] = balloon
                return 1
            else:
                return 0
        except KeyError:
            balloon.pos += wind[balloon.pos.r - 1][balloon.pos.c - 1][1]
            balloon.height = 1
            last_started_balloons[balloon.target] = balloon
            return 1

    # Flying balloons:
    if balloon.lost:
        return 0

    # Check which altitude change leads to best results "total_steps" steps in the future
    choice = time_travel(
        starting_pos=balloon.pos,
        current_pos=balloon.pos,
        current_alt=balloon.height,
        current_step=0,
        total_steps=3,
        target_row=balloon.target,
        wind=wind,
    )

    # Update balloon position based on choice
    balloon.pos += get_vector_for_alt_change(
        balloon.pos, balloon.height, choice, wind)
    if out_of_bounds(balloon.pos):
        balloon.lost = True
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
        return scoring(starting_pos, current_pos, target_row)

    opts = get_options(current_alt)
    scores = []
    # For each option (-1, 0, +1) travel further to the future
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
        scores.append(dist)

    if current_step > 0:
        return max(scores)
    return opts[scores.index(max(scores))]


def scoring(starting_pos, current_pos, target_row):
    """
    Return a score based on starting position, current position and the assigned target row
    The lower the score the better.
    """
    speed = len(starting_pos - current_pos)
    distance_to_target_row = abs(current_pos.r - target_row)
    penalty = -10 if out_of_bounds(current_pos) else 0

    # alpha > 0: higher speed yields higher scores
    alpha = 0.03
    # penalize speed over densly populated areas
    if 80 < starting_pos.c < 130 or 160 < starting_pos.c < 200:
        alpha = -1 * alpha

    score = 3.0 / (distance_to_target_row + 1) + alpha * speed + penalty
    return score


def get_vector_for_alt_change(pos, altitude, alt_change, wind):
    """
    Return wind vector for altitude changes depending on the current position and altitude
    """
    return wind[pos.r - 1][(pos.c - 1) % C][altitude + alt_change - 1]


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


def save_moves_to_disk(fle, moves):
    """
    Appends lines like "0 1 0 0 0 -1 0 0 ..... 0" to file "fle"
    """
    with open(fle, "a") as handle:
        writer = csv.writer(handle, delimiter=" ", lineterminator="\n")
        writer.writerow(moves)


def reset_target_cells(target_cells):
    """
    Resets coverage of all target cells to 0
    """
    return [{"pos": tc["pos"], "coverage":0} for tc in target_cells]


def main():
    """
    Greedy algorithm. We add one balloon at a time and determine an optimal target row for each 
    new balloon.
    """

    # load data
    radius, B, T, starting_cell, target_cells, wind = load(
        "./input/loon_r70_c300_a8_radius7_saturation_250.in")

    target_rows = []
    # add one balloon at a time until we have B balloons
    while len(target_rows) < B:
        scores = {}
        for i in range(65, 30, -1):

            target_cells = reset_target_cells(target_cells)

            # add balloon
            balloons = create_balloons(
                1 + len(target_rows), starting_cell, radius)
            balloons[0].target = i
            for j, balloon in enumerate(balloons[1:]):
                balloon.target = target_rows[j]

            last_started_balloons = {}
            print "simulating with", len(balloons), "balloons"
            print "target rows", [bal.target for bal in balloons]

            # simulation
            for _ in range(T):
                play(balloons, wind, last_started_balloons)
                check_coverage(target_cells, balloons)

            # save results
            this_rounds_points = count_points(target_cells)
            print "points", this_rounds_points
            scores.setdefault(this_rounds_points, []).append(i)

        target_rows.append(max(scores[max(scores)]))
        print target_rows, max(scores)

    # At this point, the greedy algorithm determined a set of target rows The
    # next step is to run the full simulation with the this set and to save the each
    # move to disk.
    target_cells = reset_target_cells(target_cells)

    balloons = create_balloons(B, starting_cell, radius)
    for i, balloon in enumerate(balloons):
        balloon.target = target_rows[i]

    last_started_balloons = {}
    try:
        os.remove("./output/loon.out")
    except OSError:
        pass

    # simulation
    for _ in range(T):
        moves = play(balloons, wind, last_started_balloons)
        check_coverage(target_cells, balloons)
        # save moves to file
        save_moves_to_disk("./output/loon.out", moves)

    # rename output file
    points = count_points(target_cells)
    os.rename("./output/loon.out", "./output/loon_{}.out".format(points))


if __name__ == "__main__":
    # create output directory if it does not already exist
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), "output")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "output"))

    main()
