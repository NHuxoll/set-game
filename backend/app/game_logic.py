from dataclasses import dataclass, field
from typing import List, Dict
from itertools import product, combinations
from random import shuffle


@dataclass(frozen=True)
class Card:
    color: str
    shape: str
    number: int
    shading: str


@dataclass
class Player:
    name: str
    times: List[int] = field(default_factory=list)


@dataclass
class Game:
    deck: List[Card] = field(default_factory=list)
    board: List[Card] = field(default_factory=list)
    players: Dict[str, Player] = field(default_factory=dict)
    round_number: int = 1
    submissions: Dict[str, Dict] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    # submissions[player_name] = {"cards": List[Card], "time": int}


def create_deck() -> List[Card]:
    """
    Create a deck of cards.
    :return List[Card]: Deck of cards.
    """
    colors = ["red", "green", "purple"]
    shapes = ["diamond", "oval", "squiggle"]
    numbers = [1, 2, 3]
    shadings = ["solid", "striped", "open"]

    deck = [Card(c, s, n, sh) for c, s, n, sh in product(colors, shapes, numbers, shadings)]
    shuffle(deck)
    return deck


def deal_board(deck: List[Card], count: int = 12) -> List[Card]:
    """
    creates the first board of a game
    :param deck: the deck of cards to play with
    :param count: optional parameter that sets the amount of cards to play
    :return: the first board of the game as list of cards
    """
    board = deck[:count]
    del deck[:count]
    if find_any_set(board) is None:
        board.extend(deck[:3])
        del deck[:3]
    return board


def is_set(cards: List[Card]) -> bool:
    """
    checks if the cards are a set
    :param cards: cards to check
    :return: True if the cards are a set
    """
    if len(cards) != 3:
        return False

    def all_same_or_all_different(attrs: List) -> bool:
        """
        helper function to check if all cards have the same value
        :param attrs: attributes for checking if all cards have the same value or all cards have different values
        :return: True if all cards have the same value or all cards have different values False otherwise
        """
        return len(set(attrs)) in (1, 3)

    return all(
        all_same_or_all_different([getattr(card, attr) for card in cards])
        for attr in ["color", "shape", "number", "shading"]
    )
def find_any_set(board: List[Card]) -> List[Card] | None:
    """
    Returns the first set of cards found in the given board.
    :param board: current board state.
    :return List[Card] | None: first set of cards found or None.
    """
    for cards in combinations(board, 3):
        if is_set(list(cards)):
            return list(cards)
    return None


def submit_set(game: Game, player_name: str, selected_cards: List[Card], elapsed_time_ms: int) -> bool:
    """
    Submits a set of cards selected by the given game to the given player.
    :param game: current game state.
    :param player_name: name of the player that submitted the set.
    :param selected_cards: selected cards that are a set.
    :param elapsed_time_ms: time taken to find the set
    :return:
    """
    if not all(card in game.board for card in selected_cards):
        return False

    if not is_set(selected_cards):
        return False

    game.submissions[player_name] = {
        "cards": selected_cards,
        "time": elapsed_time_ms
    }
    return True


def resolve_round(game: Game) -> str | None:
    """
    Resolve the round after all players have either submitted a set or timed out.
    Removes the winning cards from the board, replaces them with new ones from the deck,
    updates player times, and increments the round.
    Returns the winner's name or None if no submissions.
    :param game: current game state.
    :return str | None: winner's name or None if no submissions.
    """
    if not game.submissions:
        return None

    # Determine fastest submission
    winner = min(game.submissions, key=lambda p: game.submissions[p]["time"])
    winning_data = game.submissions[winner]
    winning_cards = winning_data["cards"]

    # Safely remove winning cards from the board
    game.board = [c for c in game.board if c not in winning_cards]

    # Replenish board
    if len(game.deck) >= 3:
        game.board.extend(game.deck[:3])
        del game.deck[:3]
        if find_any_set(game.board) is None:
            game.board.extend(game.deck[:3])
            del game.deck[:3]
    else:
        game.board.extend(game.deck)
        game.deck.clear()

    # Track winner time
    game.players[winner].times.append(winning_data["time"])

    # Clear submissions and increment round
    game.submissions.clear()
    game.round_number += 1

    return winner
