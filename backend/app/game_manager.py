# app/game_manager.py

from game_logic import Game, Card, create_deck, deal_board, resolve_round, Player
import time

class GameManager:
    def __init__(self):
        self.game: Game | None = None
        self.card_lookup: dict[int, Card] = {}

    def new_game(self, player_names: list[str]) -> None:
        deck = create_deck()
        self.card_lookup = {i: card for i, card in enumerate(deck)}

        # shuffle deck in-place
        from random import shuffle
        ids = list(self.card_lookup.keys())
        shuffle(ids)

        # map shuffled IDs back to cards
        shuffled_deck = [self.card_lookup[i] for i in ids]

        board = deal_board(shuffled_deck, 12)
        self.game = Game(
            deck=shuffled_deck,
            board=board,
            players={name: Player.__init__(name) for name in player_names},
            submissions={},
            round_number=1,
            history=[]
        )

    def get_state(self) -> dict:
        """Return JSON-serializable game state (board IDs, players, round)."""
        if not self.game:
            return {}

        board_ids = [self._card_to_id(c) for c in self.game.board]

        return {
            "round": self.game.round_number,
            "board": board_ids,
            "players": {
                name: {"times": pdata["times"]}
                for name, pdata in self.game.players.items()
            },
            "history": self.game.history,
        }

    def submit_set(self, player: str, card_ids: list[int], elapsed_time: float) -> bool:
        """Player submits a set attempt. Returns True if valid, False otherwise."""
        if not self.game:
            return False

        cards = [self.card_lookup[cid] for cid in card_ids]

        # validate and store submission
        from game_logic import is_set
        if is_set(cards):
            self.game.submissions[player] = {"cards": cards, "time": elapsed_time}
            return True
        else:
            return False

    def try_resolve_round(self) -> str | None:
        """Check if round is ready to resolve. If so, resolve and return winner."""
        if not self.game:
            return None

        # all players must have submitted
        if len(self.game.submissions) < len(self.game.players):
            return None

        winner = resolve_round(self.game)

        # store history
        self.game.history.append({
            "round": self.game.round_number,
            "winner": winner,
            "submissions": self.game.submissions.copy(),
        })

        return winner

    def _card_to_id(self, card: Card) -> int:
        """Find ID for a given Card (reverse lookup)."""
        for cid, c in self.card_lookup.items():
            if c == card:
                return cid
        raise ValueError("Card not found in lookup")
