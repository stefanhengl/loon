"""Hash Code 2015 Loon

Ideas:

- slow down in populated arreas, speed up over the oceans
- choose bands of 14 instead of rows

"""

from collections import Counter
import random

# global variabels
C = -1
A = -1
R = -1

class Cell(object):
    def __init__(self, r, c):
        self.r = int(r)
        self.c = int(c)

    def __add__(self, other):
        return Cell(self.r + other.r, (self.c + other.c) % C)

    def __str__(self):
        return "({}, {})".format(self.r, self.c)

class Ballon(object):
    def __init__(self, pos, height=0, target=None, radius=1):
        assert isinstance(pos, Cell)
        self.pos = pos
        self.height = height
        self.target = target
        self.radius = radius
        self.lost = False

    def covers(self, pos):
        return ((self.pos.r-pos.r)*2 + (self.columndist(self.pos.c, pos.c)*2)) < self.radius*2

    def columndist(self, c1, c2):
        return min(abs(c1-c2), C-abs(c1-c2))

def convert_to_cell(cString):
    return Cell(*[int(item) for item in cString.split()])

def convert_movement_row_to_cells(row):
    splitRow = row.split()
    return [Cell(*splitRow[i:i+2]) for i in range(0, len(splitRow), 2)]

def create_wind_grid(data, A, C, R):
    """
    0-indexed 3D list containing a wind vector for each postion and altitude
    """
    wind = [[[0]*A]*C]*R
    for alt in range(A):
        for row in range(R):
            row_wind = convert_movement_row_to_cells(data[(alt*R)+row])
            for col in range(C):
                wind[row][col][alt] = row_wind[col]
    return wind

def load(loon_input_file):
    """
    Loads the input data from disk according to the specifications in the documentation
    """
    with open(loon_input_file, 'rb') as handle:
        data = handle.readlines()

    # First row: rows, columns, altitudes
    rows, columns, altitudes = [int(item) for item in data[0].split()]

    # Second row: targets, radius, ballons, time
    itargets, radius, iballons, total_time = [int(item) for item in data[1].split()]

    # Third row: starting cell for all balloons
    starting_cell = convert_to_cell(data[2])

    # Targets
    target_cells = [{"pos":convert_to_cell(cString), "coverage":0} for cString in data[3:(3+itargets)]]

    # Wind
    wind = create_wind_grid(data[(3+itargets):((3+itargets)+(altitudes*rows))], altitudes, columns, rows)

    return rows, columns, altitudes, radius, iballons, total_time, starting_cell, target_cells, wind

def play(ballons, wind):
    started_balloons = set()
    for ballon in ballons:
        move(ballon, wind, started_balloons)
    
    print len(started_balloons), 'balloons started'

def move(balloon, wind, started_balloons):
    # Ballons on the ground
    threshold = 0.1
    if balloon.height == 0:
        # (1) Spread out ballons by randomzing launch time
        # (2) Make sure two ballons with the same target do not start at the same time
        if random.random() <= threshold and not balloon.target in started_balloons:
            balloon.pos = balloon.pos + wind[balloon.pos.r-1][balloon.pos.c-1][1]
            balloon.height = 1
            started_balloons.add(balloon.target)
        return

    # Flying balloons:
    if balloon.lost:
        return 0

    # Check which altitude change leads to best results x steps in the future
    choice = time_travel(balloon.pos, balloon.height, 0, 2, balloon.target, wind)

    # Update ballon position based on choice
    balloon.pos += get_vector_for_alt_change(balloon.pos, balloon.height, choice, wind)
    if out_of_bounds(balloon.pos):
        balloon.lost = True
        print "balloon lost"
    balloon.height += choice

    return choice

def out_of_bounds(pos):
    """
    return True if balloon is still on the map, False otherwise
    """
    return not 0 < pos.r <= R

def get_vector_for_alt_change(pos, altitude, alt_change, wind):
    """
    return wind vector for altitude changes depending on the current position and altitude
    """
    return wind[pos.r-1][(pos.c-1) % C ][altitude + alt_change]

def time_travel(current_pos, current_alt, current_step, total_steps, target_row, wind):
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
        return abs(current_pos.r - target_row)

    opts = get_options(current_alt)
    distances = []
    for opt in opts:
        vec_for_opt = get_vector_for_alt_change(current_pos, current_alt, opt, wind)
        new_pos = current_pos + vec_for_opt
        new_height = current_alt + opt
        dist = time_travel(new_pos, new_height, current_step +1, total_steps, target_row, wind)
        distances.append(dist)
 
    if current_step > 0:
        return min(distances)
    return opts[distances.index(min(distances))]

def check_coverage(targetCells, ballons):
    for t in targetCells:
        for b in ballons:
            if b.covers(t["pos"]):
                t["coverage"] += 1
                break

def count_points(targetCells):
    points = 0
    for targetCell in targetCells:
        points += targetCell["coverage"]
    return points

def create_ballons(B, starting_cell, radius):
    return [Ballon(pos=starting_cell, height=0, radius=radius) for _ in range(B)]

def assign_target_row_to_ballons(ballons, targetCells, R, V): # TODO: OPTIMZE THIS TO BANDS
    upper_limit = (R-V)-1
    lower_limit = V
    cnt = Counter([targetCell["pos"].r for targetCell in targetCells])
    choices_deep = [[item]*cnt[item] for item in cnt]
    choices_flat = [item for sublist in choices_deep for item in sublist]
    choices_cut = [lower_limit if item < lower_limit else min(item, upper_limit)
                   for item in choices_flat]
    for ballon in ballons:
        ballon.target = random.choice(choices_cut)

def main():
    global R, C, A
    R, C, A, radius, B, T, starting_cell, target_cells, wind = load("loon_r70_c300_a8_radius7_saturation_250.in")
    balloons = create_ballons(B, starting_cell, radius)
    assign_target_row_to_ballons(balloons, target_cells, R, radius)

    for i in range(T):
        play(balloons, wind)
        check_coverage(target_cells, balloons)
        print 'Turn {} Points {}'.format(i, count_points(target_cells))

if __name__ == "__main__":
    main()
