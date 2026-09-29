import pytest

from chess_contracts import braille
from chess_contracts.spec import RANK_TO_BRAILLE, PieceType

# Tabla de la especificación (docs/BRAILLE_SPEC.md).
EXPECTED = {
    1: "\u2802",
    2: "\u2806",
    3: "\u2812",
    4: "\u2832",
    5: "\u2822",
    6: "\u2816",
    7: "\u2836",
    8: "\u2826",
}


@pytest.mark.parametrize("rank,char", EXPECTED.items())
def test_rank_to_braille_matches_spec(rank, char):
    assert braille.rank_to_braille(rank) == char
    assert RANK_TO_BRAILLE[rank] == char


def test_braille_roundtrip():
    for rank, char in EXPECTED.items():
        assert braille.braille_to_rank(char) == rank


@pytest.mark.parametrize("bad", [0, 9, -1])
def test_rank_to_braille_out_of_range(bad):
    with pytest.raises(ValueError):
        braille.rank_to_braille(bad)


def test_square_to_braille_spec_example():
    # docs: Re1 = rey, columna e, fila 1 -> e⠂
    assert braille.square_to_braille("e1") == "e\u2802"


def test_piece_token_spec_example():
    assert braille.piece_token(PieceType.KING, "e1") == "Re\u2802"


def test_piece_token_pawn_without_letter():
    # variante de formato de peones: solo coordenada
    assert braille.piece_token(PieceType.PAWN, "a2", with_piece_letter=False) == "a\u2806"
    assert braille.piece_token(PieceType.PAWN, "a2", with_piece_letter=True) == "Pa\u2806"


def test_all_piece_letters():
    expected = {
        PieceType.KING: "R",
        PieceType.QUEEN: "D",
        PieceType.BISHOP: "A",
        PieceType.KNIGHT: "C",
        PieceType.ROOK: "T",
        PieceType.PAWN: "P",
    }
    for ptype, letter in expected.items():
        assert braille.piece_token(ptype, "a1").startswith(letter)
