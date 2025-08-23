import pytest

from app.game_logic import Game, Player, submit_set, resolve_round, create_deck, Card, deal_board,is_set, find_any_set


# --------------------
# Deck Generation
# --------------------

def test_generate_deck_unique():
    deck = create_deck()
    assert len(deck) == 81
    assert len(set(deck)) == 81  # requires Card to be hashable (dataclass frozen)

def test_generate_deck_expected_card():
    deck = create_deck()
    expected = Card("red", "diamond", 1, "solid")
    assert expected in deck

def test_generate_deck_feature_coverage():
    deck = create_deck()
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
    deck = create_deck()
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
    deck = create_deck()
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
# --------------------
# Game Flow
# --------------------
def make_simple_game():
    deck = create_deck()
    board = deal_board(deck, 12)
    players = {"alice": Player("alice"), "bob": Player("bob")}
    return Game(deck=deck, board=board, players=players)

def test_submit_invalid_cards():
    game = make_simple_game()
    # pick 3 cards not on the board (pop from deck)
    invalid_cards = [game.deck.pop(), game.deck.pop(), game.deck.pop()]
    assert submit_set(game, "alice", invalid_cards, 5.0) is False
    assert "alice" not in game.submissions

def test_submit_non_set():
    game = make_simple_game()
    # take 3 cards from board that don’t form a set
    cards = game.board[:3]
    assert not is_set(cards)
    assert submit_set(game, "alice", cards, 4.0) is False
    assert "alice" not in game.submissions

def test_resolve_round_winner_updates_board():
    game = make_simple_game()
    # ensure valid set on board
    valid_set = find_any_set(game.board)
    assert valid_set is not None
    submit_set(game, "alice", valid_set, 3.0)
    submit_set(game, "bob", valid_set, 5.0)

    winner = resolve_round(game)
    assert winner == "alice"
    assert game.round_number == 2
    # winner’s time recorded
    assert 3.0 in game.players["alice"].times


def test_resolve_round_no_submissions():
    game = make_simple_game()
    old_board = list(game.board)
    winner = resolve_round(game)
    assert winner is None
    assert game.board == old_board

def test_deck_depletion():
    # Make a small deck
    game = Game(deck=[], board=[], players={"alice": Player("alice")})
    # Fill with board and tiny deck
    game.board = [
        Card("red", "oval", 1, "solid"),
        Card("green", "diamond", 2, "open"),
        Card("purple", "squiggle", 3, "striped"),
    ]
    game.deck = [Card("red", "oval", 2, "solid")]  # only 1 card left

    submit_set(game, "alice", game.board[:3], 1.0)
    winner = resolve_round(game)

    assert winner == "alice"
    assert len(game.board) == 1 + 0  # old board cleared, + 1 card left in deck
    assert game.deck == []
