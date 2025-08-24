from typing import Dict, List, Optional
from app.game_logic import Card, create_deck, deal_board, is_set, resolve_round, Game, Player


class GameManager:
    def __init__(self):
        self.card_lookup_inv: Dict[Card, int] | None = None
        self.card_lookup: Dict[int, Card] = {}
        self.game: Optional[Game] = None

        # Lobby / lifecycle
        self.state: str = "lobby"  # lobby | running | finished
        self.lobby_players: List[str] = []

    # ----------------------
    # Helpers
    # ----------------------

    def _card_to_id(self, card: Card) -> int:
        """Maps a card to a stable ID (0–80)."""
        return self.card_lookup_inv[card]

    def _id_to_card(self, cid: int) -> Card:
        return self.card_lookup[cid]

    # ----------------------
    # Lobby
    # ----------------------

    def join_lobby(self, player_name: str) -> None:
        if self.state != "lobby":
            raise RuntimeError("Cannot join, game already started")

        if player_name in self.lobby_players:
            raise ValueError("Player name already taken")

        self.lobby_players.append(player_name)

    def start_game(self) -> None:
        if self.state != "lobby":
            raise RuntimeError("Game already started or finished")

        if not self.lobby_players:
            raise RuntimeError("Cannot start without players")

        deck = create_deck()
        self.card_lookup = {i: card for i, card in enumerate(deck)}
        self.card_lookup_inv = {card: i for i, card in enumerate(deck)}

        board = deal_board(deck, 12)

        players = {name: Player(name=name) for name in self.lobby_players}
        self.game = Game(deck=deck, board=board, players=players)

        self.state = "running"
        self.lobby_players.clear()

    # ----------------------
    # State Snapshot
    # ----------------------

    def get_state(self) -> Dict:
        """Return a serializable snapshot of the game state."""
        if not self.game:
            return {"state": self.state, "players": self.lobby_players}

        return {
            "state": self.state,
            "round": self.game.round_number,
            "board": [self._card_to_id(c) for c in self.game.board],
            "players": {
                name: {"times": p.times} for name, p in self.game.players.items()
            },
            "history": getattr(self.game, "history", []),
        }

    # ----------------------
    # Submissions
    # ----------------------

    def submit_set(self, player: str, card_ids: List[int], elapsed_time: float) -> bool:
        if not self.game or self.state != "running":
            return False
        if player not in self.game.players:
            return False

        cards = [self._id_to_card(cid) for cid in card_ids]
        if not is_set(cards):
            return False

        self.game.submissions[player] = {"cards": cards, "time": elapsed_time}
        return True

    # ----------------------
    # Round Resolution
    # ----------------------

    def try_resolve_round(self) -> Optional[str]:
        """Only resolves if all players have submitted."""
        if not self.game or self.state != "running":
            return None

        if len(self.game.submissions) < len(self.game.players):
            return None

        winner = resolve_round(self.game)

        # Keep a round history
        if not hasattr(self.game, "history"):
            self.game.history = []
        self.game.history.append(
            {
                "round": self.game.round_number - 1,
                "winner": winner,
                "submissions": {
                    p: d["time"] for p, d in self.game.submissions.items()
                },
            }
        )

        return winner
