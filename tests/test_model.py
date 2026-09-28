from pipeline import model

ANTICLOCKWISE = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]


def test_map_coords_are_wound_clockwise():
    coords = [float(v) for v in model._map_coords(ANTICLOCKWISE).split(",")]
    ring = list(zip(coords[::2], coords[1::2]))
    shoelace = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:]))
    assert shoelace < 0


def test_map_coords_keep_clockwise_rings_unchanged():
    clockwise = ANTICLOCKWISE[::-1]
    assert model._map_coords(clockwise) == "0.00000,0.00000,0.00000,1.00000,1.00000,1.00000,1.00000,0.00000,0.00000,0.00000"
