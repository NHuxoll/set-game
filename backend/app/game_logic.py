from dataclasses import dataclass, field
import random
from typing import List, Dict
from itertools import product,  combinations


@dataclass(frozen=True)
class Card:
    color: str
    shape: str
    number: int
    shading: str

@dataclass
class Player:
    name: str
    # times in milliseconds for each round
    times: List[int] = field(default_factory=list)

@dataclass
class Game:
    deck: List[Card] = field(default_factory=list)
    board: List[Card] = field(default_factory=list)
    players: Dict[str, Player] = field(default_factory=dict)
    round_number: int = 1
    submissions: Dict[str, Dict[str, List[Card]|int]] = field(default_factory=dict)

def generate_deck() -> List[Card]:
    """
    Generates a deck of cards.
    :return: Deck of cards as list[Card].
    """
    colors = {"red", "green", "purple"}
    shapes = {"diamond", "squiggle", "oval"}
    numbers = {1, 2, 3}
    shadings = {"solid", "striped", "open"}
    combinations_list = product(colors, shapes, numbers, shadings)
    deck = []
    for color, shape, number, shading in combinations_list:
        deck.append(Card(color, shape, number, shading))
    random.shuffle(deck)
    return deck

def deal_board(deck: List[Card], count: int = 12, seed_int: int = 42) -> List[Card]:
    """
    Deal an initial board with the given deck.
    :param deck: Deck of cards.
    :param count: Number of cards to deal.
    :param seed_int: Seed for random number generator.
    :return: Deal of initial cards.
    """
    random.seed(seed_int)
    board = []
    for _ in range(count):
        board.append(deck.pop(random.randrange(len(deck))))
    return board
def is_set(cards: List[Card]) -> bool:
    """
    Determines if the given list of cards is set.
    :param cards: selected cards to check for a set
    :return bool: True if the given list of cards is set.
    """

    if len(cards) != 3:
        return False

    features = [
        [c.shape for c in cards],
        [c.color for c in cards],
        [c.shading for c in cards],
        [c.number for c in cards],
    ]

    for values in features:
        if len(set(values)) == 2:  # neither all same nor all different
            return False
    return True




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

def update_board(board: List[Card], deck: List[Card], board_size: int = 12) -> List[Card]:
    """
    Updates the given board state.
    :param board: current board state.
    :param deck: deck of cards to update the board state with.
    :param board_size: desired size of the board state.
    :return board: updated board state.
    """
    num_missing = board_size - len(deck)
    if num_missing >= 0:
        return board

    for _ in range(num_missing):
        board.append(deck.pop(random.randrange(len(deck))))
    return board


def submit_set(game: Game, player_name: str, selected_cards: List[Card], elapsed_time_ms: int) -> bool:
    """
    Player submits a set. Returns True if valid, False if invalid.
    """
    # Check that all submitted cards are on the current board
    if not all(card in game.board for card in selected_cards):
        return False

    # Check if it's a valid set
    if not is_set(selected_cards):
        return False

    # Store submission
    game.submissions[player_name] = {
        "cards": selected_cards,
        "time": elapsed_time_ms
    }
    return True