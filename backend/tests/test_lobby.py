import pytest
from app.game_manager import GameManager

# --------------------
# Lobby Joining
# --------------------

def test_join_lobby_adds_player():
    gm = GameManager()
    gm.join_lobby("Alice")
    assert "Alice" in gm.lobby_players
    assert gm.state == "lobby"

def test_join_lobby_duplicate_name_fails():
    gm = GameManager()
    gm.join_lobby("Alice")
    with pytest.raises(ValueError):
        gm.join_lobby("Alice")

def test_join_lobby_after_start_fails():
    gm = GameManager()
    gm.join_lobby("Alice")
    gm.start_game()
    with pytest.raises(RuntimeError):
        gm.join_lobby("Bob")

# --------------------
# Start Game
# --------------------

def test_start_game_moves_players_and_deals_board():
    gm = GameManager()
    gm.join_lobby("Alice")
    gm.join_lobby("Bob")
    gm.start_game()

    assert gm.state == "running"
    assert "Alice" in gm.game.players
    assert "Bob" in gm.game.players
    assert len(gm.game.board) == 12  # default initial board

def test_start_game_without_players_fails():
    gm = GameManager()
    with pytest.raises(RuntimeError):
        gm.start_game()
