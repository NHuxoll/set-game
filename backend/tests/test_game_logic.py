import pytest
from app.game_logic import generate_deck, Card, deal_board,is_set, find_any_set, update_board
# --------------------
# Deck Generation
# --------------------

def test_generate_deck_unique():
    deck = generate_deck()
    assert len(deck) == 81
    assert len(set(deck)) == 81  # requires Card to be hashable (dataclass frozen)

def test_generate_deck_expected_card():
    deck = generate_deck()
    expected = Card("red", "diamond", 1, "solid")
    assert expected in deck

def test_generate_deck_feature_coverage():
    deck = generate_deck()
    colors = {c.color for c in deck}
    shapes = {c.shape for c in deck}
    numbers = {c.number for c in deck}
    shadings = {c.shading for c in deck}
    assert colors == {"red", "green", "purple"}
    assert shapes == {"diamond", "squiggle", "oval"}
    assert numbers == {1, 2, 3}
    assert shadings == {"solid", "striped", "open"}

# --------------------
# Deal Board
# --------------------

def test_deal_board_default():
    deck = generate_deck()
    board = deal_board(deck, 12)
    assert len(board) == 12
    assert len(deck) == 81 - 12
    for card in board:
        assert card not in deck

# --------------------
# Set Validation
# --------------------

@pytest.mark.parametrize("cards,expected", [
    # Valid: numbers differ, other features same
    ([Card("red", "oval", 1, "solid"),
      Card("red", "oval", 2, "solid"),
      Card("red", "oval", 3, "solid")], True),

    # Valid: all features different
    ([Card("red", "diamond", 1, "solid"),
      Card("green", "squiggle", 2, "striped"),
      Card("purple", "oval", 3, "open")], True),

    # Invalid: two same, one different in color
    ([Card("red", "oval", 1, "solid"),
      Card("red", "oval", 2, "solid"),
      Card("green", "oval", 3, "solid")], False),

    # Valid: same numbers, shading, shape but different color
    ([Card("red", "oval", 1, "solid"),
      Card("green", "oval", 1, "solid"),
      Card("purple", "oval", 1, "solid")], True),

    # Valid: mixed features
    ([Card("red", "oval", 1, "solid"),
      Card("red", "squiggle", 2, "striped"),
      Card("red", "diamond", 3, "open")], True),
])
def test_is_set(cards, expected):
    assert is_set(cards) == expected

# --------------------
# Find Any Set
# --------------------

def test_find_any_set_found():
    deck = generate_deck()
    board = deal_board(deck, 12)
    result = find_any_set(board)
    if result is not None:
        assert is_set(result)

def test_find_any_set_none():
    # Construct a board with no set (hardcoded example of 12 cards with no set)
    board = [
        Card("red", "diamond", 2, "striped"),
        Card("green", "diamond", 3, "solid"),
        Card("green", "squiggle", 1, "open"),
        Card("purple", "oval", 3, "striped"),
        Card("red", "squiggle", 3, "striped"),
        Card("red", "diamond", 3, "open"),
        Card("purple", "squiggle", 2, "striped"),
        Card("green", "squiggle", 3, "striped"),
        Card("green", "diamond", 2, "solid"),
        Card("purple", "squiggle", 1, "open"),
        Card("purple", "squiggle", 1, "solid"),
        Card("red", "diamond", 1, "striped"),
    ]
    assert find_any_set(board) is None
