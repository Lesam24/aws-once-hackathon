import pytest

from chess_contracts import coordinates as co


def test_square_from_indices_corners():
    assert co.square_from_indices(0, 1) == "a1"
    assert co.square_from_indices(7, 8) == "h8"
    assert co.square_from_indices(4, 1) == "e1"


def test_indices_from_square_roundtrip():
    for sq in co.all_squares():
        fi, rk = co.indices_from_square(sq)
        assert co.square_from_indices(fi, rk) == sq


def test_all_squares_count_and_order():
    squares = co.all_squares()
    assert len(squares) == 64
    # lectura visual: primera casilla a8, última h1
    assert squares[0] == "a8"
    assert squares[-1] == "h1"


@pytest.mark.parametrize("bad", ["", "i1", "a9", "a0", "aa", "11", "e", "e10", 5, None])
def test_is_valid_square_rejects(bad):
    assert co.is_valid_square(bad) is False


@pytest.mark.parametrize("good", ["a1", "h8", "e4", "d5"])
def test_is_valid_square_accepts(good):
    assert co.is_valid_square(good) is True


@pytest.mark.parametrize("bad_index", [-1, 8, 99])
def test_square_from_indices_bad_file(bad_index):
    with pytest.raises(ValueError):
        co.square_from_indices(bad_index, 1)


@pytest.mark.parametrize("bad_rank", [0, 9, -3])
def test_square_from_indices_bad_rank(bad_rank):
    with pytest.raises(ValueError):
        co.square_from_indices(0, bad_rank)


def test_file_and_rank_of():
    assert co.file_of("e4") == "e"
    assert co.rank_of("e4") == 4
