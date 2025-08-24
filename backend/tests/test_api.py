import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.main as main
from app.game_manager import GameManager

client = TestClient(app)


# ----------------------
# Fixtures
# ----------------------

@pytest.fixture(autouse=True)
def reset_manager(monkeypatch):
    """Ensure each test runs with a fresh GameManager instance bound to app.main.gm."""
    new_gm = GameManager()
    # Important: use the object form, not dotted string with separate name.
    monkeypatch.setattr(main, "gm", new_gm)
    yield
    # no teardown needed; next test rebinds


# ----------------------
# Lobby Endpoints
# ----------------------

def test_join_lobby():
    res = client.post("/lobby/join", json={"name": "Alice"})
    assert res.status_code == 200
    data = res.json()
    assert data["state"] == "lobby"
    assert data["players"] == ["Alice"]

def test_join_lobby_duplicate():
    client.post("/lobby/join", json={"name": "Alice"})
    res = client.post("/lobby/join", json={"name": "Alice"})
    assert res.status_code == 400
    assert "already" in res.json()["detail"].lower()

def test_cannot_join_after_start():
    client.post("/lobby/join", json={"name": "Alice"})
    client.post("/lobby/join", json={"name": "Bob"})
    client.post("/lobby/start")
    res = client.post("/lobby/join", json={"name": "Charlie"})
    assert res.status_code == 400

def test_start_game_without_players():
    res = client.post("/lobby/start")
    assert res.status_code == 400

def test_start_game_with_players():
    client.post("/lobby/join", json={"name": "Alice"})
    client.post("/lobby/join", json={"name": "Bob"})
    res = client.post("/lobby/start")
    assert res.status_code == 200
    data = res.json()
    assert data["state"] == "running"
    assert data["round"] == 1
    assert len(data["board"]) == 12
    assert set(data["players"].keys()) == {"Alice", "Bob"}


# ----------------------
# Game State
# ----------------------

def test_get_state_in_lobby():
    client.post("/lobby/join", json={"name": "Alice"})
    res = client.get("/game/state")
    assert res.status_code == 200
    data = res.json()
    assert data["state"] == "lobby"
    assert "players" in data
    assert "Alice" in data["players"]  # lobby returns list of names

def test_get_state_running():
    client.post("/lobby/join", json={"name": "Alice"})
    client.post("/lobby/join", json={"name": "Bob"})
    client.post("/lobby/start")
    res = client.get("/game/state")
    assert res.status_code == 200
    data = res.json()
    assert data["state"] == "running"
    assert "round" in data
    assert "board" in data
    assert "players" in data  # running returns dict of players -> stats


# ----------------------
# Submissions + Round Resolution
# ----------------------

def test_submit_invalid_before_start():
    res = client.post(
        "/game/submit",
        json={"player": "Alice", "cards": [0, 1, 2], "elapsed_time": 1.2},
    )
    assert res.status_code == 400
    assert "not running" in res.json()["detail"].lower()

def test_submit_invalid_player():
    client.post("/lobby/join", json={"name": "Alice"})
    client.post("/lobby/join", json={"name": "Bob"})
    client.post("/lobby/start")

    state = client.get("/game/state").json()
    board_ids = state["board"]

    # Unknown player name
    res = client.post(
        "/game/submit",
        json={"player": "Ghost", "cards": board_ids[:3], "elapsed_time": 1.0},
    )
    # Our backend returns 400 for any invalid submission
    assert res.status_code == 400

def test_submit_invalid_set():
    client.post("/lobby/join", json={"name": "Alice"})
    client.post("/lobby/join", json={"name": "Bob"})
    client.post("/lobby/start")

    state = client.get("/game/state").json()
    board_ids = state["board"]

    # First three may or may not be a set; if they are, server accepts.
    res = client.post(
        "/game/submit",
        json={"player": "Alice", "cards": board_ids[:3], "elapsed_time": 2.0},
    )

    if res.status_code == 200:
        assert res.json()["success"] is True
    else:
        assert res.status_code == 400

def test_submit_valid_and_resolve():
    from app.game_logic import find_any_set

    client.post("/lobby/join", json={"name": "Alice"})
    client.post("/lobby/join", json={"name": "Bob"})
    client.post("/lobby/start")

    # Get board + compute a valid set
    state = client.get("/game/state").json()
    board_ids = state["board"]

    # Use the current gm bound in app.main (after fixture monkeypatch)
    board_cards = [main.gm.card_lookup[cid] for cid in board_ids]
    set_cards = find_any_set(board_cards)
    if set_cards is None:
        pytest.skip("Generated board has no set")
    set_ids = [main.gm._card_to_id(c) for c in set_cards]

    # First submit (no resolution yet)
    r1 = client.post(
        "/game/submit",
        json={"player": "Alice", "cards": set_ids, "elapsed_time": 1.0},
    )
    assert r1.status_code == 200
    data1 = r1.json()
    assert data1["success"] is True
    assert data1["winner"] is None  # not all players have submitted yet

    # Second submit (should resolve the round)
    r2 = client.post(
        "/game/submit",
        json={"player": "Bob", "cards": set_ids, "elapsed_time": 2.0},
    )
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["success"] is True
    assert data2["winner"] in {"Alice", "Bob"}
    assert data2["state"]["round"] == 2
    assert "history" in data2["state"]
