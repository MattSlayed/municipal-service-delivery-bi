import pandas as pd
import pytest

from pipeline import config, model

ANTICLOCKWISE = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]


def test_map_coords_are_wound_clockwise():
    coords = [float(v) for v in model._map_coords(ANTICLOCKWISE).split(",")]
    ring = list(zip(coords[::2], coords[1::2]))
    shoelace = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:]))
    assert shoelace < 0


def test_map_coords_keep_clockwise_rings_unchanged():
    clockwise = ANTICLOCKWISE[::-1]
    assert model._map_coords(clockwise) == "0.00000,0.00000,0.00000,1.00000,1.00000,1.00000,1.00000,0.00000,0.00000,0.00000"


def sections(rows):
    return pd.DataFrame(rows, columns=["department", "branch", "section"]).assign(official_suburb="X", code_group="WATER")


def test_missing_section_is_labelled_by_its_branch():
    df = model.prepare_labels(sections([
        ("Technical Services", "Reticulation", None),
        (None, None, None),
    ]))
    assert df["section"].tolist() == ["Reticulation (unassigned)", "Unassigned"]


def test_section_dimension_marks_field_crews():
    df = model.prepare_labels(sections([
        ("Technical Services", "Reticulation", "Reticulation WW Conveyance"),
        ("Commercial Services", "Customer Services (Water)", "Billing Management"),
    ]))
    dim = model._section_dimension(df).set_index("section")
    assert dim.loc["Reticulation WW Conveyance", "is_field_crew"]
    assert not dim.loc["Billing Management", "is_field_crew"]


def test_section_dimension_rejects_duplicate_section_names():
    df = sections([("D1", "B1", "Same"), ("D2", "B2", "Same")])
    with pytest.raises(ValueError, match="unique"):
        model._section_dimension(df)
