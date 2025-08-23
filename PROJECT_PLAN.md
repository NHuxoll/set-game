# Project Plan: Async Turn-Based Multiplayer Set Game (MVP)
## 1. Goals
- Implement a web-based async multiplayer version of Set.
- One global game at first, later extend to multiple groups.

- Light persistence with SQLite.

- Track valid submission times for statistics (fastest, slowest, average).

- Client in plain JavaScript, backend in FastAPI with SQLAlchemy ORM.

## 2. Game Resolution Flow
### Entities

- Player: joins game with name.

- Game: holds deck and board state.

- Round: consists of submissions from players until resolved.

- Submission: player’s valid set + solve time.

### Flow per Round

1. Start Round:
   - Game has current board in DB (games.board_state).
     - extra cards come automatically if no set is available

   - Players see same board (via /board).

    - Each player may press start locally (local timer starts).

2. Player Submission
    - Player presses "Set" button 
   
    - Player selects 3 cards.

    - Client validates set locally.

    - Client sends submission (elapsed_time_ms) to /submit_set.

    - Server re-validates set → if valid, stores submission (times) in DB.

    - If invalid → reject request.

3. Resolution Trigger

    - Triggered when either:

        - All active players submitted, OR

        - Timeout X seconds passes.

4. Resolution

   - Server fetches all submissions for current round.

    - Picks fastest valid submission.

    - Updates board in DB: remove chosen set, draw new cards from deck (or add 3 more if no set available).

    - Updates winner’s score.

    - Stores round results (for stats).

5. Broadcast Result

    - New board returned at /round_result.

    - Clients refresh board state.