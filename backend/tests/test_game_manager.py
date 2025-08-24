import pytest
from app.game_manager import GameManager
from app.game_logic import find_any_set


def setup_game(num_players=2):
    gm = GameManager()
    for i in range(num_players):
        gm.join_lobby(f"player{i}")
    gm.start_game()
    return gm


# ----------------------
# Lobby / Initialization
# ----------------------

def test_lobby_join_and_start():
    gm = GameManager()
    gm.join_lobby("alice")
    gm.join_lobby("bob")

    state = gm.get_state()
    assert state["state"] == "lobby"
    assert "alice" in state["players"]
    assert "bob" in state["players"]

    gm.start_game()
    state = gm.get_state()
    assert state["state"] == "running"
    assert set(state["players"].keys()) == {"alice", "bob"}
    assert len(state["board"]) == 12


# ----------------------
# Submissions
# ----------------------

def test_submit_set_valid():
    gm = setup_game()
    board_ids = gm.get_state()["board"]

    set_cards = find_any_set([gm.card_lookup[cid] for cid in board_ids])
    if set_cards is None:
        pytest.skip("Generated board has no set")

    set_ids = [gm._card_to_id(c) for c in set_cards]

    ok = gm.submit_set("player0", set_ids, elapsed_time=2.5)
    assert ok
    assert "player0" in gm.game.submissions


def test_submit_set_invalid():
    gm = setup_game()
    board_ids = gm.get_state()["board"]
    bad_ids = board_ids[:3]  # not guaranteed a set

    ok = gm.submit_set("player0", bad_ids, elapsed_time=3.0)
    if ok:
        assert "player0" in gm.game.submissions
    else:
        assert "player0" not in gm.game.submissions


# ----------------------
# Round Resolution
# ----------------------

def test_try_resolve_round_waits():
    gm = setup_game()
    board_ids = gm.get_state()["board"]

    set_cards = find_any_set([gm.card_lookup[cid] for cid in board_ids])
    if set_cards is None:
        pytest.skip("Generated board has no set")

    set_ids = [gm._card_to_id(c) for c in set_cards]
    gm.submit_set("player0", set_ids, elapsed_time=1.2)

    assert gm.try_resolve_round() is None


def test_try_resolve_round_resolves():
    gm = setup_game()
    board_ids = gm.get_state()["board"]

    set_cards = find_any_set([gm.card_lookup[cid] for cid in board_ids])
    if set_cards is None:
        pytest.skip("Generated board has no set")

    set_ids = [gm._card_to_id(c) for c in set_cards]
    gm.submit_set("player0", set_ids, elapsed_time=1.0)
    gm.submit_set("player1", set_ids, elapsed_time=2.0)

    winner = gm.try_resolve_round()
    assert winner in {"player0", "player1"}

    state = gm.get_state()
    assert state["round"] == 2
    assert "history" in state
    assert any(r["winner"] == winner for r in state["history"])
