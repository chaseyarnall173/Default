"""3D-printable balls for The Labyrinth (STL, millimetres).

The ball is sized from the game: 5/8 in (15.875 mm) fits the smallest
hole (the 5-coin hole, 3/4 in = 19.05 mm) with about 3 mm to spare.

    python3 make_ball.py   ->  Labyrinth_ball_solid.stl  one solid ball
                               Labyrinth_ball_half.stl   half of a ball with a
                               hollow for a weight: print 2, put the weight
                               in, glue the flat faces together
"""
import math
import os
import struct

import make_labyrinth as ml

HERE = os.path.dirname(os.path.abspath(__file__))
BALL_MM = ml.BALL_D * 25.4                 # 15.875 mm
SMALLEST_HOLE_MM = min(ml.HOLE_D.values()) * 25.4
WEIGHT_HOLE_MM = 9.0                       # hollow inside each half (dia)
SEG, RINGS = 96, 48                        # smoothness


def write_stl(path, tris):
    with open(path, "wb") as fh:
        fh.write(b"Labyrinth ball".ljust(80, b" "))
        fh.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux, uy, uz = (b[i] - a[i] for i in range(3))
            vx, vy, vz = (c[i] - a[i] for i in range(3))
            n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
            ln = math.sqrt(sum(k * k for k in n)) or 1.0
            fh.write(struct.pack("<12fH", *(k / ln for k in n), *a, *b, *c,
                                 0))
    print("wrote %s (%d triangles)" % (path, len(tris)))


def dome(r, z_sign, inward=False):
    """Half sphere surface (z >= 0 if z_sign > 0), as triangles."""
    tris = []
    for j in range(RINGS):
        p0 = math.pi / 2 * j / RINGS               # 0 = pole
        p1 = math.pi / 2 * (j + 1) / RINGS
        for i in range(SEG):
            t0 = 2 * math.pi * i / SEG
            t1 = 2 * math.pi * (i + 1) / SEG

            def pt(p, t):
                return (r * math.sin(p) * math.cos(t),
                        r * math.sin(p) * math.sin(t),
                        z_sign * r * math.cos(p))
            a, b, c, d = pt(p0, t0), pt(p1, t0), pt(p1, t1), pt(p0, t1)
            quad = [(a, b, c), (a, c, d)] if j else [(a, b, c)]
            for tri in quad:
                if (z_sign < 0) != inward:
                    tri = (tri[0], tri[2], tri[1])
                tris.append(tri)
    return tris


def ring(r_in, r_out):
    """Flat annulus (or disc if r_in == 0) at z = 0, facing down."""
    tris = []
    for i in range(SEG):
        t0 = 2 * math.pi * i / SEG
        t1 = 2 * math.pi * (i + 1) / SEG
        o0 = (r_out * math.cos(t0), r_out * math.sin(t0), 0.0)
        o1 = (r_out * math.cos(t1), r_out * math.sin(t1), 0.0)
        if r_in == 0:
            tris.append(((0.0, 0.0, 0.0), o1, o0))
            continue
        i0 = (r_in * math.cos(t0), r_in * math.sin(t0), 0.0)
        i1 = (r_in * math.cos(t1), r_in * math.sin(t1), 0.0)
        tris += [(i0, o1, o0), (i0, i1, o1)]
    return tris


def main():
    assert BALL_MM < SMALLEST_HOLE_MM - 2, "ball would not drop in the 5 hole"
    r = BALL_MM / 2
    write_stl(os.path.join(HERE, "Labyrinth_ball_solid.stl"),
              dome(r, 1) + dome(r, -1))
    # half ball, flat face on the print bed (z = 0), hollow for a weight
    half = dome(r, 1) + dome(WEIGHT_HOLE_MM / 2, 1, inward=True) + \
        ring(WEIGHT_HOLE_MM / 2, r)
    write_stl(os.path.join(HERE, "Labyrinth_ball_half.stl"), half)
    print("ball %.3f mm, smallest hole %.2f mm, clearance %.2f mm"
          % (BALL_MM, SMALLEST_HOLE_MM, SMALLEST_HOLE_MM - BALL_MM))


if __name__ == "__main__":
    main()
