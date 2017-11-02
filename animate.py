"""
Creates an animated plot to show the movement of the balloons

Usage:
python animate.py
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from loon import load, create_balloons, play


def generator():
    radius, B, T, starting_cell, target_cells, wind = load(
        "./input/loon_r70_c300_a8_radius7_saturation_250.in")

    balloons = create_balloons(B, starting_cell, radius)

    target_rows = [63, 63, 63, 63, 61, 61, 61, 63, 63, 61, 63, 63, 61, 61, 61, 61, 44, 44, 44, 44, 44, 44, 61, 61, 61,
                   61, 61, 61, 61, 44, 61, 44, 44, 44, 44, 44, 44, 44, 44, 44, 33, 33, 33, 33, 33, 33, 51, 33, 61, 33, 33, 33, 33]

    for i, balloon in enumerate(balloons):
        balloon.target = target_rows[i]

    # start simulation
    last_started_balloons = {}
    for _ in range(T):
        play(balloons, wind, last_started_balloons)
        yield [balloon.pos for balloon in balloons]


def create_animation():
    fig, ax = plt.subplots()
    ax.set_ylim(0, 70)
    ax.set_xlim(0, 300)
    scat = ax.scatter([0], [0],  s=120, facecolors='g', edgecolors='g', alpha=0.5)
    gen = generator()

    def init():
        scat.set_data([], [])
        return scat

    def update(i):
        try:
            data = gen.next()
            x = [item.c for item in data]
            y = [item.r for item in data]
            scat.set_offsets(zip(x, y))
            return scat
        except StopIteration:
            return None

    ani = animation.FuncAnimation(fig, func=update, frames=range(1))
    plt.show()


if __name__ == "__main__":
    create_animation()
