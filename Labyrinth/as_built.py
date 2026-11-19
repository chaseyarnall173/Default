"""The maze exactly as the team built it in plywood (November 2026).

Traced from the team's laser drawing (Carnival_Project_Dimensions_for_
Laser_Cutting_v2) and checked wall by wall against photos of the built
board. make_autocad_script.py builds the 3D model from these numbers.
(make_labyrinth.py is the older 9 x 9 grid design and no longer matches.)

Units are inches. Origin at the front-left corner of the floor plate, top
of the floor at z = 0, x to the right, y away from the player.
"""

BOARD = 11.5            # floor plate, square; the rim sits on top of it
T = 0.125               # 1/8 in plywood
WALL_H = 2.0            # maze walls and rim, above the floor
BALL_D = 0.709          # 18 mm ball

# Rim (painted yellow): left/right are 11.5 long, front/back 11.25 between
RIMS = {
    "RIM-LEFT": (0.0, 0.0, T, BOARD),
    "RIM-RIGHT": (BOARD - T, 0.0, BOARD, BOARD),
    "RIM-FRONT": (T, 0.0, BOARD - T, T),
    "RIM-BACK": (T, BOARD - T, BOARD - T, BOARD),
}

# Maze walls (painted blue), 2 in tall: (x0, y0, x1, y1) footprints.
# Pieces meeting at a corner overlap by one wall thickness here.
WALLS = [
    # front third (START side)
    (T, 1.0, 1.5, 1.125),             # START pocket, lower
    (T, 2.5, 1.5, 2.625),             # START pocket, upper
    (2.5, 1.125, 2.625, 2.625),       # first arch, left leg
    (2.5, 2.5, 4.0, 2.625),           # first arch, top
    (3.875, T, 4.0, 2.625),           # first arch, right leg (to the rim)
    (5.125, 1.125, 5.25, 2.625),      # arch round the X hole, left leg
    (5.125, 2.5, 6.625, 2.625),       # arch round the X hole, top
    (6.5, 1.125, 6.625, 4.0),         # arch round the X hole, right leg
    (7.75, 2.5, 9.125, 2.625),        # hook, top
    (9.0, T, 9.125, 2.625),           # hook, leg (to the rim)
    (10.125, 1.125, 10.25, 4.0),      # right post up to the long wall
    (T, 3.875, 10.125, 4.0),          # long wall, 10 in
    # middle third (trapdoor)
    (4.0, 3.875, 4.125, 5.0),         # stub under the trapdoor wall
    (4.0, 4.875, 7.5, 5.0),           # wall below the trapdoor, 3.5 in
    (1.25, 4.875, 2.5, 5.0),          # foot of the long left wall
    (1.25, 4.875, 1.375, 10.125),     # long left wall
    (2.5, 6.0, 8.0, 6.125),           # wall above the trapdoor, 5.5 in
    (4.125, 6.0, 4.25, 7.375),        # stub above the trapdoor wall
    (9.125, 3.875, 9.25, 6.125),      # pocket round the right X hole
    (9.125, 4.875, 10.25, 5.0),
    (9.125, 6.0, 10.25, 6.125),
    (1.25, 7.25, BOARD - T, 7.375),   # long wall, 10.125 in
    # back third (prize corner)
    (2.5, 8.125, 4.0, 8.25),          # C shape
    (2.5, 8.125, 2.625, 9.0),
    (2.5, 8.875, 5.0, 9.0),
    (4.875, 7.25, 5.0, 10.375),
    (2.5, 10.125, 3.75, 10.25),       # pocket round the back-left X hole
    (2.5, 10.125, 2.625, BOARD - T),
    (6.125, 8.875, 7.625, 9.0),       # L
    (6.125, 8.875, 6.25, 10.125),
    (7.5, 8.375, 7.625, BOARD - T),   # left of the 1
    (8.75, 7.25, 8.875, 8.5),         # beside the X hole under the 3
    (8.75, 10.125, 8.875, BOARD - T), # between 1 and 3
    (10.0, 8.875, 10.125, BOARD - T), # between 3 and 5
]

HOLE_D = 0.875          # every hole is the same size now
# (label, x, y): "1", "3", "5" pay coins, "X" is a loss
HOLES = [
    ("1", 8.1875, 10.8125),
    ("3", 9.4375, 10.75),
    ("5", 10.75, 10.75),
    ("X", 3.25, 10.8125),
    ("X", 9.4375, 7.9375),
    ("X", 1.9375, 5.5),
    ("X", 9.75, 5.5),
    ("X", 0.875, 3.1875),
    ("X", 5.8125, 1.75),
]
TRAP = (5.5, 5.5, 1.0)      # trapdoor opening: centre x, y and size
START = (1.9, 0.6)          # where the ball waits
LABELS = [("START", 0.95, 0.45, 0.16), ("1", 8.1875, 10.2, 0.2),
          ("3", 9.4375, 10.2, 0.2), ("5", 10.75, 10.2, 0.2)]

# Collection tray: a box hanging under the floor, its walls in line with
# the rim. The left and front walls have a corner cut out at the START
# corner (3 in along each wall, 1.625 in tall) so the ball ends up there.
TRAY_H = 2.375          # tray walls
TRAY_CUT_LEN = 3.0      # length of the cut-out along each wall
TRAY_CUT_H = 1.625      # height of the cut-out
TRAY_LIP = TRAY_H - TRAY_CUT_H    # 0.75 in strip left under the cut-out
# True: the 0.75 in strip sits on the tray floor and the opening is at the
# top, under the board (as drawn) - the strip keeps the ball in the
# corner. False: the strip is at the top and the ball can roll out.
TRAY_LIP_AT_FLOOR = True

# AutoCAD colour numbers (ACI): 1 red, 2 yellow, 5 blue
COLOR = {"FLOOR": 1, "RIM": 2, "WALLS": 5, "OUTER-BOX": 1,
         "TRAY-WALLS": 2, "TRAY-FLOOR": 42}


def check():
    """Every wall sits inside the rim, every hole is on the floor and
    clear of the walls, and the trapdoor doesn't touch a hole."""
    lo, hi = T, BOARD - T
    for x0, y0, x1, y1 in WALLS:
        assert lo - 1e-9 <= x0 < x1 <= hi + 1e-9, (x0, y0, x1, y1)
        assert lo - 1e-9 <= y0 < y1 <= hi + 1e-9, (x0, y0, x1, y1)
        assert abs(min(x1 - x0, y1 - y0) - T) < 1e-9, "walls are 1/8 thick"
    r = HOLE_D / 2
    for name, x, y in HOLES:
        assert lo + r <= x <= hi - r and lo + r <= y <= hi - r, name
        for x0, y0, x1, y1 in WALLS:
            dx = max(x0 - x, 0, x - x1)
            dy = max(y0 - y, 0, y - y1)
            assert (dx * dx + dy * dy) ** 0.5 >= r - 0.02, \
                "hole %s at %.2f,%.2f runs under a wall" % (name, x, y)
    assert TRAY_LIP > BALL_D, "the ball would roll over the tray lip"
    return True


if __name__ == "__main__":
    check()
    print("%d walls, %d holes - all inside the rim and clear of the walls"
          % (len(WALLS), len(HOLES)))
